from __future__ import annotations

import logging
import logging.handlers
import os
import queue
import sys
import typing

from ._logger_adapter import _LoggerAdapter
from ._logger_filter_level_max import _LoggerFilterLevelMax
from ._logger_formatter import _LoggerFormatter
from ._logger_interceptor import _LoggerInterceptor
from .logger_depot_parameters import LoggerDepotParameters
from .logger_intercept_parameters import LoggerInterceptParameters


class LoggerDepot:
    _global_instance_default: LoggerDepot | None = None
    _global_instance_dict: dict[str, LoggerDepot] = {}

    @staticmethod
    def get_depot(depot_key: str | None = None) -> LoggerDepot:
        return LoggerDepot(depot_key)

    @staticmethod
    def drop_depot(depot_key: str | None = None) -> None:
        if LoggerDepot.get_depot(depot_key).parameters is not None:
            raise RuntimeError('must stop')

        if depot_key is None:
            LoggerDepot._global_instance_default = None
            return

        del LoggerDepot._global_instance_dict[depot_key]

    @staticmethod
    def nest_obj_logger(obj: typing.Any, depot_key: str | None = None) -> _LoggerAdapter:
        return LoggerDepot(depot_key).root_logger.nest_obj_logger(obj)

    def __new__(cls, depot_key: str | None = None):
        if depot_key is None:
            if LoggerDepot._global_instance_default is None:
                LoggerDepot._global_instance_default = super().__new__(cls)

            return LoggerDepot._global_instance_default

        if depot_key not in LoggerDepot._global_instance_dict:
            LoggerDepot._global_instance_dict[depot_key] = super().__new__(cls)

        return LoggerDepot._global_instance_dict[depot_key]

    def __init__(self, depot_key: str | None = None):
        if hasattr(self, 'depot_key'):
            return

        self.depot_key = depot_key

        self._parameters: LoggerDepotParameters | None = None
        self._logger = logging.getLogger()
        self._logger_interceptor: _LoggerInterceptor | None = None
        self._formatter: _LoggerFormatter | None = None

        self._main_queue: queue.SimpleQueue | None = None
        self._main_queue_handler: logging.Handler | None = None
        self._main_queue_listener: logging.handlers.QueueListener | None = None

        self._main_logger_file_handler: logging.Handler | None = None
        self._main_logger_stdout_handler: logging.Handler | None = None
        self._main_logger_stderr_handler: logging.Handler | None = None

    @property
    def parameters(self) -> LoggerDepotParameters | None:
        return self._parameters

    @property
    def root_logger(self) -> _LoggerAdapter:
        return _LoggerAdapter(self._logger)

    def start(self, parameters: LoggerDepotParameters) -> LoggerDepot:
        if self._parameters is not None:
            raise RuntimeError('unable to start twice')

        self._parameters = parameters

        self._logger = logging.getLogger(self._parameters.log_root)
        self._logger.setLevel(self._parameters.level)

        self._formatter = _LoggerFormatter()

        self._main_queue = queue.SimpleQueue()

        self._main_queue_handler = logging.handlers.QueueHandler(self._main_queue)
        self._logger.addHandler(self._main_queue_handler)

        self._logger_interceptor = _LoggerInterceptor(
            parameters_list=self._parameters.logger_intercept_list,
            queue=self._main_queue,
        ).start()

        main_queue_logger_handler_list: list[logging.Handler] = []

        if self._parameters.log_file_path is not None:
            os.makedirs(
                name=os.path.dirname(self._parameters.log_file_path),
                exist_ok=True,
            )

            self._main_logger_file_handler = logging.FileHandler(
                self._parameters.log_file_path,
                mode='a',
                encoding='utf-8',
            )

            main_queue_logger_handler_list.append(self._main_logger_file_handler)

            self._main_logger_file_handler.setFormatter(self._formatter)

            if self._parameters.log_file_level is not None:
                self._main_logger_file_handler.setLevel(self._parameters.log_file_level)
            else:
                self._main_logger_file_handler.setLevel(self._parameters.level)

        if self._parameters.stdout_f:
            self._main_logger_stdout_handler = logging.StreamHandler(stream=sys.stdout)
            main_queue_logger_handler_list.append(self._main_logger_stdout_handler)

            self._main_logger_stdout_handler.setFormatter(self._formatter)

            if self._parameters.stdout_level is not None:
                self._main_logger_stdout_handler.setLevel(self._parameters.stdout_level)
            else:
                self._main_logger_stdout_handler.setLevel(self._parameters.level)

            if self._parameters.split_streams_f and self._parameters.stderr_f:
                stderr_level_max = self._parameters.stderr_level
                if stderr_level_max is None:
                    stderr_level_max = 'ERROR'

                self._main_logger_stdout_handler.addFilter(_LoggerFilterLevelMax(stderr_level_max))

        if self._parameters.stderr_f:
            self._main_logger_stderr_handler = logging.StreamHandler(stream=sys.stderr)
            main_queue_logger_handler_list.append(self._main_logger_stderr_handler)

            self._main_logger_stderr_handler.setFormatter(self._formatter)

            if self._parameters.stderr_level is not None:
                self._main_logger_stderr_handler.setLevel(self._parameters.stderr_level)
            else:
                self._main_logger_stderr_handler.setLevel('ERROR')

        self._main_queue_listener = logging.handlers.QueueListener(
            self._main_queue,
            *main_queue_logger_handler_list,
            respect_handler_level=True,
        )

        self._main_queue_listener.start()

        self.root_logger.nest_obj_logger(self).info('logger start')

        return self

    def stop(self) -> LoggerDepot:
        if self._parameters is None:
            return self

        assert self._logger_interceptor is not None
        assert self._main_queue_handler is not None
        assert self._main_queue_listener is not None

        self.root_logger.nest_obj_logger(self).info('logger stop')

        self._logger_interceptor.stop()
        self._logger_interceptor = None

        self._logger.setLevel(logging.NOTSET)
        self._logger.removeHandler(self._main_queue_handler)

        self._main_queue_handler.flush()
        self._logger.removeHandler(self._main_queue_handler)
        self._main_queue_handler.close()
        self._main_queue_handler = None

        self._main_queue_listener.enqueue_sentinel()
        self._main_queue_listener.stop()
        self._main_queue_listener = None

        self._main_queue = None

        if self._main_logger_file_handler is not None:
            self._main_logger_file_handler.flush()
            self._main_logger_file_handler.close()
            self._main_logger_file_handler = None

        if self._main_logger_stdout_handler is not None:
            self._main_logger_stdout_handler.flush()
            self._main_logger_stdout_handler.close()
            self._main_logger_stdout_handler = None

        if self._main_logger_stderr_handler is not None:
            self._main_logger_stderr_handler.flush()
            self._main_logger_stderr_handler.close()
            self._main_logger_stderr_handler = None

        self._logger = logging.getLogger()
        self._parameters = None

        return self

    def start_streams(
        self,
        level: str = 'DEBUG',
        log_root: str | None = None,
        stdout_f: bool = True,
        stdout_level: str = 'DEBUG',
        stderr_f: bool = True,
        stderr_level: str = 'ERROR',
        split_streams_f: bool = True,
        logger_intercept_list: tuple[LoggerInterceptParameters, ...] | None = None,
    ) -> LoggerDepot:
        return self.start(
            parameters=LoggerDepotParameters(
                level=level,
                log_root=log_root,
                log_file_path=None,
                log_file_level=None,
                stdout_f=stdout_f,
                stdout_level=stdout_level,
                stderr_f=stderr_f,
                stderr_level=stderr_level,
                split_streams_f=split_streams_f,
                logger_intercept_list=logger_intercept_list,
            )
        )
