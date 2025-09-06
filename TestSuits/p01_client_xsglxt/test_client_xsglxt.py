import pytest

from Base.baseData import DataDriver
from PageObject.p01_client_xsglxt.client_start_stop import ClientPage


class TestClientCase1():
    """ 客户端自动化-学生管理系统-登录功能模块 """

    @pytest.mark.parametrize('case_data', DataDriver().get_case_data('01学生管理系统登录'))
    @pytest.mark.usefixtures("init_client")
    def test_login_case01(self, case_data):
        """ 客户端自动化用例-用户登录 """
        cp = ClientPage()
        cp.client_login(case_data['username'], case_data['password'])
        cp.assert_login_success(case_data['flag'])

