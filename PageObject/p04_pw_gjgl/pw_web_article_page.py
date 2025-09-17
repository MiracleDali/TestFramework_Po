import sys
import pathlib
import time

Base = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.append(str(Base))

from ExtTools.dbbase import MysqlHelp
from Base.basePath import BasePath as BP
from Base.utils import read_config_ini
from Base.baseAutoWebPw import WebBase
from Base.baseContainer import GlobalManager
from Base.baseLogger import Logger

logger = Logger(r'PageObject/p04_pw_test/pw_web_login_page.py').getLogger()


class ArticlePage(WebBase):
    def __init__(self):
        # 传入 yaml 文件名以便 WebBase 在构造时加载元素数据
        super().__init__(yaml_name='02稿件管理元素信息')
        self.config = read_config_ini(BP.CONFIG_FILE)

    def add_article(self, title, content):
        """ 添加稿件 """
        logger.info('添加稿件开始')
        self.click('add_article_btn')
        self.wait_for_timeout(1000)
        self.fill('title', title)

        logger.info('进入iframe')
        # 使用 with 自动退出 frame
        with self.frame_context(selector='add_iframe'):
            # 在这个 with 块中，self._current_frame 已经被设置为对应 Frame
            # 下面所有 self.locator(...) / self.fill(...) 都会在该 frame 上执行
            # self.fill('content', content)
            self.wait_for_timeout(1000)
        logger.info('退出iframe')

        # 保存
        self.wait_for_timeout(1000)
        self.click('save')
        self.wait_for_timeout(1000)
        # 查询
        self.click('select_btn')
        logger.info('添加稿件结束')
    

if __name__ == '__main__':

    from playwright.sync_api import sync_playwright

    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    context.tracing.start(snapshots=True, sources=True, screenshots=True)
    page = context.new_page()

    # 将 Page 对象存储在全局管理器中
    GlobalManager().set_value('page', page)

    from PageObject.p04_pw_gjgl.pw_web_login_page import LoginPage
    LoginPage().login('test01', '1111')
    ap = ArticlePage()
    ap.add_article('测试添加稿件', '测试添加稿件')
