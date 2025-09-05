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
from playwright.sync_api  import Page 


config = read_config_ini(BP.CONFIG_FILE)
gm = GlobalManager()
gm.set_value('CONFIG_INFO', config)
insert_js_html = False


# #  打开不同的浏览器
# def pytest_addoption(parser):
#     """添加命令行参数 --selenium_browser 和 --host"""
#     parser.addoption(
#         "--selenium_browser",
#         action="store",
#         default=config['WEB自动化配置']['selenium_browser'],
#         help="指定 Selenium 浏览器驱动类型: 'firefox', 'chrome' 或 'edge'"
#     )
#     parser.addoption(
#         "--host",
#         action="store",
#         default=config['项目运行设置']['TEST_URL'],
#         help="指定测试主机地址，例如: http://127.0.0.1"
#     )


@pytest.fixture(scope='function')
def driver(request):
    try:
        name = request.config.getoption("--selenium_browser")

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



####################################################################################################
############  html 报告配置
"""
pytest -v --html=report.html  --self-contained-html --capture=sys 
#: -v: 显示详细测试信息
#: --html=report.html: 生成HTML报告
#: --self-contained-html: 确保生成的HTML报告是自包含的,即不依赖于外部资源
#: --capture=sys: 确保所有print输出都能在报告中显示
"""

# 标题配置（测试前）
def pytest_html_report_title(report):
    print('生成HTML报告')
    report.title  = f"自动化测试报告 - {datetime.now().strftime('%Y-%m-%d  %H:%M')}"

# 环境信息配置（测试前）
def pytest_metadata(metadata):
    """直接通过 metadata 字典添加环境信息"""
    metadata.update({ 
        "测试项目": "zzy_exercise",
        "测试环境": "STAGING",
        "执行节点": "Jenkins Slave-02"
    })



####################################################################################################
############  失败截图

def _capture_screenshot_sel(): 
    """
    selenium 截图
    Args: 
        driver: selenium driver
    Returns: base64编码的PNG图片字符串 
    # SCREENSHOT_PIC
    """
    # 下面这段是seleuinm 的截图方法
    driver = GlobalManager().get_value('driver')
    if not driver:
        pytest.exit("driver 获取为空")
    driver.get_screenshot_as_file(BP.SCREENSHOT_PIC)
    return driver.get_screenshot_as_base64()
    

def _capture_screenshot_pil():
    """客户端 截图"""
    try:
        from PIL import ImageGrab
        output_buffer = BytesIO()
        img = ImageGrab.grab()
        img.save(BP.SCREENSHOT_PIC)
        img.save(output_buffer, 'png')
        bytes_value = output_buffer.getvalue()  
        output_buffer.close()
        return base64.b64encode(bytes_value).decode()
    except ImportError:
        pytest.exit('请安装PIL模块')


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item):
    """ 测试用例执行失败, 截图到报告 """
    outcome = yield
    pytest_html = item.config.pluginmanager.getplugin('html')
    report = outcome.get_result()
    extra = getattr(report, 'extra', [])

    # 判断当前用例的执行状态
    if report.when == 'call' or report.when == 'setup':
        xfail = hasattr(report, 'wasxfail')
        # 判断自动化测试类型
        if config['项目运行设置']['AUTO_TYPE'] == 'WEB':
            screen_ing = _capture_screenshot_sel()  # web 截图方法
        elif config['项目运行设置']['AUTO_TYPE'] == 'CLIENT':
            screen_ing = _capture_screenshot_pil()  # PIL 截图方法
        else:
            sereen_img = None

        if (report.skipped and xfail) or (report.failed and not xfail) and screen_ing:
            file_name = report.nodeid.replace("::", "_") + ".png"

            if config['项目运行设置']['REPORT_TYPE'] == 'HTML' and file_name:
                html = '<div><img src="Data:image/png;base64,%s" alt="screenshot" style="width:600px;height:300px;" ' \
                       'onclick="lookimg(this.src)" align="right"/></div>' % screen_ing
                script = '''
                <script>
                    function lookimg(str)
                    {
                        var newwin=window.open();
                        newwin.document.write("<img src="+str+" />");
                    }
                </script> 
                '''
                extra.append(pytest_html.extras.html(html))
                if not insert_js_html:
                    extra.append(pytest_html.extras.html(script))
            
            elif config['项目运行设置']['REPORT_TYPE'] == 'ALLURE':
                import allure
                with allure.step('添加失败用例截图...'):
                    allure.attach.file(BP.SCREENSHOT_PIC, '失败用例截图', allure.attachment_type.PNG)

    report.extra = extra
    report.description = str(item.function.__doc__)




####################################################################################################
############  收集所有用例并记录到临时yaml文件中  BP.TEMP_CASES
############  以便让 pyside6 读取用例

import pytest
from collections import defaultdict
def pytest_collection_modifyitems(session, config, items):
    """收集用例后修改"""
    if config.getoption("--co"):  # 判断是否使用了 --co
        testcases = defaultdict(dict)

        for item in items:
            # 获取 类名 + 方法名
            parts = item.nodeid.split("::")
            case_class_name = "::".join(parts[0:2])
            case_name = parts[-1]

            if "comment" not in testcases[case_class_name]:
                # 获取类的 docstring
                testcases[case_class_name]["comment"] = getattr(item.cls, "__doc__", "")

            # 获取方法的 docstring
            testcases[case_class_name][case_name] = getattr(item.function, "__doc__", "")

        # 循环结束后一次性写入文件
        tempcases_path = BP.TEMP_CASES
        write_yaml(tempcases_path, dict(testcases))

    
