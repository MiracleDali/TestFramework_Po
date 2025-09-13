import os
import sys
import time
from pathlib import Path

# 获取当前文件的父目录的父目录（项目根目录）
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from ExtTools.dbbase import Sqlite3Tools
from Base.baseAutoClient import GuiBase
from PageObject.p01_client_xsglxt.client_start_stop import ClientPage
from Base.baseLogger import Logger
logger = Logger('PageObject/p01_client_xsglxt/client_teacher_page.py').getLogger()


class TeacherPage(ClientPage):
    def __init__(self):
        super().__init__()


    def client_teacher_report(self):
        """ teacher check report """
        self.click_picture('teacher_report_btn')
        time.sleep(1)
        self.click_picture('teacher_down')
        time.sleep(0.5)
        self.click_picture('teacher_math')
        time.sleep(0.5)
        self.rel_picture_click('teacher_desc', rel_x=-20)
        self.click_picture('teacher_report')

    def asset_report(self):
        """ asset 成绩单 """
        assert self.is_exist('teacher_title'), '[断言失败]: 未打开查询单'
        logger.info('[断言成功]: 打开学生成绩查询单成功' )
        assert self.is_exist('teacher_ok_report'), '[断言失败]: 成绩单降序排列断言失败'
        logger.info('[断言成功]: 成绩单降序排列成功' )

    def clint_teacher_edit(self, student_number, score):
        """ 老师修改学生成绩信息 """
        self.click_picture('teache_edit_report_btn')
        time.sleep(1)
        self.click_picture('teacher_edit_down')
        time.sleep(1)
        self.click_picture('teache_edit_physics')
        self.rel_picture_click('teache_edit_student_number', rel_x=100)
        self.write_type(student_number)
        self.rel_picture_click('teache_edit_score', rel_x=100)
        self.press('backspace') 
        self.write_type(score)
        self.click_picture('teache_edit_commit')

    def assert_edit_success(self, student_number, score):
        """ 断言修改成功 """
        # 客户端断言
        assert self.is_exist('teache_edit_ok'), '[断言] 修改学生成绩单失败失败'
        logger.info('[断言] 修改学生成绩单成功')

        # 数据库断言
        sql = f"select 物理 from student_achievement where student_number = '{student_number}'"
        res = self.sqllite.sqlite3_db_query(sql)[0].get('物理')
        # print(res, int(score))
        assert res == int(score), '[断言] 修改学生成绩单成功'
        logger.info(f'[断言] 数据库修改学生成绩单成功: {score}')

    
    def clinet_teacher_export(self):
        """ 导出成绩单 """
        try:
            self.click_picture('teacher_report_btn')    
        except Exception as e:
            logger.exception(f'[错误] {e}')
        time.sleep(1)
        self.click_picture('teache_export_btn')
        time.sleep(1)

    def assert_teacher_export_success(self):
        """ 断言导出成功 """
        assert self.is_exist('teache_export_ok'), '[断言]：导出失败'
        logger.info('[断言]：导出成功')

        files = os.listdir(self.client_path)
        assert '语文排序成绩.xls' in files, '[断言]：导出失败'
        logger.info('[断言]：导出成功本地存在')

        Path(self.client_path).joinpath('语文排序成绩.xls').unlink()




if __name__ == '__main__':
    client = ClientPage()
    client.start_client()
    client.client_login('123', '123')
    
    teacher = TeacherPage()
    # teacher.client_teacher_report()
    
    # teacher.clint_teacher_edit('201901010106', '99')
    # teacher.assert_edit_success('201901010106', '99')

    teacher.clinet_teacher_export()
    teacher.assert_teacher_export_success()

    client.close_client()


    