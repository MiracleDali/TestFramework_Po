import pytest
from PageObject.p04_pw_gjgl.pw_web_login_page import LoginPage


@pytest.fixture(scope='function')
def init_login():
    lp = LoginPage()
    lp.login(username='test01', password='1111')