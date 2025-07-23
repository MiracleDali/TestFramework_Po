"""
# file:     Base/baseSendEmail.py
# 发送邮件
"""


import sys
from pathlib import Path
# 获取当前文件的父目录的父目录（项目根目录）
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
# print(sys.path)

from datetime import datetime
import os
import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# 假设 BasePath 和相关函数已经定义
from Base.basePath import BasePath as BP
from Base.utils import read_config_ini, make_zip


class HandleEmail(object):
    def __init__(self):
        """
        初始化邮件发送配置
        """
        config = read_config_ini(BP.CONFIG_FILE)
        email_config = config['邮件发送配置']

        self.host = email_config['host']
        self.port = int(email_config['port'])
        self.sender = email_config['sender']
        self.send_email = email_config['send_email']
        self.receiver = eval(email_config['receiver'])
        self.pwd = email_config['pwd']
        self.subject = email_config['subject']

    def add_text(self, text):
        """ 添加文本 """
        return MIMEText(text, 'plain', 'utf-8')

    def add_html_text(self, html):
        """ 添加html """
        return MIMEText(html, 'html', 'utf-8')

    def add_accessory(self, file_path):
        """ 添加附件, 图片, txt, pdf, zip """
        res = MIMEText(open(file_path, 'rb').read(), 'base64', 'utf-8')
        res.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file_path))
        return res

    def add_subject_attach(self, attach_info: tuple, send_date=None):
        """ 添加主题, 发件人, 收件人 """
        msg = MIMEMultipart('mixed')
        msg['Subject'] = Header(self.subject, 'utf-8')
        msg['From'] =  f"{Header(self.sender,  'utf-8').encode()} <{self.send_email}>"
        msg['To'] = ','.join(self.receiver)

        if send_date:
            """ 是否指定日期 """
            msg['Date'] = send_date
        else:
            msg['Date'] = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')

        if isinstance(attach_info, tuple):
            for i in attach_info:
                msg.attach(i)
        return msg

    def send_email_oper(self, msg):
        """ 发送邮件 """
        try:
            # 使用 SMTP_SSL
            smtp = smtplib.SMTP_SSL(self.host, port=self.port)
            smtp.login(self.send_email, self.pwd)
            smtp.sendmail(self.send_email, self.receiver, msg.as_string())
            print("{}给{}发送邮件成功，发送时间：{}".format(self.send_email, self.receiver,
                                                          datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')))
            smtp.quit()
        except Exception as e:
            print(f"发送邮件失败: {e}")

    def send_public_email(self, send_date=None, text='', html='', filetype='HTML'):
        """ 发送邮件-公共方法 """
        attach_info = []
        text_plain = self.add_text(text=text)
        attach_info.append(text_plain)
        if html:
            text_html = self.add_html_text(html=html)
            attach_info.append(text_html)
        elif filetype == 'ALLURE':
            allure_zip = make_zip(BP.ALLURE_REPORT, os.path.join(BP.ALLURE_REPORT, 'allure.zip'))
            file_attach = self.add_accessory(file_path=allure_zip)
            attach_info.append(file_attach)
        elif filetype == 'HTML':
            file_attach = self.add_accessory(file_path=os.path.join(BP.HTML_DIR, 'auto_report.html'))
            attach_info.append(file_attach)
        elif filetype == 'XML':
            file_attach = self.add_accessory(file_path=os.path.join(BP.XML_DIR, 'auto_report.xml'))
            attach_info.append(file_attach)

            # 添加主题和附件信息到msg
        attach_info = tuple(attach_info)
        msg = self.add_subject_attach(attach_info=attach_info, send_date=send_date)

        #  发送邮件
        self.send_email_oper(msg=msg)


if __name__ == '__main__':
    text = 'test_无需回复， 以下为本次测试报告'
    HandleEmail().send_public_email(send_date=None, text=text, html='', filetype='HTML')


















