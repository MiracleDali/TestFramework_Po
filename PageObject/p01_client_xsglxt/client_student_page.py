import os
import sys
import time
from pathlib import Path

# 获取当前文件的父目录的父目录（项目根目录）
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from PageObject.p01_client_xsglxt.client_start_stop import ClientPage
from Base.baseLogger import Logger
logger = Logger('PageObject/p01_client_xsglxt/client_teacher_page.py').getLogger()



class StudentPage(ClientPage):
    def __init__(self):
        super().__init__()
        

    def client_student_report(self):
        """ 获取成绩单 """
        try:
            self.click_picture('student_report_btn')
            time.sleep(1)
            logger.info('点击获取成绩单按钮')
        except Exception as e:
            logger.exception('按钮点击失败', e)

    def assert_stduent_report(self):
        """ 断言获取成绩单成功 """
        assert self.is_exist('student_report_ok'), '[断言]：获取成绩单失败'
        logger.info('查看个人成绩单成功')


    def client_student_change_password(self, new_password):
        """ 学生修改密码 """
        self.click_picture('student_change_passwd_btn')
        time.sleep(1)
        self.rel_picture_click('student_change_new_passwd', rel_x=100)
        self.write_type(new_password)
        self.rel_picture_click('student_change_queren_new_passwd', rel_x=100)
        self.write_type(new_password)
        self.click_picture('student_queren_change')
        
    
    def assert_change_password_success(self, new_password):
        """ 断言学生修改密码成功 """
        assert self.is_exist('student_change_passwd_succeed'), '[断言]修改密码失败'
        logger.info('[断言]修改密码成功')

        sql = f'SELECT student_passworld FROM student_info WHERE student_passworld = "{new_password}"'
        res = self.sqllite.sqlite3_db_query(sql)[0]['student_passworld']
        assert res == new_password, '[断言]修改密码失败'
        logger.info('[断言]数据库验证修改密码成功')

        # 把密码在更新回去
        sql = f'UPDATE student_info SET student_passworld = "123" WHERE student_number = "201901010103"'
        self.sqllite.sqlite3_db_operate(sql)


    def client_student_export(self):
        """ 学生信息导出 """
        self.click_picture('student_export')
        logger.info('点击导出按钮')

    def assert_student_export_success(self):
        """ 断言学生信息导出成功 """
        assert self.is_exist('student_export_succeed'), '[断言]学生信息导出失败'
        logger.info('[断言]学生信息导出成功')

        res = os.listdir(self.client_path)
        assert '201901010103_student_achievement.xls' in res, '[断言]学生信息导出失败'
        logger.info('[断言]学生信息导出成功')

        Path(self.client_path).joinpath('201901010103_student_achievement.xls').unlink()

    
if __name__ == '__main__':
    cp = ClientPage()
    cp.start_client()
    # time.sleep(2)
    cp.client_login('201901010103', '123')

    sp = StudentPage()
    sp.client_student_export()
    sp.assert_student_export_success()

    # cp.close_client()