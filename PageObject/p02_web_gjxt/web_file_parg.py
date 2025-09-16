import sys
from pathlib import Path
import time

Base_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(Base_dir))

from Base.basePath import BasePath as BP
from Base.utils import read_config_ini
from Base.baseAutoWeb import WebBase
from Base.baseLogger import Logger
from ExtTools.dbbase import MysqlHelp

logger = Logger(r'PageObject\p02_web_gjxt\web_file_parg.py').getLogger()

class FilePage(WebBase):
    def __init__(self):
        super().__init__('03文件上传下载')


    def add_folder(self, name, description):
        """ 创建文件夹 """
        logger.info('创建文件夹开始')
        self.click('file/file_page')
        time.sleep(1)
        self.click('file/new_folder_btn')
        time.sleep(1)
        self.clear('file/folder_name')
        self.send_keys('file/folder_name', name)
        self.send_keys('file/folder_desc', description)
        self.click('file/save_folder')
        logger.info('创建文件夹结束')

    
    def assert_add_folder_page(self, name):
        """ 断言文件夹添加成功 """
        assert self.get_text('file/first_naem') == name, '[断言] 文件夹添加失败'
        logger.info('[断言] 文件夹添加成功')


    def assert_add_folder_database(self, name, description):
        """ 断言数据库中添加的文件夹 """
        db = MysqlHelp()
        sql = f'select name, description from dlfolder where name = {name} and description = {description}  order by createDate desc;'
        result = db.mysql_db_select(sql)
        assert result[0]['name'] == name, '[断言] 数据库中没有该文件夹'
        assert result[0]['description'] == description, '[断言] 描述不一致'
        logger.info('[断言] 数据库中添加文件夹成功')


    def delete_folder(self):
        """ 删除文件夹 """
        logger.info('删除文件夹开始')
        self.click('file/file_page')
        time.sleep(1)
        self.click('file/first_delete_btn')
        self.is_alert().accept()
        logger.info('删除文件夹结束')

    def assert_delete_folder_page(self):
        """ 断言文件夹删除页面 """
        assert self.get_text('file/delete_masige_success') == '您的请求执行成功。', '[断言] 文件夹删除失败'
        logger.info('[断言] 文件夹删除成功')





if __name__ == '__main__':

    from selenium import webdriver
    # 避免浏览器闪退
    option = webdriver.ChromeOptions()
    option.add_experimental_option("detach", True)
    # 创建浏览器对象 打开浏览器
    driver = webdriver.Chrome(options=option)

    from Base.baseContainer import GlobalManager
    gm  = GlobalManager()
    gm.set_value('driver', driver)

    from PageObject.p02_web_gjxt.web_login_page import LoginPage
    login_page = LoginPage()
    login_page.login('test01', '1111')


    fp = FilePage()
    fp.add_folder('测试文件夹', '测试文件夹描述')
    fp.assert_add_folder_page('测试文件夹')
    fp.delete_folder()