import sys
from pathlib import Path
import time
Base_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(Base_dir))

from Base.basePath import BasePath as BP
from Base.utils import read_config_ini
from Base.baseAutoWeb import WebBase
from Base.baseLogger import Logger

logger = Logger(r'PageObject\p02_web_gjxt\web_login_page.py').getLogger()


class LoginPage(WebBase):

    def __init__(self):
        super().__init__('01登陆页面元素信息页面')
        self.config = read_config_ini(BP.CONFIG_FILE)
    
    def login(self, username, password):
        """ 稿件系统登陆 """
        logger.info('稿件系统开始执行登陆')
        self.get_url(self.config['项目运行设置']['TEST_URL'])
        time.sleep(1)
        # 输入用户名
        self.clear('login/username')
        self.send_keys('login/username', username)
        # 输入密码
        time.sleep(1)
        self.clear('login/password')
        time.sleep(0.5)
        self.send_keys('login/password', password)
        # 点击登陆
        self.click('login/loginbtn')
        logger.info('稿件系统登陆成功')

    def assert_login_success(self, flag):
        """ 断言登陆成功 """
        if flag == 1:
            assert self.get_title() == "测试比对样品 - 稿件管理", "[断言]登陆失败"
            logger.info('[断言]登陆成功')

            assert self.get_text('login/welcome') == "Welcome test01!", "[断言]用户名获取失败"

        if flag == 2:
            assert self.get_title() == "测试比对样品 - 登录", "[断言] 错误账号验证登陆失败，失败"
            logger.info('[断言]错误用户名验证登陆失败，成功')

        if flag == 3:
            assert self.get_title() == "测试比对样品 - 登录", "[断言] 错误密码验证登陆失败，失败"
            logger.info('[断言]错误密码验证登陆失败，成功')



if __name__ == '__main__':

    from selenium import webdriver
    # 避免浏览器闪退
    option = webdriver.ChromeOptions()
    option.add_experimental_option("detach", True)
    # 创建浏览器对象 打开浏览器
    driver = webdriver.Chrome(options=option)  
    
    from Base.baseContainer import GlobalManager
    gm  = GlobalManager()
    gm.set_value('driver', driver)


    login_page = LoginPage()
    login_page.login('test01', '1111')