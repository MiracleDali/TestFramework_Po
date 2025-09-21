from PageObject.p03_http_gjgl.api_login_page import LoginPage
import pytest

@pytest.fixture(scope='function')
def init_login():
    login_page = LoginPage()
    login_page.login(username='test01', password='1111')
