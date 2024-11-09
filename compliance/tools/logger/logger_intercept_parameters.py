from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class LoggerInterceptParameters:
    logger_path: str | None = None
    overwrite_level: str | None = None
    propogate_break_f: bool = False
