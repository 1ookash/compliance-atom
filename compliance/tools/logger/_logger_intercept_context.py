import logging
from dataclasses import dataclass

from .logger_intercept_parameters import LoggerInterceptParameters


@dataclass
class _LoggerInterceptContext:
    parameters: LoggerInterceptParameters
    level_init: str
    propogate_f_init: bool
    handler: logging.Handler
