import logging


def get_logger(name, log_level):
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Stream Handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # File Handler
    file_handler = logging.FileHandler("log.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
