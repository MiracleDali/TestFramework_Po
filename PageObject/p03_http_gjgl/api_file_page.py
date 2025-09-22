import sys
import pathlib
Base_dir = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.append(str(Base_dir))
import re
from Base.baseAutoHTTP import ApiBase
from Base.baseLogger import Logger
from ExtTools.dbbase import MysqlHelp
import time
logger = Logger('PageObject/p03_http_gjgl/api_file_page.py').getLogger()


class ApiFile(ApiBase):
    def __init__(self):
        super().__init__('03文件管理接口信息')

    def add_folder(self, folder_name, file_description):
        """ 文件夹新增 """
        change_data = {
            '_20_name': folder_name,
            '_20_description': file_description
        }
        res = self.request_base('add_folder', change_data)
        logger.info(f'{folder_name}：新增文件夹结束')
        return  res

    def query_folder(self):
        """ 文件夹查询 """
        res = self.request_base('query_folder_api')
        res_info = re.findall('library%2Fview&_20_folderId=(.*?)">(.*?)</a>', res.text)
        return res_info

    def assert_add_folder(self, folder_name):
        """ 新增文件夹页面断言 """
        re_info = self.query_folder()[0]
        assert folder_name in re_info, '[断言] 新增文件夹断言失败'
        logger.info(f'[断言] 新增文件夹页面断言成功')

    def assert_add_folder_databases(self, folder_name, file_description):
        """ 新增文件夹数据库断言 """
        mysql = MysqlHelp()
        sql = f"select name, description from dlfolder order by createDate desc limit 1;"
        res = mysql.mysql_db_select(sql)
        assert res[0]['name'] == folder_name, '[断言] 新增文件夹数据库断言失败'
        assert res[0]['description'] == file_description, '[断言] 新增文件夹数据库断言失败'
        logger.info(f'[断言] 新增文件夹数据库断言成功')


if __name__ == '__main__':
    from PageObject.p03_http_gjgl.api_login_page import LoginPage
    lp = LoginPage()
    lp.login('test01', '1111')

    af = ApiFile()
    res = af.add_folder('测试新增文件夹', '测试新增文件夹描述')
    af.assert_add_folder('测试新增文件夹')
    af.assert_add_folder_databases('测试新增文件夹', '测试新增文件夹描述')
