import pytest
from PageObject.p02_web_gjxt.web_login_page import LoginPage
from PageObject.p02_web_gjxt.web_article_page import ArticlePage

@pytest.fixture(scope='function')
def init_login():
    """ 稿件系统登陆 """
    lp = LoginPage()
    lp.login(username='test01', password='1111')


@pytest.fixture(scope='function')
def delete_article():
    """ 删除稿件 """
    yield
    ap = ArticlePage()
    ap.delete_article()