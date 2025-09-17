"""
# file:     Base/baseContainer.py
# 全局变量管理器封装
# 使用单例模式
"""
import sys
from pathlib import Path
# 获取当前文件的父目录的父目录（项目根目录）
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from Base.baseLogger import Logger
logger = Logger('Base/baseContainer.py').getLogger()

class GlobalManager(object):
    """ 单例模式全局变量管理器 """
    _globaldict = {}
    _instance = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(GlobalManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def set_value(self, name, value):
        self._globaldict[name] = value

    def get_value(self, name):
        try:
            return self._globaldict[name]
        except KeyError:
            logger.error(f'获取的变量不存在{name}')
            # print(f'获取的变量不存在{name}')
            return None


if __name__ == '__main__':
    gm1 = GlobalManager()
    gm1.set_value('a', 'value_a')

    gm2 = GlobalManager()
    print(gm2.get_value('a'))
