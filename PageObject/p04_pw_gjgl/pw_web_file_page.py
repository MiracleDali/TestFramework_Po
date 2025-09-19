import sys
import pathlib
import time

Base = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.append(str(Base))

from ExtTools.dbbase import MysqlHelp
from Base.basePath import BasePath as BP
from Base.utils import read_config_ini
from Base.baseAutoWebPw import WebBase
from Base.baseContainer import GlobalManager
from Base.baseLogger import Logger

logger = Logger(r'PageObject/p04_pw_test/pw_web_login_page.py').getLogger()


class FilePage(WebBase):
    def __init__(self):
        super().__init__('03文件上传下载')

    def create_folder(self, name, description):
        """ 创建文件夹 """
        logger.info('创建文件夹开始')
        self.click('file_page')
        time.sleep(1)
        self.click('new_folder_btn')
        time.sleep(1)
        self.clear('folder_name')
        self.fill('folder_name', name)
        self.fill('folder_desc', description)
        self.click('save_folder')
        logger.info('创建文件夹结束')

    def delete_folder(self):
        """ 删除文件夹 """
        logger.info('删除文件夹开始')
        self.click('file_page')
        self.wait_for_timeout(1000)
        hand = self.on_dialog(handler_type='accept')
        self.wait_for_timeout(1000)
        self.click('first_delete_btn')
        self.wait_for_timeout(1000)
        off = self.off_dialog(hand)
        logger.info('删除文件夹结束')
        self.wait_for_timeout(1000)

    def upload_file(self, rename, description, file_path):
        """ 上传文件 """
        logger.info('上传文件开始')
        self.click('file_page')
        self.click('select_folder')  # 文件夹
        self.wait_for_timeout(1000)
        self.click('upload_btn')
        logger.info('切换iframe')
        with self.frame_context(selector='iframe_file'):
            # path = pathlib.Path(BP.DATA_TEMP_DIR).joinpath(file_path)
            self.set_input_files('select_file_box', file_path)
            self.fill('file_rename', rename)
            self.fill('file_description', description)
            self.click('submit_file')
        logger.info('退出iframe')
        self.wait_for_timeout(500)
        logger.info('上传文件结束')

    def assert_upload_file_page(self, rename, description):
        """ 断言上传文件成功-页面 """
        filef_info = self.inner_text('first_file_name')
        assert filef_info.split('\n')[0] == rename, '[断言] 文件上传失败!'
        assert filef_info.split('\n')[1] == description, '[断言] 文件上传失败!'
        logger.info('[断言] 文件上传成功')

    def assert_upload_file_databases(self, rename, description):
        """ 断言上传文件成功-数据库 """
        rename = rename.split('.')[0]
        db = MysqlHelp()
        sql = f"select title, description from dlfileentry where title = '{rename}';"
        res = db.mysql_db_select(sql)
        assert res[0]['title'] == rename, '[断言] 文件上传失败!'
        assert res[0]['description'] == description, '[断言] 文件上传失败!'
        logger.info('[断言] 文件上传成功 数据库验证')

    def download_file(self, save_path):
        """ 下载文件 """
        logger.info('下载文件开始')
        file_path = self.expect_download('first_file_name', save_path=save_path)
        logger.info(f'下载文件结束, 文件路径为: {file_path}')

    def assert_download_file(self):
        """ 断言下载文件成功 """
        assert pathlib.Path(self.last_file_download_path).exists(), '[断言] 文件下载失败!'
        self.wait_for_timeout(500)
        pathlib.Path(self.last_file_download_path).unlink()
        logger.info('[断言] 文件下载成功')
    

if __name__ == '__main__':

    from playwright.sync_api import sync_playwright

    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    context.tracing.start(snapshots=True, sources=True, screenshots=True)
    page = context.new_page()

    # 将 Page 对象存储在全局管理器中
    GlobalManager().set_value('page', page)

    from PageObject.p04_pw_gjgl.pw_web_login_page import LoginPage
    LoginPage().login('test01', '1111')
    ap = FilePage()
    ap.create_folder(name='创建文件夹', description='创建文件夹描述')
    ap.upload_file(rename='is_renamee.txt', description='qweqweqweqweqwe', file_path=r"D:\文件上传下载\666666.txt")
    ap.download_file(save_path=r"D:\文件上传下载")
    ap.assert_download_file()
    # ap.assert_upload_file_page(rename='sdf.txt', description='qweqweqweqweqwe')

    # ap.assert_upload_file_databases(rename='rerere', description='rererer')

