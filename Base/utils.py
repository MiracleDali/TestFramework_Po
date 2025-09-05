"""
# file:     Base/utils.py
# 读取-配置文件.ini
# 打包zip文件
"""

import sys
from pathlib import Path
# 获取当前文件的父目录的父目录（项目根目录）
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
# print(sys.path)

from configparser import RawConfigParser
from Base.basePath import BasePath
import os
import zipfile


def read_config_ini(config_path):
    """ 读取-配置文件.ini """
    config = RawConfigParser()    # 创建RawConfigParser对象
    config.read(config_path, encoding='utf-8')
    return config

def make_zip(local_path, pname):
    """ 打包zip """
    zipf = zipfile.ZipFile(pname, 'w', zipfile.ZIP_DEFLATED)
    pre_len = len(os.path.dirname(local_path))
    for parent, dirnames, filenames in os.walk(local_path):
        for filename in filenames:
            pathfile = os.path.join(parent,  filename)
            arcname = pathfile[pre_len:].strip(os.path.sep)
            zipf.write(pathfile,  arcname)
    zipf.close()
    return pname


def file_all_dele(path):
    """ 删除文件及文件夹下所有文件  """
    for filename in os.listdir(path):
        os.unlink(os.path.join(path, filename))


if __name__ == '__main__':
    config = read_config_ini(BasePath.CONFIG_FILE)
    print(config['客户端自动化配置']['confidence'])