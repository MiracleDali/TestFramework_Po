"""
# file:     Base/baseAutoWeb.py
# WEB自动化
"""


from Base.baseData import DataBase
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from Base.baseLogger import Logger

logger = Logger('Base/baseAutoWeb.py').getLogger()


class WebBase(DataBase):
    """ WEB自动化基类 """

    def __init__(self, yaml_name):
        super().__init__(yaml_name)
        self.driver = self.gm.get_value('driver')
        self.t = 0.5
        self.timeout = 10

    def get_locator_data(self, locator, change_data=None):
        """
        获取元素数据
        param: change_data: 是否修改yaml数据
        param: locator: (login/password)-->yaml文件的层级
        """
        res = self.get_element_data(change_data)  # 读取到的yaml文件信息
        # print(res)
        items = locator.split('/')  # 吧传进来的字符串，使用 / 分割成列表 --> ["login", "password"]
        # print(items)
        # print([items[0]])
        locator_data = tuple(res[items[0]][items[1]])
        return locator_data


if __name__ == '__main__':
    wb = WebBase('Web元素信息')
    res = wb.get_locator_data(locator="login/login_error_message")
    print(res)