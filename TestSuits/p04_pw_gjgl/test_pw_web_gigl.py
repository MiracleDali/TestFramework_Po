import time
import pytest
from Base.baseData import DataDriver
from PageObject.p04_pw_gjgl.pw_web_login_page import LoginPage
from PageObject.p04_pw_gjgl.pw_web_article_page import ArticlePage


class TestCase01():
    """ playwright自动化, 稿件管理，登陆功能模块 """
    @pytest.mark.parametrize('case_data', DataDriver().get_case_data('01_登陆功能'))
    @pytest.mark.usefixtures("page")
    def test_login_gjgl(self, page, case_data):
        """ web自动化, 稿件管理，用户登陆测试 """
        bp = LoginPage()
        bp.login(case_data['username'], case_data['password'])
        time.sleep(1)
        bp.assert_login_success(case_data['flag'])


class TestCase02():
    """ playwright自动化, 稿件管理，添加稿件功能模块 """
    @pytest.mark.parametrize('case_data', DataDriver().get_case_data('02_添加稿件'))
    @pytest.mark.usefixtures("page", "init_login")
    def test_add_article(self, case_data, page, init_login):
        """ web自动化, 稿件管理，添加稿件测试 """
        bp = ArticlePage()
        bp.add_article(case_data['title'], case_data['content'])