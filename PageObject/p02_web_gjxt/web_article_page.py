import sys
from pathlib import Path
import time

Base_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(Base_dir))

from Base.basePath import BasePath as BP
from Base.utils import read_config_ini
from Base.baseAutoWeb import WebBase
from Base.baseLogger import Logger
from ExtTools.dbbase import MysqlHelp

logger = Logger(r'PageObject\p02_web_gjxt\web_article_page.py').getLogger()


class ArticlePage(WebBase):
    def __init__(self):
        super().__init__('02稿件管理元素信息')

    def add_article(self, title, content):
        """ 添加稿件 """
        logger.info('添加稿件开始')
        self.click('article/add_article_btn')
        time.sleep(1)
        self.send_keys('article/title', title)
        # 切换到iframe
        self.switch_iframe('article/add_iframe')
        # self.send_keys('article/content', content)
        # 退出iframe
        self.switch_iframe_out()
        # 保存
        time.sleep(1)
        self.click('article/save')
        time.sleep(1)
        # 查询
        self.click('article/select_btn')
        logger.info('添加稿件结束')
  
    def assert_article_add_success(self, title):
        """ 断言稿件添加成功 """
        logger.info('断言添加稿件成功开始')
        assert self.get_text('article/first') == title, '[断言] 标题断言 添加稿件失败！'
        logger.info('[断言] 标题断言 添加稿件成功结束')
        assert self.get_text('article/state') == '不批准', '[断言] 状态断言 添加稿件失败！'
        logger.info('[断言]  状态断言 添加稿件成功结束')

    def assert_add_database(self, title):
        """ 添加稿件-数据库断言 """
        logger.info('断言 添加稿件-数据库断言')
        dbInfo = self.config['mysql连接配置']
        db = MysqlHelp(dbInfo['host'], dbInfo['user'], dbInfo['passwd'], dbInfo['port'], dbInfo['database'])
        res = db.mysql_db_select("select title, content, approved, createDate  from  journalarticle order by createDate desc limit 1;")
        print(res[0]['title'])
        assert res[0]['title'] == title, '[断言] 标题断言 添加稿件失败！'
        # assert content in res[0]['content'], '[断言] 内容断言 添加稿件失败！'
        logger.info('[断言] 添加稿件成功-数据库断言结束')


    def delete_article(self):
        """ 删除稿件 """
        logger.info('删除稿件开始')
        # 查询稿件
        self.click('article/select_btn')
        time.sleep(1)
        # 勾选
        self.click('article/cleck')
        time.sleep(1)
        # 删除
        self.click('article/delete_btn')
        # 弹窗确定
        time.sleep(1)
        self.is_alert().accept()
        time.sleep(2)

    def assert_delete_page_article(self, title):
        """ 断言 页面删除稿件成功 """
        logger.info('断言 删除稿件是否成功，开始')
        assert self.get_text('article/first') != title, '[断言] 删除稿件失败！'
        logger.info('[断言] 删除稿件成功')

    def assert_delete_database_article(self, title):
        """ 断言 删除稿件-数据库断言 """
        logger.info('断言 删除稿件-数据库断言, 开始')
        db = MysqlHelp()
        sql = f"select count(*) from journalarticle where title = '{title}';"
        res = db.mysql_db_select(sql)
        assert int(res[0]['count(*)']) == 0, '[断言] 删除稿件-数据库断言失败！'
        logger.info('[断言] 删除稿件-数据库断言成功-结束')

    def edit_article(self, title):
        """ 修改稿件 """
        logger.info('修改稿件开始')
        self.click('article/first_article')
        time.sleep(1)
        self.clear('article/title')
        self.send_keys('article/title', text=title)
        # 切换到iframe
        self.switch_iframe('article/add_iframe')
        # self.clear('article/content')
        # self.send_keys('article/content', '这是修改后的内容')
        self.switch_iframe_out()
        self.click('article/save')
        logger.info('修改稿件结束')


    def search_article(self, title):
        """ 搜索稿件 """
        logger.info('搜索稿件开始')
        self.clear('article/search_input')  # 清空输入框
        self.send_keys('article/search_input', title)
        self.click('article/select_btn')
        time.sleep(1)
        logger.info('搜索稿件结束')

    def assert_search_article(self, title):
        """ 断言 搜索稿件 """
        logger.info('断言 搜索稿件，开始')
        assert self.get_text('article/first') == title, '[断言] 搜索稿件失败！'
        logger.info('[断言] 搜索稿件成功-结束')

    def assert_search_article_database(self, title):
        """ 搜索稿件-数据库断言 """
        logger.info('断言 搜索稿件-数据库断言，开始')
        db = MysqlHelp()
        sql = f"select title from journalarticle where title = '{title}';"
        res = db.mysql_db_select(sql)
        assert res[0]['title'] == title, '[断言] 搜索稿件-数据库断言失败！'
        logger.info('[断言] 搜索稿件-数据库断言成功-结束')


    
    


if __name__ == '__main__':

    from selenium import webdriver
    # 避免浏览器闪退
    option = webdriver.ChromeOptions()
    option.add_experimental_option("detach", True)
    # 创建浏览器对象 打开浏览器
    driver = webdriver.Chrome(options=option)

    from Base.baseContainer import GlobalManager
    gm  = GlobalManager()
    gm.set_value('driver', driver)

    from PageObject.p02_web_gjxt.web_login_page import LoginPage
    login_page = LoginPage()
    login_page.login('test01', '1111')

    article = ArticlePage()
    article.add_article('这是测试标题', '这是测试内容')
    # article.assert_article_add_success('这是测试标题')
    # article.assert_add_database('这是测试标题')
    # article.delete_article()
    # article.assert_delete_page_article('这是测试标题')
    # article.assert_delete_database_article('这是稿8件1')

    # article.edit_article('这是修改后的标题')

    # 查询稿件
    article.search_article('这是测试标题')
    # article.assert_search_article('这是测试标题')
