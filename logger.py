import logging

loggers = {}


def setup_logger(name, log_level=logging.DEBUG, log_file=None):

    global loggers

    if loggers.get(name):
        return loggers.get(name)

    else:
        logger = logging.getLogger(name)
        logger.setLevel(log_level)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)

        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "name": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}'
        )
        console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        loggers[name] = logger
        return logger
