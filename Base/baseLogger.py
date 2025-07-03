"""
# file:     Base/baseLogger.py
# 日志基类封装
# 实现双通道输出，console_output、file_save。 支持多实例复用
"""

import logging
import time
import os
from Base.basePath import BasePath as BP
from Base.utils import read_config_ini

config = read_config_ini(BP.CONFIG_FILE)['日志打印配置']
rq = time.strftime('%Y%m%d_%H_%M', time.localtime()) + '.log'

class Logger(object):
    def __init__(self, name):
        self.name = name
        # 创建log记录器
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(config['level'])

        # set output log formatter
        self.formatter = logging.Formatter(config['formatter'])

        # create stream handler
        self.streamHandler = logging.StreamHandler()
        self.streamHandler.setFormatter(self.formatter)
        self.streamHandler.setLevel(config['stream_handler_level'])

        # create file handler
        self.fileHandler = logging.FileHandler(os.path.join(BP.LOG_DIR, rq), 'a', encoding='utf-8')
        self.fileHandler.setFormatter(self.formatter)
        self.fileHandler.setLevel(config['file_handler_level'])

        # 将handler添加到logger中
        self.logger.addHandler(self.streamHandler)
        self.logger.addHandler(self.fileHandler)


    def getLogger(self):
        """ 返回日志记录器对象 """
        return self.logger


if __name__ == '__main__':
    logger = Logger('Base/baseLogger.py').getLogger()
    logger.info('这是info级别的信息')