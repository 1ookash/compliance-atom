from dataclasses import dataclass

from .logger_intercept_parameters import LoggerInterceptParameters


@dataclass(frozen=True, kw_only=True)
class LoggerDepotParameters:
    level: str = 'DEBUG'
    log_root: str | None = 'root'

    log_file_path: str | None = None
    log_file_level: str | None = None

    stdout_f: bool = True
    stdout_level: str | None = None

    stderr_f: bool = True
    stderr_level: str | None = None

    split_streams_f: bool = True

    logger_intercept_list: tuple[LoggerInterceptParameters, ...] | None = None
