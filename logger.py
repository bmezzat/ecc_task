import logging


def setup_logger(name, level="INFO") -> logging.Logger:
    formatter = logging.Formatter(
        "%(asctime)s : %(levelname)s : %(name)s :  %(message)s"
    )

    stream_handler = logging.StreamHandler()  #output logs to console
    stream_handler.setFormatter(formatter)

    file_handler = logging.FileHandler("app.log", mode="a")  # output logs app.log
    file_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    logger.propagate = False

    return logger
