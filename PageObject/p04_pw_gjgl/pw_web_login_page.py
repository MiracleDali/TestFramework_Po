"""
使用 playwright 重写稿件管理测试用例
"""

import sys
import pathlib
import time

Base = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.append(str(Base))

from Base.basePath import BasePath as BP
from Base.utils import read_config_ini
from Base.baseAutoWebPw import WebBase
from Base.baseContainer import GlobalManager
from Base.baseLogger import Logger

logger = Logger('PageObject\p04_pw_test\pw_web_login_page.py').getLogger()

class LoginPage(WebBase):
    """ 示例：使用Playwright基类 """

    def __init__(self):
        super().__init__()
        self.config = read_config_ini(BP.CONFIG_FILE)

    def login(self, username, password):
        """ 稿件系统登陆 """
        logger.info('稿件系统开始执行登陆')
        self.goto("http://172.25.64.149")
        self.wait_for_timeout(2000)
        self.fill("[name='_58_login']", username)
        self.fill('[name="_58_password"]', password)
        self.page.reload
        self.wait_for_timeout(1000)
        self.click("//input[@type='submit' and @value='登录']")
        self.wait_for_timeout(1000)
        logger.info('稿件系统登陆成功')

    def assert_login_success(self, flag):
        """ 验证登陆成功 """
        if flag == 'success':
            assert self.is_visible("//div[@id='navigation']/ul/li[2]/a/span") == True, '[断言] 正确账号密码登陆失败'
            logger.info('[断言] 正确账号密码登陆成功-通过')
        elif flag == 'fail':
            assert self.is_visible("//div[@id='navigation']/ul/li[2]/a/span") == False, '[断言] 错误账号密码登陆成功'
            logger.info('[断言] 错误账号密码登陆失败-通过')



if __name__ == "__main__":
    from playwright.sync_api import sync_playwright

    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    context.tracing.start(snapshots=True, sources=True, screenshots=True)
    page = context.new_page()

    # 将 Page 对象存储在全局管理器中
    GlobalManager().set_value('page', page)

    LoginPage().login('test01', '1111')