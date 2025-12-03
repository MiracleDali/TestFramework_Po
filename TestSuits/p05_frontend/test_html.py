import time
from Base.baseData import DataDriver
from PageObject.p05_frontend.frontend_html import FrontendHtml


class TestFrontendHtml():
    """ 前端学习之html测试 """
    def test_html_case01(self):
        fh = FrontendHtml()
        res = fh.get_html_page()