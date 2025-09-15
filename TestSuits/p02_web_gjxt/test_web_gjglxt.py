
from Base.baseData import DataDriver
from PageObject.p02_web_gjxt.web_article_page import ArticlePage
from PageObject.p02_web_gjxt.web_login_page import LoginPage
import pytest


class TestCase01():
    """ web自动化, 稿件管理，登陆功能模块 """

    @pytest.mark.parametrize('case_data', DataDriver().get_case_data('01_登陆功能'))
    @pytest.mark.usefixtures('driver')
    def test_login(self, driver,  case_data):
        """ web自动化, 稿件管理，用户登陆测试 """
        lp = LoginPage()
        lp.login(case_data['username'], case_data['password'])
        lp.assert_login_success(case_data['flag'])



class TestCase02():
    """ web自动化, 稿件管理，稿件管理模块 """
    @pytest.mark.parametrize('case_data', DataDriver().get_case_data('02_添加稿件'))
    @pytest.mark.usefixtures('driver', 'init_login')
    def test_add_article(self, case_data, driver, init_login):
        """  web自动化, 稿件管理，添加稿件测试 """
        ap = ArticlePage()
        ap.add_article(title=case_data['title'], content=case_data['content'])
        ap.assert_article_add_success(title=case_data['title'])
        ap.assert_add_database(title=case_data['title'])

    @pytest.mark.parametrize('case_data', DataDriver().get_case_data('03稿件删除'))  
    @pytest.mark.usefixtures('driver', 'init_login')
    def test_delete_article(self, driver, init_login, case_data):
        """ web自动化, 稿件管理，删除稿件测试 """
        ap = ArticlePage()
        # ap.add_article(title=case_data['title'], content='test content')   # 添加稿件
        ap.delete_article()   # 删除稿件
        ap.assert_delete_page_article(title=case_data['title'])
        ap.assert_delete_database_article(title=case_data['title'])

    @pytest.mark.parametrize('case_data', DataDriver().get_case_data('04_稿件修改'))
    @pytest.mark.usefixtures('driver', 'delete_article')
    def test_edit_article_case03(self, case_data, driver, delete_article):
        """ web自动化, 稿件管理，修改稿件测试 """
        ap = ArticlePage()
        ap.add_article(title='新增加稿件')  # 添加稿件
        ap.edit_article(title=case_data['title'])
        ap.assert_article_add_success(title=case_data['title'])
        ap.assert_add_database(title=case_data['title'])
