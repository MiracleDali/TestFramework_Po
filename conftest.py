"""
测试用例执行前的初始化
"""

import base64
import pytest
import pytest_html
from datetime import datetime
from io import BytesIO
from Base.utils import *
from Base.basePath import BasePath as BP
from Base.baseContainer import GlobalManager
from Base.baseYaml import write_yaml
from selenium import webdriver


config = read_config_ini(BP.CONFIG_FILE)
gm = GlobalManager()
gm.set_value('CONFIG_INFO', config)


#  打开不同的浏览器
def pytest_addoption(parser):
    """ 添加命令行参数 --browser， --host """
    parser.addoption(
        "--browser", action="store",
        default=config['WEB自动化配置']['browser'],
        help="browser option: firefox or chrome or Edge")

    parser.addoption(
        "--host", action="store",
        default=config['项目运行设置']['TEST_URL'],
        help="host option: http://127.0.0.1-->选择项目运行主机")

@pytest.fixture(scope='function')
def driver(request):
    try:
        name = request.config.getoption("--browser")

        _driver = None
        if name == 'firefox':
            _driver = webdriver.Firefox()
        elif name == 'Edge':
            _driver = webdriver.Edge()
        elif name == 'chrome':
            _driver = webdriver.Chrome()
        elif name == 'chromeheadless':
            options = webdriver.ChromeOptions()
            options.add_argument('headless')
            _driver = webdriver.Chrome(options=options)

        GlobalManager().set_value('driver', _driver)

        _driver.implicitly_wait(5)
        print(f'正在打开 【{name}】 浏览器')

        def fu():
            print('当全部用例执行完成后，关闭浏览器')
            _driver.quit()
        request.addfinalizer(fu)

        return _driver


    except ImportError:
        pytest.exit("请安装selenium依赖包")
    except Exception as e:
        pytest.exit("启动webdriver错误", e)




# 给HTML报告添加一下信息
def pytest_html_report_title(report):
    report.title = "My very own title!"

def pytest_html_results_summary(prefix, summary, postfix):
    """ Summary部分在这里设置 """
    prefix.extend([
        "<p>测试组：测试开发组 -->  测试人员: tester</p>"
        ])

def pytest_html_results_table_header(cells):
    cells.insert(1,  "<p>Description</p>")
    cells.pop() 


# def pytest_html_results_table_row(report, cells):
#     if hasattr(report, "description"):
#         cells.insert(2, f"<td>{report.description}</td>")
#         cells.pop()
#     else:
#         print("!!!!!!!!",report.longreprtext)



# 失败用例截图 -- 重写钩子函数来实现截图  -- 添加到html报告
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    pytest_html = item.config.pluginmanager.getplugin('html')
    report = outcome.get_result()
    extra = getattr(report, 'extra', [])

    

