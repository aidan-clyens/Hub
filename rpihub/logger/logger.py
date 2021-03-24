import logging
import os


log_path = "logs"


def create_log_dir():
    if not os.path.exists(log_path):
        os.makedirs(log_path)


def get_logger(name, log_level):
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Stream Handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # File Handler
    create_log_dir()
    file_handler = logging.FileHandler(os.path.join(log_path, "log.log"))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
