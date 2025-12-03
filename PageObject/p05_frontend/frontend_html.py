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
        """ 稿件新增 """
        res = self.request_base(api_name='home_api')
        return res.text
    


if __name__ == '__main__':
    fh = FrontendHtml()
    res = fh.get_html_page()
    print(res)
    
