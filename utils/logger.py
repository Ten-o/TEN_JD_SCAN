import logging
import colorlog
from logging.handlers import RotatingFileHandler

MESSAGE = "message"


def setup_logger(log_file='sacn.log'):
    # 创建一个 logger
    logger = logging.getLogger(log_file)
    logger.setLevel(logging.DEBUG)

    # 创建格式化器

    log_format = ("%(log_color)s| %(asctime)s |  %(levelname)-8s%(reset)s%(log_color)s| %(message)s%(reset)s")
    formatter = colorlog.ColoredFormatter(
        log_format,
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'green',
            'INFO': 'cyan',
            'WARNING': 'white',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    #
    # # 创建文件处理器，支持按大小切割日志文件
    # file_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=2,  encoding='utf-8')
    # file_handler.setFormatter(formatter)

    # 创建控制台处理器，显示在终端
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # 添加处理器到 logger
    # logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


if __name__ == '__main__':
    log = setup_logger()
    log.debug('debug message')
    log.info('info message')
    log.warning('warning message')
    log.error('error message')
    log.critical('critical message')
