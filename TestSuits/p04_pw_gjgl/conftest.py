import pytest
from PageObject.p04_pw_gjgl.pw_web_login_page import LoginPage
from PageObject.p04_pw_gjgl.pw_web_file_page import FilePage

@pytest.fixture(scope='function')
def init_login():
    lp = LoginPage()
    lp.login(username='test01', password='1111')


@pytest.fixture(scope='function')
def add_del_folder():
    fp = FilePage()
    fp.create_folder('测试文件夹', '测试文件夹描述')
    yield
    fp.delete_folder()