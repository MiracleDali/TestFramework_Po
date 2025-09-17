
import pytest
from Base.baseData import DataDriver
from PageObject.p04_pw_gjgl.pw_web_login_page import LoginPage


class TestCase01():
    """ playwright自动化, 稿件管理，登陆功能模块 """
    @pytest.mark.parametrize('case_data', DataDriver().get_case_data('01_登陆功能'))
    @pytest.mark.usefixtures("page")
    def test_login_gjgl(self, page, case_data):
        """ web自动化, 稿件管理，用户登陆测试 """
        bp = LoginPage()
        bp.login(case_data['username'], case_data['password'])
        bp.assert_login_success(case_data['flag'])