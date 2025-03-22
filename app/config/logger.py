import logging

from .settings import IS_DEVELOPMENT, LOG_LEVEL


def init_logger():
    logger = logging.getLogger()
    logger.setLevel(LOG_LEVEL)

    console_handler = logging.StreamHandler()

    plain_formatter = logging.Formatter(fmt='%(asctime)s - [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    if IS_DEVELOPMENT:
        import colorlog

        color_formatter = colorlog.ColoredFormatter(
            fmt='%(asctime)s - %(log_color)s[%(levelname)s]%(reset)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            },
        )
        console_handler.setFormatter(color_formatter)
    else:
        console_handler.setFormatter(plain_formatter)

    logger.handlers = []
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler('app.log')
    file_handler.setFormatter(plain_formatter)
    logger.addHandler(file_handler)
