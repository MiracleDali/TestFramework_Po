import sys
from pathlib import Path
Base_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(Base_DIR))


from Base.baseData import DataDriver
from PageObject.p02_web_gjxt.web_login_page import LoginPage
import pytest


class TestCase01(object):
    """ web自动化, 稿件管理，登陆功能模块 """

    @pytest.mark.parametrize('case_data', DataDriver().get_case_data('01_登陆功能'))
    @pytest.mark.usefixtures('driver')
    def test_login(self, driver,  case_data):
        """ web自动化, 稿件管理，用户登陆测试 """
        lp = LoginPage()
        lp.login(case_data['username'], case_data['password'])
        lp.assert_login_success(case_data['flag'])