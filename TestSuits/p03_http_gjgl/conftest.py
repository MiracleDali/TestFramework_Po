from PageObject.p03_http_gjgl.api_article_page import ApiArticle
from PageObject.p03_http_gjgl.api_file_page import ApiFile
from PageObject.p03_http_gjgl.api_login_page import LoginPage
import pytest

@pytest.fixture(scope='function')
def init_login():
    login_page = LoginPage()
    login_page.login(username='test01', password='1111')



@pytest.fixture(scope='function')
def add_del_article_edit(request):
    """ 稿件新增删除_修改稿件使用 """
    case_data = request.param
    api = ApiArticle()
    api.add_article(title=case_data['title'], content='添加测试内容')
    yield case_data
    api.delete_article(title=case_data['edit_title'])


@pytest.fixture(scope='function')
def add_del_article(request):
    """ 稿件新增删除 """
    case_data = request.param
    api = ApiArticle()
    api.add_article(title=case_data['title'], content=case_data['content'])
    yield case_data
    api.delete_article(title=case_data['title'])


@pytest.fixture(scope='function')
def add_del_folder():
    """ 文件夹新增删除 """
    api = ApiFile()
    api.add_folder(folder_name='测试新增文件夹名称1', file_description='测试新增文件夹描述1')
    yield
    api.delete_folder(folder_name='测试新增文件夹名称1')