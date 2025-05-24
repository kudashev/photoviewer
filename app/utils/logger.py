import logging


def get_logger(logger_name) -> logging.Logger:
    return logging.getLogger(logger_name)


def setup_logger(logger, rank: int = 0, logging_level: str = 'INFO'):
    for handler in logger.handlers:
        logger.removeHandler(handler)
    logger.setLevel(getattr(logging, logging_level.upper()))
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        fmt=f"%(asctime)s %(levelname)s {rank:02d}: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"))
    logger.addHandler(console_handler)
