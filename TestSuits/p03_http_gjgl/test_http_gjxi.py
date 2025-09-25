import time
from Base.baseData import DataDriver
from PageObject.p03_http_gjgl.api_login_page import LoginPage
from PageObject.p03_http_gjgl.api_article_page import ApiArticle
from PageObject.p03_http_gjgl.api_file_page import ApiFile
import pytest
import os


class TestApiCase01():
    """ 接口自动化稿件管理系统-登录功能模块 """
    @pytest.mark.parametrize('case_data', DataDriver().get_case_data('01稿件系统登录'))
    def test_login_case01(self, case_data):
        """ 接口自动化-用户登录测试 """
        lp = LoginPage()
        res = lp.login(case_data['username'], case_data['password'])
        lp.assert_login_success(res, case_data['title'])


class TestApiCase02():
    """ 接口自动化稿件管理系统-稿件管理模块"""

    @pytest.mark.smoke
    @pytest.mark.parametrize('case_data', DataDriver().get_case_data('02稿件新增'))
    @pytest.mark.usefixtures('init_login')
    def test_add_article_case01(self, case_data, init_login):
        """ 接口自动化-添加稿件测试 """
        ap = ApiArticle()
        ap.add_article(case_data['title'], case_data['content'])
        ap.assert_add_article(case_data['title'])
        # ap.assert_add_article_databases(case_data['title'], case_data['content'])
        time.sleep(1)


    @pytest.mark.parametrize('case_data', DataDriver().get_case_data('03稿件删除'))
    @pytest.mark.usefixtures('init_login')
    def test_delete_article_case02(self, case_data, init_login):
        """ 接口自动化-测试稿件删除 """
        ap = ApiArticle()
        # ap.add_article(case_data['title'], '删除测试！！！')
        ap.delete_article(case_data['title'])
        ap.assert_delete_article(case_data['title'])
        # ap.assert_delete_article_databases(case_data['title'])


    @pytest.mark.parametrize('add_del_article_edit', DataDriver().get_case_data('04稿件修改'), indirect=True)    
    @pytest.mark.usefixtures('init_login')
    def test_edit_article_case03(self, init_login, add_del_article_edit):
        """ 接口自动化-测试稿件编辑 """
        ap = ApiArticle()
        ap.edit_article(add_del_article_edit['title'], add_del_article_edit['edit_title'], add_del_article_edit['edit_content'])
        ap.assert_add_article(add_del_article_edit['edit_title'])
        # ap.assert_add_article_databases(add_del_article_edit['edit_title'], add_del_article_edit['edit_content'])
        # time.sleep(0.2)

    @pytest.mark.parametrize('add_del_article', DataDriver().get_case_data('05稿件查询'), indirect=True)    
    @pytest.mark.usefixtures('init_login')
    def test_select_article_case04(self, init_login, add_del_article):
        """ 接口自动化-测试稿件查询 """
        ap = ApiArticle()
        res = ap.search_article(title=add_del_article['title'])
        ap.assert_search_article(res, add_del_article['title'])
        # ap.assert_search_article_database(add_del_article['title'])


class TestApiCase03():
    """ 接口自动化稿件管理系统-文件上传下载模块 """

    @pytest.mark.parametrize('case_data', DataDriver().get_case_data('06文件夹新增和删除'))
    @pytest.mark.usefixtures('init_login')
    def test_file_case01(self, case_data, init_login):
        """ 接口自动化-测试文件夹创建删除 """
        af = ApiFile()
        af.add_folder(case_data['folder_name'], case_data['folder_description'])
        af.assert_add_folder(case_data['folder_name'])
        af.assert_add_folder_databases(case_data['folder_name'], case_data['folder_description'])
        af.delete_folder(case_data['folder_name'])
        af.assert_delete_folder(case_data['folder_name'])


    @pytest.mark.parametrize('case_data', DataDriver().get_case_data('07文件上传下载'))
    @pytest.mark.usefixtures('init_login', 'add_del_folder')
    def test_file_case02(self, case_data, init_login, add_del_folder):
        """ 测试上传文件 """
        af = ApiFile()
        res = af.upload_file(case_data['rename'], case_data['description'])
        af.assert_upload_file(res, case_data['rename'])
        # af.assert_upload_file_databases(case_data['rename'], case_data['description'])

    @pytest.mark.parametrize('case_data', DataDriver().get_case_data('08文件下载'))
    @pytest.mark.usefixtures('init_login', 'add_del_folder')
    def test_file_case03(self, init_login, add_del_folder, case_data):
        """ 测试下载文件 """
        af = ApiFile()
        af.upload_file(case_data['rename'], case_data['description'])
        res = af.query_file(case_data['rename'])
        af.download_file(res, case_data['download_file'])
        af.assert_download_file(case_data['download_file'])

