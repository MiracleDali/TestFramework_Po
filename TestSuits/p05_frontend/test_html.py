import time
from Base.baseData import DataDriver
from PageObject.p05_frontend.frontend_html import FrontendHtml


class TestFrontendHtml():
    """ 前端学习之html测试 """
    def test_html_case01(self):
        """ 测试html笔记的主页面 """
        fh = FrontendHtml()
        res = fh.get_html_page()
        fh.assert_html_page(res)