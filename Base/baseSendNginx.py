"""
# file:     Base/baseSendNginx.py
"""

import sys
from pathlib import Path
# 获取当前文件的父目录的父目录（项目根目录）
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

import os
import time
from Base.baseLogger import Logger
from Base.basePath import BasePath as BP
from Base.utils import read_config_ini
import subprocess


logger = Logger('Base/baseSendNginx.py').getLogger()


class SendNginx(object):
    """
    # 发送报告到nginx
    """
    def __init__(self):
        """ 获取本地报告路径以及远程nginx配置 """
        self.local_allure_report = BP.ALLURE_REPORT
        self.local_html_report = os.path.join(BP.HTML_DIR, 'auto_report.html')

        config = read_config_ini(BP.CONFIG_FILE)
        nginx_conf = config['nginx配置']
        self.nginx_host = nginx_conf['host']
        self.nginx_user = nginx_conf['user']
        self.nginx_passwd = nginx_conf['passwd']
        self.nginx_port = nginx_conf['port']
        self.nginx_allure_path = nginx_conf['allure_path']
        self.nginx_html_path = nginx_conf['html_path']

        self.send_or_not = config['项目运行设置']['SEND_REPORT_NG']
        self.report_type = config['项目运行设置']['REPORT_TYPE']


    def start_send(self, cmd):
        """ 报告发送实现 """
        try:
            logger.info(f'common: {cmd}')
            process = subprocess.Popen(cmd,  # 输入的cmd命令
                             shell=True,  # 通过操作系统的 shell 执行指定的命令
                             stdout=subprocess.PIPE,  # 将结果标准输出
                             stderr=subprocess.PIPE)  # 将标准错误输出
            stdout, stderr = process.communicate()
            if process.returncode != 0:
                logger.error(f'发送失败: {stderr.decode().strip()}')
            elif process.returncode == 0:
                logger.info(f'报告发送成功')
        except Exception as e:
            logger.error(f'启动命令失败: {e}')
        except FileNotFoundError:
            logger.error(f'请检查nginx配置文件路径是否正确')

    def send_allure(self, timestamp):
        """ 发送allure报告 """
        if os.path.isdir(self.local_allure_report):
            # 为allure报告目录添加时间戳
            allure_dir_name = os.path.basename(self.local_allure_report.rstrip('/'))
            timed_allure_dir = f"{allure_dir_name}_{timestamp}"
            remote_allure_path = os.path.join(os.path.dirname(self.nginx_allure_path), timed_allure_dir)

            logger.info(f'allure 报告存在准备发送到nginx: {self.local_allure_report}')
            self.start_send(f'scp '
                            # f'-v '  # （verbose模式）查看详细交互过程
                            f'-r '
                            f'-P {self.nginx_port} '
                            f'-o ConnectTimeout=10 '  # 连接阶段超时（TCP握手）
                            f'-o PreferredAuthentications=publickey '  # 认证公钥
                            f'-o ServerAliveInterval=30 '  # 每30秒发送一次存活包
                            f'-o ServerAliveCountMax=3 '  # 最大存活检测次数
                            f'{self.local_allure_report} '
                            f'{self.nginx_user}@{self.nginx_host}:{remote_allure_path}')
        else:
            logger.info(f'{self.local_allure_report} 报告不存在')

    def send_html(self, timestamp):
        """ 发送html报告 """
        if os.path.isfile(self.local_html_report):
            html_filename = os.path.basename(self.local_html_report)
            name, ext = os.path.splitext(html_filename)
            timed_html_filename = f"{name}_{timestamp}{ext}"
            remote_html_path = os.path.join(os.path.dirname(self.nginx_html_path), timed_html_filename)

            logger.info(f'html 报告存在开始发送到nginx: {self.local_html_report}')
            self.start_send(f'scp '
                            # f'-v '  # （verbose模式）查看详细交互过程
                            f'-r '
                            f'-P {self.nginx_port} '
                            f'-o ConnectTimeout=10 '  # 连接阶段超时（TCP握手）
                            f'-o PreferredAuthentications=publickey '  # 认证公钥
                            f'-o ServerAliveInterval=30 '  # 每30秒发送一次存活包
                            f'-o ServerAliveCountMax=3 '  # 最大存活检测次数
                            f'{self.local_html_report} '
                            f'{self.nginx_user}@{self.nginx_host}:{remote_html_path}')
        else:
            logger.info(f'{self.local_html_report} 报告不存在')


    def send_report(self):
        """ 判断报告类型 """
        if self.send_or_not == 'no':
            logger.info(f'本次测试不发送报告到nginx')
            return

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        if self.report_type == 'ALLURE':
            self.send_allure(timestamp)

        elif self.report_type == 'HTML':
            self.send_html(timestamp)
        else:
            logger.info(f'暂不支持发送该类型报告:{self.report_type}')



if __name__ == '__main__':
    example = SendNginx()
    example.send_report()

