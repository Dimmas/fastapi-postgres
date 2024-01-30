import logging


def get_logger(logger_name: str):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.WARNING)
    formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger
