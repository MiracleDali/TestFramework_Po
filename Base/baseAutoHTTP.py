"""
# file:     Base/baseAutoHTTP.py
# HTTP自动化
"""

import sys
from pathlib import Path
# 获取当前文件的父目录的父目录（项目根目录）
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
print(sys.path)

import requests
import urllib3
from requests import session

from Base.baseData import DataBase
from Base.baseLogger import Logger
from urllib3.exceptions import InsecureRequestWarning
from urllib.parse import urljoin

logger = Logger('Base/baseAutoHTTP.py').getLogger()

class ApiBase(DataBase):
    """ 接口自动化基类 """

    # 创建session--会话保持器
    session = requests.session()

    def __init__(self, yaml_name):
        super().__init__(yaml_name)
        self.timeout = 10

    def request_base(self,api_name, change_data=None, **kwargs):
        """ 通用接口请求 """
        try:
            logger.info(f'{self.yaml_name}-{api_name}:接口调用开始')
            yaml_data = self.get_element_data(change_data)[api_name]
            # print(yaml_data)

            yaml_data['url'] = urljoin(self.run_config['TEST_URL'], yaml_data['url'])

            logger.info(f'获取【{self.yaml_name}】文件【{api_name}】接口请求数据：{yaml_data}')
            logger.info(f'接口请求方式为：{yaml_data["method"]}')
            logger.info(f'接口请求URL为：{yaml_data["url"]}')
            if 'data' in yaml_data.keys():
                logger.info(f'接口请求数据为：{yaml_data["data"]}')
            elif 'json' in yaml_data.keys():
                logger.info(f'接口请求数据为：{yaml_data["json"]}')

            # 禁用安全请求警告
            urllib3.disable_warnings(InsecureRequestWarning)
            # res = requests.request(method = yaml_data['method'],
            #                        url = yaml_data['url'],
            #                        headers=yaml_data['headers'])
            # 等同上面
            res = ApiBase.session.request(**yaml_data, **kwargs)

            logger.info(f'接口响应时间为：{res.elapsed.total_seconds()}')
            logger.debug(f'接口响应状态码为：{res.status_code}')
            logger.debug(f'接口响应体数据为：{res.text}')
            logger.info(f'{self.yaml_name}-{api_name}:接口调用结束')
            return res

        except Exception as e:
            logger.error('接口请求失败', e)


if __name__ == '__main__':
    api = ApiBase('接口元素信息登陆')
    api.request_base('home_api')