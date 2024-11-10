import logging


class _LoggerFilterLevelMax(logging.Filter):
    def __init__(self, level_max: str):
        super().__init__()
        self.level_max = level_max

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno < logging.getLevelName(self.level_max)
