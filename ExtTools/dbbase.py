import pymysql
import sqlite3
from dbutils.pooled_db import PooledDB


class MysqlHelp(object):
    """ mysql 数据库操作 """
    # 类属性，共享连接池
    _pool = None
    
    def __init__(self, host, user, passwd, port, database):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.port = int(port)
        self.database = database
        
        # 初始化连接池
        if MysqlHelp._pool is None:
            MysqlHelp._pool = PooledDB(
                creator=pymysql,
                maxconnections=5,  # 连接池最大连接数
                mincached=2,       # 初始化时创建的连接数
                host=self.host,
                user=self.user,
                passwd=self.passwd,
                port=self.port,
                db=self.database,
                charset='utf8',
                use_unicode=True
            )
    
    def get_connection(self):
        """ 从连接池获取连接 """
        return MysqlHelp._pool.connection()

    def mysql_db_select(self, sql):
        """ 查询数据库 """
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql)
                result_set = cursor.fetchall()
            return result_set
        except Exception as e:
            print(f'查询错误: {e}')
            return None
        finally:
            conn.close()  # 实际将连接返回连接池

    def mysql_db_operate(self, sql):
        """ 数据库 增删改 操作 """
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql)
                conn.commit()
        except Exception as e:
            conn.rollback()
            print(f'操作错误: {e}')
        finally:
            conn.close()  # 实际将连接返回连接池



class Sqlite3Tools():
    """ sqlite3数据库操作 """
    def __init__(self, database=''):
        self.database = database
        self.connection = None

    def dict_factory(self, cursor, row):
        # 将查询结果转换成字典
        # self.connection.row_factory = self.dict_factory 返回的是元组列表
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def create_connection(self):
        """ 创建数据库连接 """
        try:
            self.connection = sqlite3.connect(self.database)
            self.connection.row_factory = self.dict_factory
        except Exception as e:
            print(e)
            print('数据库连接失败')

    def sqlite3_db_query(self, sql):
        """ 查询 """
        try:
            self.create_connection()
            cur = self.connection.cursor().execute(sql)
            result_set = cur.fetchall()
            return result_set
        except Exception as e:
            print(e)
            print('查询失败')
        finally:
            self.connection.close()

    def sqlite3_db_operate(self, sql):
        """ 增删改 """
        try:
            self.create_connection()
            self.connection.cursor().execute(sql)
            self.connection.commit()
        except Exception as e:
            print(e)
            print('操作失败')
            self.connection.rollback()
        finally:
            self.connection.close()

