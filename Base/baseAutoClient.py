"""
# file:     Base/baseAutoClient.py
# 客户端自动化
# -封装（图片）定位、点击、相对位置点击方法
# -封装（鼠标）点击、移动、拖拽、滑轮滚动
# -封装（键盘）输入长文本、单个按键操作、组合按键操作
"""

import sys
from pathlib import Path
# 获取当前文件的父目录的父目录（项目根目录）
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
# print(sys.path)

import time
import pyautogui
import pyperclip   # 用于复制粘贴
from Base.baseData import DataBase
from Base.baseLogger import Logger
from Base.basePath import BasePath as Bp

logger = Logger('Base/baseAutoClient.py').getLogger()

class GuiBase(DataBase):
    """
    客户端自动化
    -封装（图片）定位、点击、相对位置点击方法
    -封装（鼠标）点击、移动、拖拽、滑轮滚动
    -封装（键盘）输入长文本、单个按键操作、组合按键操作
    """
    def __init__(self):
        super().__init__()
        self.duration = float(self.config['客户端自动化配置']['duration'])
        self.interval = float(self.config['客户端自动化配置']['interval'])
        self.minSearchTime = float(self.config['客户端自动化配置']['minSearchTime'])
        self.confidence  = float(self.config['客户端自动化配置']['confidence'])
        self.grayscale = bool(self.config['客户端自动化配置']['grayscale'])

    def _is_file_exist(self, el):
        """ 判断文件是否存在 """
        abs_path = self.api_path.get(el)
        # print(abs_path)
        if not abs_path:
            logger.debug(f"文件不存在，请检查文件名，或者配置文件核对项目路径: {el}")
            raise FileNotFoundError(f"文件不存在，请检查文件名，或者配置文件核对项目路径: {el}")
        return abs_path

    def is_exist(self, el, search_time=None):
        """ 检查图片是否在屏幕上 """
        pic_path = self._is_file_exist(el)
        if not search_time:
            search_time = self.minSearchTime
        try:
            # 获取图片坐标（返回 Box 对象）
            coordinates = pyautogui.locateOnScreen(
                pic_path,
                minSearchTime=search_time,
                confidence=self.confidence,
                grayscale=self.grayscale
            )
            if coordinates:
                logger.debug(f"{el}图片对象在屏幕上")
                # 将 Box 转换为标准元组并确保使用 Python 原生 int
                box_tuple = (
                    int(coordinates.left),
                    int(coordinates.top),
                    int(coordinates.width),
                    int(coordinates.height)
                )
                return pyautogui.center(box_tuple)
        except pyautogui.ImageNotFoundException:
            logger.debug(f"{el}图片对象不在屏幕上")
        return None

    @staticmethod
    def _error_record(el, type_name):
        """ 错误截图 """
        time_str = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
        pyautogui.screenshot(f"{Bp.SCREENSHOT_DIR}/{time_str}_{el}.png")
        logger.error(f"方法：{type_name}，查找图片{el}位置，当前屏幕无此内容，以截屏")
        raise pyautogui.ImageNotFoundException(f"类型：{type_name}，查找图片{el} 位置，当前屏幕无此内容，以截屏")

    def click_picture(self, el, clicks: int = 1, button='left', is_click=True):
        """ 图片点击、悬停, 点击次数, 鼠标左键还是右键点击"""
        pos_x_y = self.is_exist(el)
        # print(66, pos_x_y)
        if not  pos_x_y:
            self._error_record(el, 'click_picture')
        pyautogui.moveTo(pos_x_y, duration=self.duration)
        if is_click:
            pyautogui.click(pos_x_y, clicks=clicks, button=button, interval=self.interval)
            logger.debug(f"移动到图片{el}位置{is_click}， 点击{pos_x_y}成功")
        logger.debug(f"移动到图片{el}位置成功")

    def rel_picture_click(self, el, rel_x=0, rel_y=0, clicks: int = 1, button='left', is_click=True):
        """ 相对位置点击 图片点击、悬停, 点击次数, 鼠标左键还是右键点击"""
        pos_x_y = self.is_exist(el)
        if not pos_x_y:
            self._error_record(el, 'rel_click_picture')
        pyautogui.moveTo(pos_x_y, duration=self.duration)
        pyautogui.moveRel(rel_x, rel_y, duration=self.duration)
        if is_click:
            pyautogui.click(clicks=clicks, button=button, interval=self.interval)
        logger.debug(f"查找图片{el}，位置{is_click}，偏移位置{rel_x, rel_y}，点击{is_click}, 成功")

    def click(self, pos_x=None, pos_y=None, clicks: int = 1, button='left'):
        """ 鼠标的绝对位置点击 """
        pyautogui.click(pos_x, pos_y, clicks=clicks, button=button, duration=self.duration, interval=self.interval)
        logger.debug(f"鼠标绝对位置点击,坐标:{pos_x, pos_y},使用:{button}按钮,点击:{clicks}次")

    def rel_click(self, rel_x=0, rel_y=0, clicks: int = 1, button='left'):
        """ 鼠标相对位置点击 """
        pyautogui.move(rel_x, rel_y, duration=self.duration)
        pyautogui.click(clicks=clicks, button=button, duration=self.duration, interval=self.interval)
        logger.debug(f"鼠标相对位置点击,移动:{rel_x, rel_y},使用:{button}按钮,点击:{clicks}次")

    def moveto(self, pos_x=None, pos_y=None, rel=False):
        """ 鼠标移动&相对位置移动 """
        if rel:
            pyautogui.moveRel(pos_x, pos_y, duration=self.duration)
            logger.debug(f"鼠标相对位置(偏移)移动:{pos_x, pos_y}")
        else:
            pyautogui.moveTo(pos_x, pos_y, duration=self.duration)
            logger.debug(f"鼠标绝对位置移动,坐标:{pos_x, pos_y}")

    def drag(self, pos_x=None, pos_y=None, button='left', rel=False):
        """ 鼠标拖拽, 相对位置拖拽， 绝对位置拖拽 """
        if rel:
            pyautogui.dragRel(pos_x, pos_y, duration=self.duration, button=button)
            logger.debug(f"鼠标相对位置(偏移)拖拽:{pos_x, pos_y}")
        else:
            pyautogui.dragTo(pos_x, pos_y, duration=self.duration, button=button)
            logger.debug(f"鼠标绝对位置拖拽,坐标:{pos_x, pos_y}")

    def scroll(self, amount_to_scroll, move_to_x=None, move_to_y=None):
        """ 鼠标滚轮 amount_to_scroll正数为向上滚动，负数向下 """
        pyautogui.scroll(clicks=amount_to_scroll, x=move_to_x, y=move_to_y)
        logger.debug(f"鼠标滚轮,滚动:{amount_to_scroll}")

    def write_type(self, *args):
        """ 键盘输入长文本(不包含中文) """
        pyautogui.write(*args)
        logger.debug(f"键盘输入:{args}")

    def input_string(self, text, copy_to_clipboard=False):
        """ 键盘输入中文 """
        pyperclip.copy(text)
        if not copy_to_clipboard:
            pyautogui.hotkey('ctrl', 'v')
            logger.debug(f"键盘输入:{text}")

    def press(self, key):
        """ 键盘单个按键操作"""
        pyautogui.press(key)
        logger.debug(f"键盘按键:{key},按下")

    def hotkey(self, *args):
        """ 键盘组合按键操作 """
        pyautogui.hotkey(*args)
        logger.debug(f"键盘组合按键:{args},按下")


if __name__ == '__main__':
    gui = GuiBase()
    time.sleep(3)
    # gui.click_picture('qq_icon', clicks=2)
    # gui.rel_click_picture('qq_icon', rel_y=-320, clicks=2)
    # time.sleep(3)
    # gui.moveto(235, 155)
    # time.sleep(3)
    # gui.drag(100, 100, rel=True)
    # gui.scroll(-1000)
    # gui.input_string('hello,world你看卡', copy_to_clipboard=True)
    gui.hotkey('win', 'd')



