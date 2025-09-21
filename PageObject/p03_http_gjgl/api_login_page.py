import sys
import pathlib

Base_dir = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.append(str(Base_dir))
from Base.baseAutoHTTP import ApiBase
from Base.baseLogger import  Logger
import re

logger = Logger('PageObject/p03_http_gjgl/api_login_page.py').getLogger()


class LoginPage(ApiBase):
    def __init__(self):
        super().__init__('01登陆接口信息')

    def login(self, username, password):
        """ 这是稿件管理的登录功能 """
        logger.info('稿件管理登录开始')
        # 获取首页信息
        self.request_base('home_api')

        change_data = {
            "_58_login": username,
            "_58_password": password
        }
        # 登录
        res = self.request_base(api_name='login_api', change_data=change_data)
        return res.text

    def assert_login_success(self, res, title):
        """ 断言登陆成功 """
        logger.info('[断言] 登录断言开始')
        page_title = re.findall('<title>(.*?)</title>', res)[0]
        logger.info(f'[断言] 登录断言结果：{page_title}')
        assert page_title == title, '[断言] 登录断言失败'
        logger.info('[断言] 登录断言成功')



if __name__ == '__main__':
    lp = LoginPage()
    res = lp.login('test01', '1111')
    lp.assert_login_success(res, '测试比对样品 - 稿件管理')