"""
# file:     Base/baseAutoWeb.py
# WEB自动化
"""

import sys
from pathlib import Path
# 获取当前文件的父目录的父目录（项目根目录）
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from Base.baseData import DataBase
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from Base.baseLogger import Logger

logger = Logger('Base/baseAutoWeb.py').getLogger()


class WebBase(DataBase):
    """ WEB自动化基类 """

    def __init__(self, yaml_name):
        super().__init__(yaml_name)
        self.driver = self.gm.get_value('driver')
        self.t = 0.5   # 元素显示等待最小时间
        self.timeout = 10  # 元素显示等待最大时间

    def get_locator_data(self, locator, change_data=None):
        """
        获取元素数据
        param: change_data: 是否修改yaml数据
        param: locator: (login/password)-->yaml文件的层级
        """
        res = self.get_element_data(change_data)  # 读取到的yaml文件信息
        # print(res)
        items = locator.split('/')  # 吧传进来的字符串，使用 / 分割成列表 --> ["login", "username"]
        # print(items)
        # print([items[0]])
        locator_data = tuple(res[items[0]][items[1]])
        return locator_data

    def find_element(self, locator, change_data=None):
        """
        元素定位方法，返回元素对象
        """
        try:
            locator = self.get_locator_data(locator, change_data)
            if not isinstance(locator, tuple):
                logger.error('locator_data 参数类型错误，必须为元组类型 loc = ("name", "66_login")')

            logger.info(f"正在定位元素，定位方式-->{locator[0]}, value值-->{locator[1]}")
            ele = WebDriverWait(self.driver, self.timeout, self.t).until(EC.presence_of_element_located(locator))
            logger.info(f"元素定位成功，元素信息-->{locator}")
            return ele
        except Exception as e:
            logger.error('未定位到元素', locator)
            raise e

    def find_elements(self, locator, change_data=None):
        """
        多个元素定位
        元素定位方法，返回元素对象
        """
        try:
            locator = self.get_locator_data(locator, change_data)
            if not isinstance(locator, tuple):
                logger.error('locator_data 参数类型错误，必须为元组类型 loc = ("name", "66_login")')

            logger.info(f"正在定位元素，定位方式-->{locator[0]}, value值-->{locator[1]}")
            ele = WebDriverWait(self.driver, self.timeout, self.t).until(EC.presence_of_all_elements_located(locator))
            logger.info(f"元素定位成功，元素信息-->{locator}")
            return ele
        except Exception as e:
            logger.error('未定位到元素', locator)
            raise e

    def get_url(self, url):
        """ 打开url连接&最大化窗口 """
        self.driver.get(url)
        self.driver.maximize_window()
        logger.debug(f"浏览器访问请求地址-->{url}")


    def click(self, locator, change_data=None):
        """ 点击元素 """
        try:
            ele = self.find_element(locator, change_data)
            ele.click()
            logger.info(f"点击元素-->{locator},成功")
        except Exception as e:
            logger.error(f'点击元素-->{locator},失败')
            raise e

    def clear(self, locator, change_data=None):
        """ 清空输入框 """
        try:
            ele = self.find_element(locator, change_data)
            ele.clear()
            logger.info(f"清空输入框-->{locator},成功")
        except Exception as e:
            logger.error(f'清空输入框-->{locator},失败')
            raise e

    def send_keys(self, locator, text='', change_data=None):
        """ 输入内容 """
        try:
            ele = self.find_element(locator, change_data)
            ele.send_keys(text)
            logger.info(f"输入内容-->{text},成功")
        except Exception as e:
            logger.error(f'输入内容-->{text},失败')
            raise e



    def get_title(self):
        """ 获取页面标题 """
        try:
            title = self.driver.title
            logger.info(f"获取页面 title-->{title},成功")
            return title
        except Exception as e:
            logger.error(f'获取页面title,失败', e)
            return ''

    def get_text(self, locator, change_data=None):
        """ 获取元素文本 """
        try:
            content = self.find_element(locator, change_data).text
            logger.info(f"获取元素文本-->{content},成功")
            return content
        except Exception as e:
            logger.error(f'获取元素文本,失败', e)
            return ''

    def get_attribute(self, locator, attribute, change_data=None):
        """ 获取元素属性 """
        try:
            content = self.find_element(locator, change_data).get_attribute(attribute)
            logger.info(f"获取元素属性-->{attribute},成功")
            return content
        except Exception as e:
            logger.error(f'获取元素属性,失败', e)
            return ''


    def isSelected(self, locator, change_data=None):
        """ 判断元素是否被选中 返回bool值 """
        ele = self.find_element(locator, change_data)
        return ele.is_selected()

    def is_title(self, _title=''):
        """ 判断页面标题是否与预期一致 """
        try:
            result = WebDriverWait(self.driver, self.timeout, self.t).until(EC.title_is(_title))
            return result
        except Exception as e:
            return False

    def is_title_contains(self, _title=''):
        """ 验证页面标题是否包含预期字符串 """
        try:
            result = WebDriverWait(self.driver, self.timeout, self.t).until(EC.title_contains(_title))
            return result
        except Exception as e:
            return False

    def is_text_in_element(self, locator, _text='', change_data=None):
        """ 验证元素文本是否与预期一致 """
        try:
            locator = self.get_locator_data(locator, change_data)
            result = WebDriverWait(self.driver, self.timeout, self.t).until(EC.text_to_be_present_in_element(locator, _text))
            return result
        except Exception as e:
            return False

    def is_value_in_element(self, locator, _value='', change_data=None):
        """ 验证元素属性值是否与预期一致 """
        try:
            locator = self.get_locator_data(locator, change_data)
            result = WebDriverWait(self.driver, self.timeout, self.t).until(EC.text_to_be_present_in_element_value(locator, _value))
            return result
        except Exception as e:
            return False

    def is_alert(self, timeout=3):
        """ 判断弹窗是否在页面内 """
        try:
            result = WebDriverWait(self.driver, timeout, self.t).until(EC.alert_is_present())
            return result
        except Exception as e:
            return False, logger.error('未定位到弹窗', e)

    def mouse_move_to(self, locator, change_data=None):
        """ 鼠标悬停 """
        try:
            ele = self.find_element(locator, change_data)
            ActionChains(self.driver).move_to_element(ele).perform()
            logger.info(f"鼠标悬停元素-->{locator},成功")
        except Exception as e:
            logger.error(f'鼠标悬停元素-->{locator},失败')
            raise e

    def mouse_drag_to(self, locator, x_offset, y_offset, change_data=None):
        """ 鼠标拖拽到 指定坐标 """
        element = self.find_element(locator, change_data)
        ActionChains(self.driver).drag_and_drop_by_offset(element, x_offset, y_offset).perform()
        logger.info(f"鼠标拖拽元素-->{locator},成功")

    def js_focus_element(self, locator, change_data=None):
        """ js聚焦元素  滑轮滚动 """
        target = self.find_element(locator, change_data)
        self.driver.execute_script("arguments[0].scrollIntoView();", target)
        logger.info(f"聚焦元素-->{locator},成功")

    def js_scroll_end(self):
        """ js 滚动到底部 """
        js = "window.scrollTo(0,document.body.scrollHeight)"
        self.driver.execute_script(js)
        logger.info(f"滚动到底部,成功")

    def js_scroll_top(self):
        """ js 滚动到顶部 """
        js = "window.scrollTo(0,0)"
        self.driver.execute_script(js)
        logger.info(f"滚动到顶部,成功")

    def keyboard_send_keys_to_element(self, locator, text, change_data=None):
        """ 键盘输入 """
        element = self.find_element(locator, change_data)
        ActionChains(self.driver).send_keys_to_element(element, text).perform()
        logger.info(f"键盘在{locator}位置输入-->{text},成功")


    def get_alert_text(self):
        """ 获取弹窗文本 """
        try:
            text = self.driver.switch_to.alert.text
            logger.info(f"获取弹窗文本-->{text},成功")
            return text
        except Exception as e:
            logger.error(f'获取弹窗文本,失败')
            raise e

    def alert_accept(self):
        """ 点击接受弹窗 """
        try:
            self.driver.switch_to.alert.accept()
            logger.info(f"接受弹窗,成功")
        except Exception as e:
            logger.error(f'接受弹窗,失败')
            raise e

    def alert_dismiss(self):
        """ 点击取消弹窗 """
        try:
            self.driver.switch_to.alert.dismiss()
            logger.info(f"取消弹窗,成功")
        except Exception as e:
            logger.error(f'取消弹窗,失败')
            raise e

    def input_alert_text(self, text):
        """ 输入弹窗文本 """
        try:
            self.driver.switch_to.alert.send_keys(text)
            logger.info(f"输入弹窗文本-->{text},成功")
        except Exception as e:
            logger.error(f'输入弹窗文本,失败')
            raise e

    def select_by_index(self, locator, index=0, change_data=None):
        """ 通过索引选择 """
        element = self.find_element(locator, change_data)
        Select(element).select_by_index(index)
        logger.info(f"通过索引选择下拉列表下拉索引-->{index},成功")

    def select_by_value(self, locator, value, change_data=None):
        """ 通过value值选择 """
        element = self.find_element(locator, change_data)
        Select(element).select_by_value(value)
        logger.info(f"通过value值选择下拉列表下拉索引-->{value},成功")

    def select_by_text(self, locator, text, change_data=None):
        """ 通过文本选择 """
        element = self.find_element(locator, change_data)
        Select(element).select_by_visible_text(text)
        logger.info(f"通过文本选择下拉列表下拉索引-->{text},成功")

    def switch_iframe(self, locator, change_data=None):
        """ 切换iframe """
        try:
            id_index_locator = self.get_locator_data(locator, change_data)
            if isinstance(id_index_locator, int):
                self.driver.switch_to.frame(id_index_locator)
            elif isinstance(id_index_locator, str):
                self.driver.switch_to.frame(id_index_locator)
            elif isinstance(id_index_locator, tuple) or isinstance(id_index_locator, list):
                ele = self.find_element(locator)
                self.driver.switch_to.frame(ele)
            logger.info(f"切换iframe-->{locator},成功")
        except Exception as e:
            logger.error(f'切换iframe-->{locator},失败', e)

    def switch_iframe_out(self):
        """ 退出iframe """
        try:
            self.driver.switch_to.default_content()
            logger.info(f"退出iframe,成功")
        except Exception as e:
            logger.error(f'退出iframe,失败', e)

    def switch_iframe_up(self):
        """ 切换到上一层iframe """
        try:
            self.driver.switch_to.parent_frame()
            logger.info(f"切换到上一层iframe,成功")
        except Exception as e:
            logger.error(f'切换到上一层iframe,失败', e)


    def get_handles(self):
        """ 获取所有窗口句柄 """
        try:
            handles = self.driver.window_handles
            logger.info(f"获取所有窗口句柄-->{handles},成功")
            return handles
        except Exception as e:
            logger.error(f'获取所有窗口句柄,失败', e)

    def switch_handle(self, index=-1):
        """ 切换窗口句柄 """
        try:
            handle_list = self.driver.window_handles
            self.driver.switch_to.window(handle_list[index])
            logger.info(f"切换窗口句柄-->{index},成功")
        except Exception as e:
            logger.error(f'切换窗口句柄-->{index},失败', e)






if __name__ == '__main__':
    from selenium import webdriver
    option = webdriver.ChromeOptions()
    # 避免浏览器闪退
    option.add_experimental_option("detach", True)
    # 创建浏览器对象 打开浏览器
    driver = webdriver.Chrome(options=option)  
    
    from Base.baseContainer import GlobalManager
    gm  = GlobalManager()
    gm.set_value('driver', driver)


    wb = WebBase('01登陆页面元素信息页面')
    wb.get_url('https://www.baidu.com')