import time
import pytest
from PageObject.p01_client_xsglxt.client_start_stop import ClientPage


@pytest.fixture(scope="function")
def init_client():
    """ 客户端前置和后置 """
    cg = ClientPage()
    cg.start_client()
    yield
    cg.close_client()
    time.sleep(2)

@pytest.fixture(scope="function")
def teacher_login():
    """ 老师登录 """
    cg = ClientPage()
    cg.client_login('123', '123')

@pytest.fixture(scope="function")
def student_login():
    """ 学生登录 """
    cg = ClientPage()
    cg.client_login('201901010103', '123')



