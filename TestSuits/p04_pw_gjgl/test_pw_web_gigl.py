import time
import pytest
from Base.baseData import DataDriver
from PageObject.p04_pw_gjgl.pw_web_login_page import LoginPage
from PageObject.p04_pw_gjgl.pw_web_article_page import ArticlePage
from PageObject.p04_pw_gjgl.pw_web_file_page import FilePage


class TestCase01():
    """ playwright自动化, 稿件管理，登陆功能模块 """
    @pytest.mark.parametrize('case_data', DataDriver().get_case_data('01_登陆功能'))
    @pytest.mark.usefixtures("page")
    def test_login_gjgl(self, page, case_data):
        """ web自动化, 稿件管理，用户登陆测试 """
        bp = LoginPage()
        bp.login(case_data['username'], case_data['password'])
        time.sleep(1)
        bp.assert_login_success(case_data['flag'])


class TestCase02():
    """ playwright自动化, 稿件管理，添加稿件功能模块 """
    # @pytest.mark.parametrize('case_data', DataDriver().get_case_data('02_添加稿件'))
    # @pytest.mark.usefixtures("page", "init_login")
    # def test_add_article(self, case_data, page, init_login):
    #     """ web自动化, 稿件管理，添加稿件测试 """
    #     bp = ArticlePage()
    #     bp.add_article(case_data['title'], case_data['content'])

    @pytest.mark.parametrize('case_data', DataDriver().get_case_data('02_添加稿件'))
    @pytest.mark.usefixtures("page", "init_login")
    def test_delete_article(self, page, init_login, case_data):
        """ web自动化, 稿件管理，删除稿件测试 """
        bp = ArticlePage()
        bp.add_article(case_data['title'], case_data['content'])
        bp.delete_article()


class TestCase03():
    """ playwright自动化, 稿件管理，文件功能模块 """

    @pytest.mark.parametrize('case_data', DataDriver().get_case_data('06_文件夹操作'))
    @pytest.mark.usefixtures('page', 'init_login')
    def test_create_folder(self, case_data, page, init_login):
        """ web自动化, 稿件管理，创建&删除文件夹测试 """
        fp = FilePage()  
        fp.create_folder(case_data['name'], case_data['description'])
        fp.delete_folder()

    @pytest.mark.parametrize('case_data', DataDriver().get_case_data('07_上传文件'))
    @pytest.mark.usefixtures('page', 'init_login', 'add_del_folder')
    def test_upload_file(self, case_data, page, init_login, add_del_folder):
        """ web自动化, 稿件管理，上传文件测试 """
        fp = FilePage()
        fp.upload_file(case_data['rename'], case_data['description'], case_data['file_path'])
        fp.assert_upload_file_page(case_data['rename'], case_data['description'])  
        # fp.assert_upload_file_databases(case_data['rename'], case_data['description']) 

    @pytest.mark.parametrize('case_data', DataDriver().get_case_data('08_下载文件'))
    @pytest.mark.usefixtures('page', 'init_login', 'add_del_folder')
    def test_download_file(self, case_data, page, init_login, add_del_folder):
        """ web自动化, 稿件管理，下载文件测试 """
        fp = FilePage()
        fp.upload_file(case_data['rename'], case_data['description'], case_data['file_path'])
        fp.download_file(case_data['save_path'])
        fp.assert_download_file()
