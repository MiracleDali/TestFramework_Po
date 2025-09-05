"""
# file:     Base/basePath.py
# 项目路径管理
"""

import os

class BasePath:
    #  这些为类变量，不能被修改
    #  项目根目录
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    #  项目配置文件目录
    CONFIG_DIR = os.path.join(PROJECT_ROOT, 'Config')
    CONFIG_FILE = os.path.join(CONFIG_DIR, '配置文件.ini')

    #  Data文件路径
    DATA_DIR = os.path.join(PROJECT_ROOT, 'Data')
    DATA_DRIVER_DIR = os.path.join(DATA_DIR, 'DataDriver')
    DATA_ELEMENT_DIR = os.path.join(DATA_DIR, 'DataElement')

    DATA_TEMP_DIR = os.path.join(DATA_DIR, 'Temp')
    SCREENSHOT_DIR = os.path.join(DATA_TEMP_DIR, 'Screenshots')
    SCREENSHOT_PIC = os.path.join(SCREENSHOT_DIR, 'errar_pic.png')

    # pyside6 用例管理路径
    TEST_CASES = os.path.join(DATA_TEMP_DIR, 'test_cases.yaml')
    TEMP_CASES = os.path.join(DATA_TEMP_DIR, 'temp_cases.yaml')

    #  Driver文件路径
    DRIVER_DIR = os.path.join(PROJECT_ROOT, 'Driver')

    #  Log文件路径
    LOG_DIR = os.path.join(PROJECT_ROOT, 'Log')

    #  Report文件路径
    ALLURE_DIR = os.path.join(PROJECT_ROOT, 'Report', 'ALLURE')
    ALLURE_REPORT = os.path.join(ALLURE_DIR, 'Report')
    ALLURE_RESULT = os.path.join(PROJECT_ROOT, 'Result')
    HTML_DIR = os.path.join(PROJECT_ROOT, 'Report', 'HTML')
    XML_DIR = os.path.join(PROJECT_ROOT, 'Report', 'XML')

    # 用例路径
    TEST_SUITE_DIR = os.path.join(PROJECT_ROOT, 'TestSuits')



if  __name__ == '__main__':
    print(BasePath.PROJECT_ROOT)
    print(BasePath.CONFIG_DIR)
    print(BasePath.DATA_DIR)
    print(BasePath.DATA_DRIVER_DIR)
    print(BasePath.DATA_ELEMENT_DIR)
    print(BasePath.DATA_TEMP_DIR)
    print(BasePath.DRIVER_DIR)
    print(BasePath.LOG_DIR)
    print(BasePath.ALLURE_DIR)
    print(BasePath.HTML_DIR)
    print(BasePath.XML_DIR)