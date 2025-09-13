"""
# file:     Base/baseLogger.py
# 日志基类封装
# 实现双通道输出，console_output、file_save。 支持多实例复用
"""

import sys
from pathlib import Path
# 获取当前文件的父目录的父目录（项目根目录）
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))


from datetime import datetime
import os
from Base.basePath import BasePath as BP
from Base.utils import read_config_ini
from loguru import logger

# 获取配置
config = read_config_ini(BP.CONFIG_FILE)['日志打印配置']

class Logger:
    _initialized = False
    
    def __init__(self, name=None):
        """
        初始化日志记录器
        name: 日志记录器名称，通常为模块名
        """
        self.name = name or __name__   
        
        # 确保只初始化一次配置
        if not Logger._initialized:
            self._setup_logging()
            Logger._initialized = True
            
        # 绑定上下文信息（模块名）
        self._logger = logger.bind(name=self.name)
    
    def _setup_logging(self):
        """配置日志记录器"""
        # 确保日志目录存在
        os.makedirs(BP.LOG_DIR, exist_ok=True)
        
        # 生成日志文件名
        log_file = os.path.join(BP.LOG_DIR, f"{datetime.now().strftime('%Y%m%d_%H_%M')}.log")
        
        # 移除默认配置
        logger.remove()
        
        # 解析日志级别
        # level = config.get('level', 'DEBUG')
        level = config['level']
        
        # 设置日志格式
        # formatter = config.get('formatter', "{time:YYYY-MM-DD HH:mm:ss.SSS} - {extra[name]} - {line} - {level} - {message}")
        formatter = config['formatter']
        
        # 添加控制台输出
        # console_level = config.get('stream_handler_level', level)
        console_level = config['stream_handler_level']
        logger.add(
            sys.stdout,
            level=console_level,
            format=formatter,
            colorize=True,
            backtrace=True,
            diagnose=True
        )
        
        # 添加文件输出
        # file_level = config.get('file_handler_level', level)
        file_level = config['file_handler_level']
        logger.add(
            log_file,
            level=file_level,
            format=formatter,
            encoding='utf-8',
            backtrace=True,
            diagnose=True,
            rotation="100 MB",  # 日志文件大小达到100MB时轮转
            # retention="30 days",  # 保留30天的日志
            compression="zip",      # 轮转时自动压缩
        )
    
    def getLogger(self):
        """返回日志记录器对象"""
        return self._logger
    

# 创建全局默认日志记录器
default_logger = Logger().getLogger()



if __name__ == '__main__':
    # 使用示例
    logger = Logger('Base/baseLogger.py').getLogger()
    logger.info('这是info级别的信息')
    logger.success('这是success级别信息')
    
    # 测试异常记录
    try:
        1 / 0
    except ZeroDivisionError:
        logger.exception("发生了除零错误")

    default_logger.info('这是info级别信息')

    # level = config.get('level')
    # level2 = config['level']
    # print(level)
    # print(level2)



    