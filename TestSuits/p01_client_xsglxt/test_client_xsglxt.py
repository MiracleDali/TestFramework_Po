import pytest

from Base.baseData import DataDriver
from PageObject.p01_client_xsglxt.client_start_stop import ClientPage
from PageObject.p01_client_xsglxt.client_teacher_page import TeacherPage
from PageObject.p01_client_xsglxt.client_student_page import StudentPage


class TestClientCase1():
    """ 客户端自动化-学生管理系统 登陆注册模块"""

    @pytest.mark.parametrize('case_data', DataDriver().get_case_data('01学生管理系统登录'))
    @pytest.mark.usefixtures("init_client")
    def test_login_case01(self, case_data):
        """ 客户端自动化用例-用户登录 """
        cp = ClientPage()
        cp.client_login(case_data['username'], case_data['password'])
        cp.assert_login_success(case_data['flag'])


    @pytest.mark.parametrize('case_data', DataDriver().get_case_data('02学生管理系统注册'))
    @pytest.mark.usefixtures("init_client")
    def test_register_case02(self, case_data):
        """ 客户端自动化-学生管理系统-学生注册 """
        cp = ClientPage()
        cp.client_student_register(case_data['name'], case_data['age'], case_data['username'], case_data['password'])
        print(666666666, case_data['name'])
        cp.assert_register_success(case_data['name'])


     
class TestClientCase02:
    """ 客户端自动化-学生管理系统 老师账号功能模块"""
    @pytest.mark.usefixtures("init_client", "teacher_login")
    def test_report_case01(self):
        """ 客户端自动化用例-查看学生报告 """
        tp = TeacherPage()
        tp.client_teacher_report()
        tp.asset_report()

    @pytest.mark.parametrize('case_data', DataDriver().get_case_data('03学生管理系统修改'))
    @pytest.mark.usefixtures('init_client', 'teacher_login')
    def test_thacher_edit_case02(self, case_data):
        """ 测试老师编辑学生成绩 """
        tp = TeacherPage()
        tp.clint_teacher_edit(case_data['num'], case_data['score'])
        tp.assert_edit_success(case_data['num'], case_data['score'])

    @pytest.mark.usefixtures('init_client', 'teacher_login')
    def test_teacher_export_case03(self):
        """ 测试老师导出学生成绩单数据 """
        tp = TeacherPage()
        tp.clinet_teacher_export()
        tp.assert_teacher_export_success()



class TestStudentCase03:
    """ 客户端自动化-学生管理系统-学生账号功能模块 """
    @pytest.mark.usefixtures('init_client', 'student_login')
    def test_student_report_case01(self):
        """ 测试学生查看成绩单功能 """
        sp = StudentPage()
        sp.client_student_report()
        sp.assert_stduent_report()


    @pytest.mark.parametrize('new_password', DataDriver().get_case_data('04学生管理系统密码修改'))
    @pytest.mark.usefixtures('init_client', 'student_login')
    def test_student_change_password_case02(self, new_password):
        """ 测试学生修改密码功能 """
        sp = StudentPage()
        sp.client_student_change_password(new_password['newpsw'])
        sp.assert_change_password_success(new_password['newpsw'])

    @pytest.mark.usefixtures('init_client', 'student_login')
    def test_student_export_case03(self):
        """ 测试学生导出功能 """
        sp = StudentPage()
        sp.client_student_export()
        sp.assert_student_export_success()

        



