import os
import sys
import argparse
# 将项目根路径添加到系统环境路径中
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # 项目根目录
sys.path.append(PROJECT_ROOT)
import pytest
from Base.basePath import BasePath as BP
from Base.utils import read_config_ini, file_all_dele
from Base.baseContainer import GlobalManager
from Base.baseSendEmail import HandleEmail
from Base.baseSendNginx import SendNginx
from Base.baseLogger import Logger

logger = Logger('run.py').getLogger()


config = read_config_ini(BP.CONFIG_FILE)
gm = GlobalManager()
gm.set_value('CONFIG_INFO', config)
gm.set_value('DATA_DIRVER_PATH', os.path.join(BP.DATA_DRIVER_DIR, config['项目运行设置']['DATA_DRIVER_TYPE']))


def run_main(markexpr=None):
    """ 运行主函数 """
    # 运行配置
    run_config = gm.get_value('CONFIG_INFO')['项目运行设置']
    # 用例完整路径
    test_case = os.path.join(BP.TEST_SUITE_DIR, run_config['TEST_PROJECT'])

    # 构建基础参数
    pytest_args = ['-vs', test_case]

    # 如果传入 marker 参数，则添加 marker 参数
    if markexpr and markexpr.strip():
        pytest_args.extend(['-m', markexpr.strip()])
        logger.info(f"执行标记为 '{markexpr}' 的测试用例")
    else:
        logger.info("执行所有测试用例")

    # 根据报告类型添加不同参数
    if run_config['REPORT_TYPE'] == 'ALLURE':
        pytest_args.extend(['--alluredir', BP.ALLURE_RESULT])
        pytest.main(pytest_args)
        os.system(f'allure generate {BP.ALLURE_RESULT} -o {BP.ALLURE_REPORT} --clean')
        file_all_dele(BP.ALLURE_RESULT)

    elif run_config['REPORT_TYPE'] == 'HTML':
        report_path = os.path.join(BP.HTML_DIR, 'auto_report.html')
        pytest_args.extend([f'--html={report_path}', '--self-contained-html'])
        pytest.main(pytest_args)

    elif run_config['REPORT_TYPE'] == 'XML':
        report_path = os.path.join(BP.XML_DIR, 'auto_report.xml')
        pytest_args.extend([f'--junitxml={report_path}'])
        pytest.main(pytest_args)
    else:
        print(f'暂不支持{run_config["REPORT_TYPE"]}报告类型')

    if run_config['IS_EMAIL'] == 'yes':
        el = HandleEmail()
        text = 'test_无需回复, 以下为本次测试报告'
        print(f'{run_config["REPORT_TYPE"]}')
        el.send_public_email(text=text, filetype=run_config['REPORT_TYPE'])

    # 发送报告->nginx
    SendNginx().send_report()


def parse_arguments():
    """ 解析命令行参数 """
    parser = argparse.ArgumentParser(description='添加用例标签')
    parser.add_argument('-m',
                        '--markexpr',
                        type=str,
                        help='pytest标记表达式，例如 "smoke" 或 "smoke or ui"，不传则执行所有用例')
    return parser.parse_args()


if __name__ == '__main__':
    # 解析命令行参数
    args = parse_arguments()
    # 调用运行主函数
    run_main(markexpr=args.markexpr)
    

"""
运行命令
python run.py                        # 运行所有用例
python run.py -m smoke               # 运行标记为 "smoke" 的用例
python run.py -m "smoke or ui"       # 运行标记为 "smoke" 或 "ui" 的用例
python run.py -m "not smoke"         # 运行标记不为 "smoke" 的用例
python run.py -m "(smoke or api) and not slow"    # 运行标记为 "smoke" 或 "api"，且不包含 "slow" 的用例
"""

