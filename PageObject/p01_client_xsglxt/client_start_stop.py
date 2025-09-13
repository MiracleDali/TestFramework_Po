import sys
import time
from pathlib import Path
# 获取当前文件的父目录的父目录（项目根目录）
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from ExtTools.dbbase import Sqlite3Tools
from ExtTools.sysbase import SysOperation
from Base.baseAutoClient import GuiBase
from Base.baseLogger import Logger
logger = Logger('PageObject/p01_client_xsglxt/client_start_stop.py').getLogger()



class ClientPage(GuiBase):
    def __init__(self):
        super().__init__()
        self.client_path = r"D:\2_python_file\manage_system\program"
        self.exe_path = Path(self.client_path).joinpath("main.exe")
        self.db_path = Path(self.client_path).joinpath("student.db")
        self.sys = SysOperation()
        self.sqllite = Sqlite3Tools(database=self.db_path)

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
        """ 断言登录 """
        if flag == 'student':
            time.sleep(1)
            assert self.is_exist('loginok_student')
            logger.info(f"学生账号登录成功")
        elif flag == 'teacher':
            assert self.is_exist('loginok_teacher')
            logger.info(f"教师账号登录成功")

    
    def client_student_register(self, name, age, username, password):
        """ 学生注册 """
        self.click_picture('zhuce_btn')
        time.sleep(1)
        self.rel_picture_click('zhuce_name', rel_x=200)
        self.input_string(name)
        self.rel_picture_click('zhuce_age', rel_x=200)
        self.write_type(age)
        self.rel_picture_click('zhuce_student_number', rel_x=200)
        self.write_type(username)
        self.rel_picture_click('zhuce_password', rel_x=200)
        self.write_type(password)
        self.click_picture('zhuce_commit')

    def assert_register_success(self, name):
        """ 断言注册成功 """
        # 界面断言
        assert self.is_exist('zhuce_success'), '[断言]: 学生注册断言失败!'
        logger.info(f"[断言]: 学生注册断言成功!")
        self.click_picture('zhuce_queding')

        # 验证数据库
        sql = f"select student_name from student_info where student_name = '{name}';"
        print(sql)
        res = self.sqllite.sqlite3_db_query(sql)
        # if not res:
        #     raise Exception(f'[断言]: 数据库内无 {name} 该信息')
        assert res[0]['student_name'] == name, '[断言]: 数据库学生注册断言失败!'
        logger.info(f"[断言]: 数据库学生注册断言成功!")

        # 数据清除
        sql = f"delete from student_info where student_name = '{name}';"
        self.sqllite.sqlite3_db_operate(sql)
        
 

if __name__ == '__main__':
    client = ClientPage()
    client.start_client()

    client.client_login('201901010105', '123')
    # client.close_client()

    # time.sleep(2)
    # client.client_student_register('小甜甜', '18', '201901010107', '123')
    # client.assert_register_success('小甜甜')

    client.close_client()
