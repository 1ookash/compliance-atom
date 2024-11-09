import typing

from .logger_depot_parameters import LoggerDepotParameters
from .logger_intercept_parameters import LoggerInterceptParameters
from .logger_depot import LoggerDepot

from ._logger_adapter import _LoggerAdapter as LoggerType


def get_depot(depot_key: str | None = None) -> LoggerDepot:
    return LoggerDepot.get_depot(depot_key)


def drop_depot(depot_key: str | None = None) -> None:
    return LoggerDepot.drop_depot(depot_key)


def start(parameters: LoggerDepotParameters, depot_key: str | None = None) -> LoggerDepot:
    return LoggerDepot.get_depot(depot_key).start(parameters)


def stop(depot_key: str | None = None) -> LoggerDepot:
    return LoggerDepot.get_depot(depot_key).stop()


def start_streams(
    level: str = 'DEBUG',
    log_root: str | None = None,
    stdout_f: bool = True,
    stdout_level: str = 'DEBUG',
    stderr_f: bool = True,
    stderr_level: str = 'ERROR',
    split_streams_f: bool = True,
    depot_key: str | None = None,
    logger_intercept_list: tuple[LoggerInterceptParameters] | None = None,
) -> LoggerDepot:
    return LoggerDepot.get_depot(depot_key).start_streams(
        level=level,
        log_root=log_root,
        stdout_f=stdout_f,
        stdout_level=stdout_level,
        stderr_f=stderr_f,
        stderr_level=stderr_level,
        split_streams_f=split_streams_f,
        logger_intercept_list=logger_intercept_list,
    )


def nest_obj_logger(obj: typing.Any, depot_key: str | None = None):
    return LoggerDepot.nest_obj_logger(
        obj=obj,
        depot_key=depot_key,
    )


# TODO перенаправление ворнингов
# TODO мультипроцессинг
