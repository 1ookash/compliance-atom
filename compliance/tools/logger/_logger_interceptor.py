from __future__ import annotations

import logging
import logging.handlers
import queue

from ._logger_intercept_context import _LoggerInterceptContext
from .logger_intercept_parameters import LoggerInterceptParameters


class _LoggerInterceptor:
    def __init__(
        self,
        parameters_list: tuple[LoggerInterceptParameters, ...] | None,
        queue: queue.SimpleQueue,
    ):
        self.parameters_list = parameters_list
        self.queue = queue

        self._start = False
        self._logger_intercept_context_list: list[_LoggerInterceptContext] = []

    def start(self) -> _LoggerInterceptor:
        if self.parameters_list is None:
            return self

        if self._start:
            raise RuntimeError('unable to start twice')

        self._start = True

        for parameters in self.parameters_list:
            logger = logging.getLogger(parameters.logger_path)

            level_init = logging.getLevelName(logger.level)
            propogate_f_init = logger.propagate

            if parameters.overwrite_level is not None:
                logger.setLevel(parameters.overwrite_level)

            if parameters.propogate_break_f:
                logger.propagate = False

            handler = logging.handlers.QueueHandler(self.queue)
            logger.addHandler(handler)

            self._logger_intercept_context_list.append(
                _LoggerInterceptContext(
                    parameters=parameters,
                    level_init=level_init,
                    propogate_f_init=propogate_f_init,
                    handler=handler,
                )
            )

        return self

    def stop(self) -> _LoggerInterceptor:
        if self.parameters_list is None or not self._start:
            return self

        self._start = False

        for context in self._logger_intercept_context_list:
            parameters = context.parameters

            logger = logging.getLogger(parameters.logger_path)

            if parameters.overwrite_level is not None:
                logger.setLevel(context.level_init)

            if parameters.propogate_break_f:
                logger.propagate = context.propogate_f_init

            logger.removeHandler(context.handler)

        self._logger_intercept_context_list = []

        return self
