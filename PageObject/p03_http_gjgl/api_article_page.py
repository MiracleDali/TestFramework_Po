import sys
import pathlib
Base_dir = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.append(str(Base_dir))
import re
from Base.baseAutoHTTP import ApiBase
from Base.baseLogger import Logger
from ExtTools.dbbase import MysqlHelp
import time
logger = Logger('PageObject/p03_http_gjgl/api_article_page.py').getLogger()

class ApiArticle(ApiBase):

    def __init__(self):
        super().__init__(yaml_name='02稿件管理接口信息')

    def add_article(self, title, content):
        """ 稿件新增 """
        change_data = {
            '_15_title': title,
            '_15_content': content
        }
        res = self.request_base(api_name='add_api_article', change_data=change_data)
        return res.text

    def search_article(self, title=''):
        """ 稿件查询接口 """
        change_data = {
            '_15_keywords': title
        }
        res = self.request_base(api_name='search_api', change_data=change_data)
        re_info = re.findall('_15_version=1.0">(.*?)</a>', res.text)[:7]
        return re_info
    
    def assert_search_article(self, res, title):
        """ 稿件查询断言 """
        assert res[1] == title, '[断言] 验证稿件查询失败'
        logger.info('[断言] 验证稿件查询成功')

    def assert_search_article_database(self, title):
        """ 稿件查询数据库断言 """
        db = MysqlHelp()
        sql = f'select title, content, approved from  journalarticle where title = "{title}"'
        res = db.mysql_db_select(sql)
        assert res[0]['title'] == title, f'[断言] 稿件查询数据库查询失败: {title}'
        assert res[0]['approved'] == 0, f'[断言] 稿件新增数据库查询失败: {res[0]['approved']}'
        logger.info('[断言] 稿件查询数据库查询成功')


    def assert_add_article(self, title):
        """ 稿件新增断言 """
        res_info = self.search_article()
        # print(res_info, 6666666666666666666)
        # logger.info(f'{res_info}, 6666666666666666666')
        assert res_info[1] == title, '[断言] 稿件新增接口查询失败'
        assert res_info[3] == '不批准', '[断言] 稿件新增接口查询失败'
        logger.info('[断言] 稿件新增接口查询成功')

    def assert_add_article_databases(self, title, content):
        """ 稿件新增数据库断言 """
        db = MysqlHelp()
        sql = 'select title, content, approved from  journalarticle order by createDate desc limit 1'
        res = db.mysql_db_select(sql)
        # print(res)
        assert res[0]['title'] == title, f'[断言] 稿件新增数据库查询失败: {title}'
        assert content in res[0]['content'], f'[断言] 稿件新增数据库查询失败: {content}'
        assert res[0]['approved'] == 0, f'[断言] 稿件新增数据库查询失败: {res[0]['approved']}'
        logger.info('[断言] 稿件新增数据库查询成功')


    def delete_article(self, title):
        """ 稿件删除 """
        # 查询稿件
        id = self.search_article(title)[0]
        change_data = {
            '_15_deleteArticleIds': f'{id}_version_1.0',
            '_15_rowIds': f'{id}_version_1.0'
        }
        res = self.request_base(api_name='delete_article', change_data=change_data)
        logger.info('稿件删除结束')
        return res.text
        
    def assert_delete_article(self, title):
        """ 稿件删除断言 """
        res_info = self.search_article(title)
        assert res_info == [], '[断言] 稿件删除接口查询失败'
        logger.info('[断言] 稿件删除接口查询成功')

    def assert_delete_article_databases(self, title):
        """ 稿件删除数据库断言 """
        db = MysqlHelp()
        # sql = 'select title, content, approved from  journalarticle order by createDate desc limit 1'
        sql = f'select count(*) from  journalarticle where title = "{title}"'
        res = db.mysql_db_select(sql)
        assert res[0]['count(*)'] == 0, '[断言] 稿件删除数据库查询失败'
        logger.info('[断言] 稿件删除数据库查询成功')
 

    def edit_article(self, title, edit_title, edit_content):
        """ 稿件修改 """
        id = self.search_article(title)[0]
        change_data = {
            '_15_articleId': id,
            '_15_content': edit_content,
            '_15_deleteArticleIds': f'{id}_version_1.0',
            '_15_expireArticleIds': f'{id}_version_1.0',
            '_15_title': edit_title
        }
        res = self.request_base(api_name='edit_article', change_data=change_data)
        return res.text


if __name__ == '__main__':
    from PageObject.p03_http_gjgl.api_login_page import LoginPage
    lp = LoginPage()
    lp.login('test01', '1111')

    api = ApiArticle()
    # res = api.add_article('测试新增稿件1', '测试新增稿件内容1')
    # api.search_article(title='测试新增稿件1')
    # api.assert_add_article('测试新增稿件1')
    # api.assert_add_article_databases('测试新增稿件1', '测试新增稿件内容1')
    # time.sleep(2)
    # api.delete_article('测试新增稿件1')
    # api.assert_delete_article('测试新增稿件1')
    # api.assert_delete_article_databases('测试新增稿件1')

    api.edit_article('666668888', 'editedit', 'editedittest')