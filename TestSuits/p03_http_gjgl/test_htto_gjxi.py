from Base.baseData import DataDriver
from PageObject.p03_http_gjgl.api_login_page import LoginPage
import pytest


class TestApiCase01():
    """ 接口自动化稿件管理系统-登录功能模块 """
    @pytest.mark.parametrize('case_data', DataDriver().get_case_data('01稿件系统登录'))
    def test_login_case01(self, case_data):
        """ 接口自动化-用户登录测试 """
        lp = LoginPage()
        res = lp.login(case_data['username'], case_data['password'])
        lp.assert_login_success(res, case_data['title'])