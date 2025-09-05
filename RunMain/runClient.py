import os
import sys
import pathlib
# 获取项目根目录添加到环境变量
PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

import pytest
import multiprocessing
import ctypes
from contextlib import contextmanager
from Base.baseContainer import GlobalManager
from Base.baseSendEmail import HandleEmail
from Base.baseGuiRan import run
from Base.basePath import BasePath as BP
from Base.utils import read_config_ini, file_all_dele
from Base.baseYaml import read_yaml


config = read_config_ini(BP.CONFIG_FILE)
gm = GlobalManager()
gm.set_value('CONFIG_INFO', config)
run_config = gm.get_value('CONFIG_INFO')['项目运行设置']


@contextmanager
def output_to_null():
    f = open(os.devnull, 'w')
    saved_stdout = sys.stdout
    sys.stdout = f
    yield
    sys.stdout = saved_stdout
    f.close()

def run_collect_testcase(v):
    with output_to_null():
        try:
            test_pj = pathlib.Path(BP.TEST_SUITE_DIR).joinpath(run_config['TEST_PROJECT']).resolve()
            res = pytest.main(['-sv', '-q', '--co', test_pj])
        except Exception as e:
            sys.exit('用例收集发送错误', e)
    
    if res == 0:
        v.value = True
        print("收集用例成功, 生成用例集 testcases.yaml")

def run_main():
    try:
        datas = read_yaml(BP.TEST_CASES)
        testcases = []
        if not datas:
            print("未选择任何用例")
            return
        for module in datas.keys():
            for key in datas[module]:
                if key == "comment":
                    continue
                testcase = key
                testcase = os.path.join(BP.PROJECT_ROOT, module) + "::" + testcase
                testcases.append(testcase)
        
        # 生成报告
        if run_config['REPORT_TYPE'] == 'ALLURE':
            pytest.main(['-sv', f'--alluredir={BP.ALLURE_RESULT}', *testcases])
            os.system(f'allure generate {BP.ALLURE_RESULT} -o {BP.ALLURE_REPORT} --clean')
            file_all_dele(BP.ALLURE_RESULT)
        elif run_config['REPORT_TYPE'] == 'HTML':
            report_path = os.path.join(BP.HTML_DIR, 'auto_report.html')
            pytest.main(['-sv', f'--html={report_path}', '--self-contained-html', *testcases])
        elif run_config['REPORT_TYPE'] == 'XML':
            report_path = os.path.join(BP.XML_DIR, 'auto_report.xml')
            pytest.main(['-sv', f'--junitxml={report_path}', *testcases])
        else:
            print(f'暂不支持{run_config["REPORT_TYPE"]}报告类型')
        
        # 邮件发送
        if run_config['IS_EMAIL'] == 'yes':
            el = HandleEmail()
            text = 'test_无需回复, 以下为本次测试报告'
            el.send_public_email(text=text, filetype=run_config['REPORT_TYPE'])
            print(f'邮件发送成功{run_config["REPORT_TYPE"]}')

    except FileNotFoundError as e:
        print("无用例文件, 执行testsuits 目录下的用例")
        test_case = os.path.join(BP.TEST_SUITE_DIR, run_config['TEST_PROJECT'])
        pytest.main(['-sv', f'--alluredir={BP.ALLURE_RESULT}', test_case])
        os.system(f'allure generate {BP.ALLURE_RESULT} -o {BP.ALLURE_REPORT} --clean')
        file_all_dele(BP.ALLURE_RESULT)

def run_app(name, *args):
    app = multiprocessing.Process(target=name, args=args)
    app.start()
    app.join()


if __name__ == '__main__':
    manager = multiprocessing.Manager()
    v = manager.Value(ctypes.c_bool, False)
    print("用例正在加载...")

    run_app(run_collect_testcase, v)
    if not v.value:
        sys.exit()
    run_app(run)
    run_main()

