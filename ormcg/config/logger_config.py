# -*- coding: utf-8 -*-

"""
@author: takeEasy9
@description: logger configuration
@version: 1.0.0
@since: 2024/4/30 20:08
"""
import logging
import sys
from logging import handlers

from ormcg.utils.constant_util import ConstantUtil


class LoggerConfiguration:
    def __init__(self):
        # logger
        root_logger = logging.getLogger('root')
        console_logger = logging.getLogger('console')
        file_logger = logging.getLogger('file')
        # handler
        stream_handler = logging.StreamHandler(sys.stdout)
        file_handler = handlers.RotatingFileHandler(filename=ConstantUtil.LOG_FILE_NAME,
                                                    maxBytes=ConstantUtil.LOG_FILE_MAX_SIZE,
                                                    backupCount=ConstantUtil.LOG_FILE_BACKUP_COUNT,
                                                    mode='a',
                                                    encoding=ConstantUtil.DEFAULT_CHARSET)
        # set log level,default to debug
        root_logger.setLevel(logging.DEBUG)
        console_logger.setLevel(logging.DEBUG)
        file_logger.setLevel(logging.DEBUG)
        stream_handler.setLevel(logging.DEBUG)
        file_handler.setLevel(logging.DEBUG)
        # set logger formatter
        formatter = logging.Formatter(ConstantUtil.LOG_FORMATTER, ConstantUtil.LOG_DATE_TIME_FORMATTER)
        stream_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        # set handler for logger
        root_logger.addHandler(stream_handler)
        root_logger.addHandler(file_handler)
        console_logger.addHandler(stream_handler)
        file_logger.addHandler(file_handler)

        # close log file
        file_handler.close()

        self.__loggers = {'root': root_logger, 'console': console_logger, 'file': file_logger}

    def get_logger(self, name='root'):
        assert (name in self.__loggers.keys())
        return self.__loggers[name]


logger = LoggerConfiguration().get_logger()
