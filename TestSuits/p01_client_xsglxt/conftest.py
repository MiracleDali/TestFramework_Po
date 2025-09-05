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