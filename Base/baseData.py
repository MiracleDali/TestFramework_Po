"""
# file:     Base/baseData.py
# 元素或接口数据自动读取
"""

import sys
from pathlib import Path
# 获取当前文件的父目录的父目录（项目根目录）
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

import os
from string import Template
import yaml
from Base.baseContainer import GlobalManager
from Base.baseLogger import Logger
from Base.basePath import BasePath as BP
from Base.utils import read_config_ini
from Base.baseYaml import read_yaml
from Base.baseExcel import ExcelRead

logger = Logger('Base/baseData.py').getLogger()

def init_file_path(folder_path):
    """遍历文件夹下所有文件路径"""
    path = {}
    for dirpath, _, filenames in os.walk(folder_path):
        for filename in filenames:
            # if filename.endswith('.yaml') or filename.endswith('.yml') or filename.endswith('.xlsx'):
            # 获取不带扩展名的文件名
            name = os.path.splitext(filename)[0]
            # 存储完整路径
            path[name] = os.path.join(dirpath, filename)
    return path


def is_file_exist(file_path, yaml_name):
    """ 检查文件是否存在 """
    abs_path = file_path.get(yaml_name)
    if not abs_path:
        raise FileNotFoundError(f"文件不存在，请检查文件路径是否正确 & 请确认测试 type 是否正确（HTTP、WEB、CLIENT）: {yaml_name}")
    return abs_path


class DataBase:
    """ 逻辑层数据读取 """
    def __init__(self, yaml_name = None):
        self.gm = GlobalManager()

        self.yaml_name = yaml_name

        self.config = read_config_ini(BP.CONFIG_FILE)
        self.run_config = self.config['项目运行设置']
        self.api_path = init_file_path(os.path.join(BP.DATA_ELEMENT_DIR, self.run_config['TEST_PROJECT']))

        # 判断测试类型 （自动化测试类型：HTTP、WEB、CLIENT）
        if not self.run_config['AUTO_TYPE'] == 'CLIENT':
            self.abs_path = is_file_exist(self.api_path, self.yaml_name)
            print(self.abs_path)

    def get_element_data(self, change_data=None):
        """
        change_data: 是否修改数据
        """
        if change_data:
            with open(self.abs_path, 'r', encoding='utf-8') as f:
                cfg = f.read()
                content = Template(cfg).safe_substitute(**change_data)
                return yaml.load(content, Loader=yaml.FullLoader)
        else:
            return read_yaml(self.abs_path)


class DataDriver:
    """ 读取数据 """
    def __init__(self):
        self.gm = GlobalManager()
        self.config = read_config_ini(BP.CONFIG_FILE)

    def get_case_data(self, file_name):
        """ 获取用例数据 """
        data_type = self.config['项目运行设置']['DATA_DRIVER_TYPE']
        abs_path = init_file_path(os.path.join(BP.DATA_DRIVER_DIR, data_type, self.config['项目运行设置']['TEST_PROJECT']))
        data_path = is_file_exist(abs_path, file_name)

        if data_type == 'YamlDriver':
            return read_yaml(data_path)
        elif data_type == 'ExcelDriver':
            return ExcelRead(data_path).dict_date()




if __name__ == '__main__':
    res = init_file_path(r'D:\2_python_file\TestFramework_Po\Data\DataElement\project01_auto_test')
    res1 = is_file_exist(res, 'Web元素信息')
    print(res1)

    # element = DataBase('接口元素信息登陆')
    # change_data = {
    #     "username": "用户",
    #     "password": "密码"
    # }
    # res = element.get_element_data(change_data)
    # print(res)

    driver = DataDriver()
    res = driver.get_case_data('excel')
    print(res)