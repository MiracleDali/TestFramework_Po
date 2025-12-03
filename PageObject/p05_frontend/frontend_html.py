-- Active: 1761479637360@@192.168.198.128@3306
import sys
import pathlib
Base_dir = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.append(str(Base_dir))
from Base.baseAutoHTTP import ApiBase
from Base.baseLogger import Logger
import time
logger = Logger(r'PageObject\p05_frontend\frontend_html.py').getLogger()


class FrontendHtml(ApiBase):
    """ 前端HTML页面 """
    def __init__(self):
        super().__init__(yaml_name='01html')

    def get_html_page(self):
        """ 访问页面 """
        res = self.request_base(api_name='home_api')
        return res.text
    
    def assert_html_page(self, res):
        """ 1_html页面断言 """
        logger.info('[断言] html页面断言开始')
        assert res.find('<title>Index of /Frontend/1_HTML/</title>') != -1, '[断言] html页面断言失败'
        logger.info('[断言] html页面断言成功')

        
    


if __name__ == '__main__':
    fh = FrontendHtml()
    res = fh.get_html_page()
    fh.assert_html_page(res)   
    
