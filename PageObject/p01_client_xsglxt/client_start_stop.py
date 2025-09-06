import sys
import time
from pathlib import Path
# 获取当前文件的父目录的父目录（项目根目录）
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from ExtTools.sysbase import SysOperation
from Base.baseAutoClient import GuiBase
from Base.baseLogger import Logger
logger = Logger('PageObject/client_start_stop.py').getLogger()



class ClientPage(GuiBase):
    def __init__(self):
        super().__init__()
        self.client_path = r"E:\学浪课程配套_pytest框架\02项目实战\学生管理系统\客户端程序"
        self.exe_path = Path(self.client_path).joinpath("main.exe")
        self.db_path = Path(self.client_path).joinpath("student.db")
        self.sys = SysOperation()

    def start_client(self):
        """ 启动客户端 """
        self.sys.popen_cmd(f'E: & cd {self.client_path} && start {self.exe_path}')
        logger.info(f'启动客户端成功')

    def close_client(self):
        """ 关闭客户端 """
        self.sys.popen_cmd(f'cd {self.client_path} && taskkill /f /t /im main.exe')
        logger.info(f'关闭客户端成功')

    def client_login(self, username, password):
        """ 客户端登录 """
        # 1.输入学号
        self.rel_picture_click('login_studnum', rel_x=150)
        self.write_type(username)
        logger.info(f"输入学号成功:{username}")
        # 2.输入密码
        self.rel_picture_click('login_password', rel_x=150)
        self.write_type(password)
        logger.info(f"输入密码成功:{password}")
        # 3.点击登录
        self.click_picture('login_stuteach_btn')

    def assert_login_success(self, flag):
        """ 断言登录成功 """
        if flag == 'student':
            time.sleep(1)
            assert self.is_exist('loginok_student')
            logger.info(f"学生账号登录成功")
        elif flag == 'teacher':
            assert self.is_exist('loginok_teacher')
            logger.info(f"教师账号登录成功")



if __name__ == '__main__':
    client = ClientPage()
    client.start_client()
    # client.client_login('201901010103', '123')
    # client.close_client()

