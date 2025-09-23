import sys
import pathlib
Base_dir = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.append(str(Base_dir))
import re
from Base.basePath import BasePath as BP
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
        re_info = self.query_folder()
        info = [i[1] for i in re_info if i[1] == folder_name]
        assert folder_name in info, '[断言] 新增文件夹断言失败'
        logger.info(f'[断言] 新增文件夹页面断言成功')

    def assert_add_folder_databases(self, folder_name, file_description):
        """ 新增文件夹数据库断言 """
        mysql = MysqlHelp()
        sql = f"select name, description from dlfolder order by createDate desc limit 1;"
        res = mysql.mysql_db_select(sql)
        assert res[0]['name'] == folder_name, '[断言] 新增文件夹数据库断言失败'
        assert res[0]['description'] == file_description, '[断言] 新增文件夹数据库断言失败'
        logger.info(f'[断言] 新增文件夹数据库断言成功')


    def delete_folder(self, folder_name):
        """ 文件夹删除 """
        res = self.query_folder()
        folder_id = None
        for i in res:
            if folder_name in i:
                folder_id = i[0]
        change_data = {
            '_20_folderId': folder_id
        }
        res = self.request_base('delete_folder_api', change_data)
        logger.info(f'删除文件夹结束')
        return res.text
    
    def assert_delete_folder(self, folder_name):
        """ 文件夹删除断言 """
        res = self.query_folder()
        assert folder_name not in str(res), '[断言] 文件夹删除断言失败'
        logger.info(f'[断言] 文件夹删除断言成功')

    
    def upload_file(self, rename, description):
        """ 文件上传 """
        folder_id = self.query_folder()[0][0]
        print('folder_id', folder_id)
        change_data = {
            '_20_title': rename.split('.')[0],
            '_20_description': description,
            'folderId': folder_id
        }
        file_path = pathlib.Path(BP.DATA_TEMP_DIR) / 'file_upload_download' / 'upload_file.txt'
        files = {
            '_20_file': ('upload_file.txt', open(file_path, 'rb'), 'text/plain')
        }
        res = self.request_base('file_upload_api', change_data=change_data, files=files)
        logger.info(f'文件上传结束')
        # logger.info(res.text)
        return res.text
    
    def assert_upload_file(self, res, rename):
        """ 文件上传页面验证 """
        name = re.findall('id="_20_title" name="_20_title" style="width: 350px; " type="text" value="(.*?)"', res)[0]
        assert name == rename.split('.')[0], '[断言] 文件上传页面验证失败'
        logger.info(f'[断言] 文件上传页面验证成功')

    def assert_upload_file_databases(self, rename, description):
        """ 文件上传数据库验证 """
        mysql = MysqlHelp()
        sql = f"SELECT title,description FROM dlfileentry ORDER BY createDate DESC LIMIT 1;"
        res = mysql.mysql_db_select(sql)
        assert res[0]['title'] == rename.split('.')[0], '[断言] 文件上传数据库验证失败'
        assert res[0]['description'] == description, '[断言] 文件上传数据库验证失败'
        logger.info(f'[断言] 文件上传数据库验证成功')


    def query_file(self, rename):
        """ 文件查询 """
        folder_id = self.query_folder()[0][0]
        change_data = {
                'folderid': folder_id,
                '_20_keywords': rename.split('.')[0]
        }
        res = self.request_base('query_file_api', change_data=change_data)
        # logger.info(res.text)
        return res.text
    
    def download_file(self, res, rename):
        """ 文件下载 """
        res = re.findall(r'library%2Fget_file&_20_folderId=(.*?)&_20_name=(.*?)">', res)[0]
        change_data = {
            '_20_folderId': res[0],
            '_20_name': res[1]
        }
        res = self.request_base('file_wodnload_api', change_data=change_data)
        file_path = pathlib.Path(BP.DATA_TEMP_DIR) / 'file_upload_download' / rename
        with open(file_path, 'wb') as f:
            f.write(res.content)
        logger.info(f'文件下载结束')

    def assert_download_file(self, download_file):
        """ 文件下载断言 """
        file_path = pathlib.Path(BP.DATA_TEMP_DIR) / 'file_upload_download' / download_file
        assert pathlib.Path(file_path).is_file(), '[断言] 文件下载断言失败'
        logger.info(f'[断言] 文件下载断言成功')


if __name__ == '__main__':
    from PageObject.p03_http_gjgl.api_login_page import LoginPage
    lp = LoginPage()
    lp.login('test01', '1111')

    af = ApiFile()
    res = af.add_folder('测试新增文件夹', '测试新增文件夹描述')
    af.assert_add_folder('测试新增文件夹')
    af.assert_add_folder_databases('测试新增文件夹', '测试新增文件夹描述')

    res = af.upload_file('rename_upload_file.txt', '测试上传文件描述')
    af.assert_upload_file(res, 'rename_upload_file.txt')
    af.assert_upload_file_databases('rename_upload_file.txt', '测试上传文件描述')

    res = af.query_file('rename_upload_file.txt')
    af.download_file(res, 'download_file.txt')
    af.assert_download_file('download_file.txt')

    af.delete_folder('测试新增文件夹')
    af.assert_delete_folder('测试新增文件夹')

    