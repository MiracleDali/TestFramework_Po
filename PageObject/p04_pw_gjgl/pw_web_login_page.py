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

logger = Logger(r'PageObject/p04_pw_test/pw_web_login_page.py').getLogger()

class LoginPage(WebBase):
    """ 示例：使用Playwright基类 （在构造时传入 YAML 名称以读取顶层 key） """

    def __init__(self):
        # 传入 yaml 文件名以便 WebBase 在构造时加载元素数据
        super().__init__(yaml_name='01登陆页面元素信息页面')
        self.config = read_config_ini(BP.CONFIG_FILE)
        self.ip = self.config['项目运行设置']['TEST_URL']

    def login(self, username, password):
        """ 稿件系统登陆 — 这里的 "username"/"password"/"login_btn" 都必须是 YAML 顶层 key """
        logger.info('稿件系统开始执行登陆')
        self.goto(self.ip)
        self.wait_for_timeout(2000)
        self.fill("username", username)
        self.fill("password", password)
        self.wait_for_timeout(1000)
        self.click("login_btn")
        self.wait_for_timeout(1000)
        self.page.reload()
        logger.info('稿件系统登陆成功')

    def assert_login_success(self, flag):
        """ 验证登陆成功 """
        if flag == 'success':
            assert self.is_visible("文档上传下载按钮") == True, '[断言] 正确账号密码登陆失败'
            logger.info('[断言] 正确账号密码登陆成功-通过')
        elif flag == 'fail':
            assert self.is_visible("文档上传下载按钮") == False, '[断言] 错误账号密码登陆成功'
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

    lp = LoginPage()
    lp.login('test01', '1111')
    lp.assert_login_success('success')