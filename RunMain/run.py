import os
import sys

# 将项目根路径添加到系统环境路径中
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # 项目根目录
sys.path.append(PROJECT_ROOT)

import pytest
from Base.basePath import BasePath as BP
from Base.utils import read_config_ini, file_all_dele
from Base.baseContainer import GlobalManager
from Base.baseSendEmail import HandleEmail
from Base.baseSendNginx import SendNginx


config = read_config_ini(BP.CONFIG_FILE)
gm = GlobalManager()
gm.set_value('CONFIG_INFO', config)
gm.set_value('DATA_DIRVER_PATH', os.path.join(BP.DATA_DRIVER_DIR, config['项目运行设置']['DATA_DRIVER_TYPE']))


def run_main():
    """ 运行主函数 """
    # 运行配置
    run_config = gm.get_value('CONFIG_INFO')['项目运行设置']
    # 用例完整路径
    test_case = os.path.join(BP.TEST_SUITE_DIR, run_config['TEST_PROJECT'])

    if run_config['REPORT_TYPE'] == 'ALLURE':
        pytest.main(['-sv', f'--alluredir={BP.ALLURE_RESULT}', test_case])
        os.system(f'allure generate {BP.ALLURE_RESULT} -o {BP.ALLURE_REPORT} --clean')
        file_all_dele(BP.ALLURE_RESULT)

    elif run_config['REPORT_TYPE'] == 'HTML':
        report_path = os.path.join(BP.HTML_DIR, 'auto_report.html')
        pytest.main(['-sv', f'--html={report_path}', '--self-contained-html', test_case])

    elif run_config['REPORT_TYPE'] == 'XML':
        report_path = os.path.join(BP.XML_DIR, 'auto_report.xml')
        pytest.main(['-sv', f'--junitxml={report_path}', test_case])
    else:
        print(f'暂不支持{run_config["REPORT_TYPE"]}报告类型')

    if run_config['IS_EMAIL'] == 'yes':
        print(66)
        el = HandleEmail()
        text = 'test_无需回复, 以下为本次测试报告'
        print(f'{run_config["REPORT_TYPE"]}')
        el.send_public_email(text=text, filetype=run_config['REPORT_TYPE'])



if __name__ == '__main__':
    run_main()
    SendNginx().send_report()
    


# import pytest
# pytest.main(['-sv', 
#              r'--alluredir=d:\2_python_file\TestFramework_Po\Result', 
#              r'd:\2_python_file\TestFramework_Po\TestSuits\project02'])
