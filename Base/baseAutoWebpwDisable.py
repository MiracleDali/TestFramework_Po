"""
# file:     Base/baseAutoWebPw.py
# WEB自动化
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

# 获取当前文件的父目录的父目录（项目根目录）
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from Base.baseContainer import GlobalManager
from Base.baseData import DataBase
from Base.baseLogger import Logger
from Base.utils import read_config_ini
from Base.basePath import BasePath as BP
from playwright.sync_api import Page, Locator, expect, Dialog, Frame, ElementHandle

logger = Logger('Base/baseAutoWebPw.py').getLogger()



class BaesWebPw(DataBase):
    """Playwright WEB自动化基类"""
    
    def __init__(self, yaml_name: Optional[str] = None):
        """
        初始化Playwright基类
        yaml_name: YAML配置文件名，如果为None则不加载配置
        """
        self.config = read_config_ini(BP.CONFIG_FILE)
        if yaml_name:
            super().__init__(yaml_name)
        self.page: Page = GlobalManager().get_value('page')
        self.page.set_default_timeout(int(self.config['WEB自动化配置']['pw_timeout'])) 
        self.default_timeout = 10000  # 超时时间（毫秒）
        # 当前上下文 frame（如果已切换到 iframe，设置为 Frame 对象；否则为 None）
        self._current_frame: Optional[Frame] = None
 

    def get_locator_data(self, locator: str, change_data=None) -> tuple:
        """
        获取元素数据
            param: change_data: 是否修改yaml数据
            param: locator: (login/password)-->yaml文件的层级关系
        """
        res = self.get_element_data(change_data)  # 读取到的yaml文件信息
        # print(res)
        items = locator.split('/')  # 吧传进来的字符串，使用 / 分割成列表 --> ["login", "username"]
        # print(items)
        # print([items[0]])
        locator_data = tuple(res[items[0]][items[1]])
        return locator_data


    def locator(self, selector: str, has_text: Optional[str] = None, has: Optional[str] = None) -> Locator:
        """
        获取定位器
        
        Args:
            selector: CSS选择器或XPath表达式
            has_text: 筛选包含特定文本的元素
            has: 筛选包含特定子元素的元素选择器
            
        Returns:
            Locator: Playwright定位器对象
        """
        has_locator = None
        if has:
            has_locator = self.page.locator(has)
        return self.page.locator(selector, has_text=has_text, has=has_locator)
        
    def goto(self, url: str, wait_until: str = "load", timeout: Optional[int] = None):
        """
        导航到指定URL
        url: 要导航到的URL
        wait_until: 等待条件，可选值："commit", "domcontentloaded", "load", "networkidle"
        timeout: 超时时间（毫秒）
        """
        try:
            self.page.goto(url, wait_until=wait_until, timeout=timeout or self.default_timeout)
            logger.info(f"导航到URL: {url}")
        except Exception as e:
            logger.exception(f"导航到URL失败: {url}")
            raise e


    def get_by_role(self, role: str, **kwargs) -> Locator:
        """
        通过ARIA角色获取元素
        
        Args:
            role: ARIA角色，如"button", "link", "textbox"等
            **kwargs: 其他属性，如name, checked, pressed等
            
        Returns:
            Locator: Playwright定位器对象
        """
        return self.page.get_by_role(role, **kwargs)
    
    def get_by_text(self, text: str, exact: bool = False) -> Locator:
        """
        通过文本内容获取元素
        
        Args:
            text: 文本内容
            exact: 是否精确匹配
            
        Returns:
            Locator: Playwright定位器对象
        """
        return self.page.get_by_text(text, exact=exact)
    
    def get_by_label(self, text: str) -> Locator:
        """
        通过标签文本获取元素
        
        Args:
            text: 标签文本
            
        Returns:
            Locator: Playwright定位器对象
        """
        return self.page.get_by_label(text)
        
    def get_by_placeholder(self, text: str) -> Locator:
        """
        通过占位符文本获取元素
        
        Args:
            text: 占位符文本
            
        Returns:
            Locator: Playwright定位器对象
        """
        return self.page.get_by_placeholder(text)
        
    def get_by_test_id(self, test_id: str) -> Locator:
        """
        通过测试ID获取元素
        
        Args:
            test_id: 测试ID（data-testid属性值）
            
        Returns:
            Locator: Playwright定位器对象
        """
        return self.page.get_by_test_id(test_id)
        
    def click(self, selector: str, **kwargs):
        """
        点击元素
        
        Args:
            selector: CSS选择器或XPath表达式
            **kwargs: 点击选项，如button, modifiers, position等
        """
        try:
            self.locator(selector).click(**kwargs)
            logger.info(f"点击元素: {selector}")
        except Exception as e:
            logger.error(f"点击元素失败: {selector}")
            raise e
        
    def dblclick(self, selector: str, **kwargs):
        """
        双击元素
        
        Args:
            selector: CSS选择器或XPath表达式
            **kwargs: 双击选项，如button, modifiers, position等
        """
        try:
            self.locator(selector).dblclick(**kwargs)
            logger.info(f"双击元素: {selector}")
        except Exception as e:
            logger.error(f"双击元素失败: {selector}")
            raise e
            
    def fill(self, selector: str, value: str, **kwargs):
        """
        填充表单字段
        
        Args:
            selector: CSS选择器或XPath表达式
            value: 要填充的值
            **kwargs: 填充选项，如force, timeout等
        """
        try:
            self.locator(selector).fill(value, **kwargs)
            logger.info(f"填充表单: {selector} -> {value}")
        except Exception as e:
            logger.error(f"填充表单失败: {selector} -> {value}")
            raise e
            
    def type(self, selector: str, text: str, **kwargs):
        """
        模拟键盘输入
        
        Args:
            selector: CSS选择器或XPath表达式
            text: 要输入的文本
            **kwargs: 输入选项，如delay等
        """
        try:
            self.locator(selector).type(text, **kwargs)
            logger.info(f"输入文本: {selector} -> {text}")
        except Exception as e:
            logger.error(f"输入文本失败: {selector} -> {text}")
            raise e
            
    def press(self, selector: str, key: str, **kwargs):
        """
        按下键盘键
        
        Args:
            selector: CSS选择器或XPath表达式
            key: 按键名称，如"Enter", "ArrowDown"等
            **kwargs: 按键选项
        """
        try:
            self.locator(selector).press(key, **kwargs)
            logger.info(f"按下按键: {selector} -> {key}")
        except Exception as e:
            logger.error(f"按下按键失败: {selector} -> {key}")
            raise e
            
    def select_option(self, selector: str, value: str, **kwargs):
        """
        选择下拉选项
        
        Args:
            selector: CSS选择器或XPath表达式
            value: 选项值
            **kwargs: 选择选项
        """
        try:
            self.locator(selector).select_option(value, **kwargs)
            logger.info(f"选择选项: {selector} -> {value}")
        except Exception as e:
            logger.error(f"选择选项失败: {selector} -> {value}")
            raise e
            
    def check(self, selector: str, **kwargs):
        """
        勾选复选框或单选按钮
        
        Args:
            selector: CSS选择器或XPath表达式
            **kwargs: 勾选选项
        """
        try:
            self.locator(selector).check(**kwargs)
            logger.info(f"勾选元素: {selector}")
        except Exception as e:
            logger.error(f"勾选元素失败: {selector}")
            raise e
            
    def uncheck(self, selector: str, **kwargs):
        """
        取消勾选复选框
        
        Args:
            selector: CSS选择器或XPath表达式
            **kwargs: 取消勾选选项
        """
        try:
            self.locator(selector).uncheck(**kwargs)
            logger.info(f"取消勾选元素: {selector}")
        except Exception as e:
            logger.error(f"取消勾选元素失败: {selector}")
            raise e
            
    def hover(self, selector: str, **kwargs):
        """
        鼠标悬停
        
        Args:
            selector: CSS选择器或XPath表达式
            **kwargs: 悬停选项
        """
        try:
            self.locator(selector).hover(**kwargs)
            logger.info(f"鼠标悬停: {selector}")
        except Exception as e:
            logger.error(f"鼠标悬停失败: {selector}")
            raise e
            
    def focus(self, selector: str, **kwargs):
        """
        聚焦元素
        
        Args:
            selector: CSS选择器或XPath表达式
            **kwargs: 聚焦选项
        """
        try:
            self.locator(selector).focus(**kwargs)
            logger.info(f"聚焦元素: {selector}")
        except Exception as e:
            logger.error(f"聚焦元素失败: {selector}")
            raise e
            
    def drag_to(self, source_selector: str, target_selector: str, **kwargs):
        """
        拖放元素
        
        Args:
            source_selector: 源元素选择器
            target_selector: 目标元素选择器
            **kwargs: 拖放选项
        """
        try:
            source = self.locator(source_selector)
            target = self.locator(target_selector)
            source.drag_to(target, **kwargs)
            logger.info(f"拖放元素: {source_selector} -> {target_selector}")
        except Exception as e:
            logger.error(f"拖放元素失败: {source_selector} -> {target_selector}")
            raise e
            
    def screenshot(self, selector: Optional[str] = None, **kwargs) -> bytes:
        """
        截取屏幕或元素截图
        
        Args:
            selector: 可选，要截图的元素选择器
            **kwargs: 截图选项
            
        Returns:
            bytes: 截图数据
        """
        try:
            if selector:
                screenshot = self.locator(selector).screenshot(**kwargs)
                logger.info(f"元素截图: {selector}")
            else:
                screenshot = self.page.screenshot(**kwargs)
                logger.info("页面截图")
            return screenshot
        except Exception as e:
            logger.error("截图失败")
            raise e
            
    def wait_for_timeout(self, timeout: int):
        """
        等待指定时间
        
        Args:
            timeout: 等待时间（毫秒）
        """
        self.page.wait_for_timeout(timeout)
        logger.info(f"等待 {timeout} 毫秒")
        
    def wait_for_selector(self, selector: str, **kwargs):
        """
        等待选择器匹配的元素出现
        
        Args:
            selector: CSS选择器或XPath表达式
            **kwargs: 等待选项
        """
        self.page.wait_for_selector(selector, **kwargs)
        logger.info(f"等待元素出现: {selector}")
        
    def wait_for_url(self, url: str, **kwargs):
        """
        等待URL匹配指定模式
        Args:
            url: URL或URL模式
            **kwargs: 等待选项
        """
        self.page.wait_for_url(url, **kwargs)
        logger.info(f"等待URL: {url}")
        
    def wait_for_load_state(self, state: str = "load", **kwargs):
        """
        等待页面加载状态
        Args:
            state: 加载状态，可选值："load", "domcontentloaded", "networkidle"
            **kwargs: 等待选项
        """
        self.page.wait_for_load_state(state, **kwargs)
        logger.info(f"等待加载状态: {state}")
        
    def expect(self, selector: str):
        """
        获取断言对象
        
        Args:
            selector: CSS选择器或XPath表达式
            
        Returns:
            expect: Playwright断言对象
        """
        return expect(self.locator(selector))
        
    def evaluate(self, expression: str, arg: Any = None) -> Any:
        """
        在页面上下文中执行JavaScript表达式
        
        Args:
            expression: JavaScript表达式
            arg: 传递给表达式的参数
            
        Returns:
            Any: 表达式执行结果
        """
        try:
            result = self.page.evaluate(expression, arg)
            logger.info(f"执行JavaScript: {expression}")
            return result
        except Exception as e:
            logger.error(f"执行JavaScript失败: {expression}")
            raise e
            
    def evaluate_handle(self, expression: str, arg: Any = None) -> Any:
        """
        在页面上下文中执行JavaScript表达式并返回JSHandle
        
        Args:
            expression: JavaScript表达式
            arg: 传递给表达式的参数
            
        Returns:
            Any: JSHandle对象
        """
        try:
            result = self.page.evaluate_handle(expression, arg)
            logger.info(f"执行JavaScript并返回句柄: {expression}")
            return result
        except Exception as e:
            logger.error(f"执行JavaScript并返回句柄失败: {expression}")
            raise e
            
    def dispatch_event(self, locator: Locator, event_type: str, event_init: Dict = None):
        """
        分派事件到元素
        
        Args:
            locator: Playwright定位器
            event_type: 事件类型
            event_init: 事件初始化参数
        """
        try:
            locator.dispatch_event(event_type, event_init)
            logger.info(f"分派事件: {locator} -> {event_type}")
        except Exception as e:
            logger.error(f"分派事件失败: {locator} -> {event_type}")
            raise e
            
    def get_attribute(self, selector: str, name: str) -> Optional[str]:
        """
        获取元素属性值
        
        Args:
            selector: CSS选择器或XPath表达式
            name: 属性名
            
        Returns:
            Optional[str]: 属性值
        """
        try:
            value = self.locator(selector).get_attribute(name)
            logger.info(f"获取属性: {selector} -> {name} = {value}")
            return value
        except Exception as e:
            logger.error(f"获取属性失败: {selector} -> {name}")
            raise e
            
    def inner_text(self, selector: str) -> str:
        """
        获取元素内部文本
        
        Args:
            selector: CSS选择器或XPath表达式
            
        Returns:
            str: 内部文本
        """
        try:
            text = self.locator(selector).inner_text()
            logger.info(f"获取内部文本: {selector} -> {text}")
            return text
        except Exception as e:
            logger.error(f"获取内部文本失败: {selector}")
            raise e
            
    def text_content(self, selector: str) -> Optional[str]:
        """
        获取元素文本内容
        
        Args:
            selector: CSS选择器或XPath表达式
            
        Returns:
            Optional[str]: 文本内容
        """
        try:
            content = self.locator(selector).text_content()
            logger.info(f"获取文本内容: {selector} -> {content}")
            return content
        except Exception as e:
            logger.error(f"获取文本内容失败: {selector}")
            raise e
            
    def input_value(self, selector: str) -> str:
        """
        获取输入元素的值
        
        Args:
            selector: CSS选择器或XPath表达式
            
        Returns:
            str: 输入值
        """
        try:
            value = self.locator(selector).input_value()
            logger.info(f"获取输入值: {selector} -> {value}")
            return value
        except Exception as e:
            logger.error(f"获取输入值失败: {selector}")
            raise e
            
    def is_checked(self, selector: str) -> bool:
        """
        检查元素是否被选中
        
        Args:
            selector: CSS选择器或XPath表达式
            
        Returns:
            bool: 是否选中
        """
        try:
            checked = self.locator(selector).is_checked()
            logger.info(f"检查选中状态: {selector} -> {checked}")
            return checked
        except Exception as e:
            logger.error(f"检查选中状态失败: {selector}")
            raise e
            
    def is_disabled(self, selector: str) -> bool:
        """
        检查元素是否被禁用
        
        Args:
            selector: CSS选择器或XPath表达式
            
        Returns:
            bool: 是否禁用
        """
        try:
            disabled = self.locator(selector).is_disabled()
            logger.info(f"检查禁用状态: {selector} -> {disabled}")
            return disabled
        except Exception as e:
            logger.error(f"检查禁用状态失败: {selector}")
            raise e
            
    def is_editable(self, selector: str) -> bool:
        """
        检查元素是否可编辑
        
        Args:
            selector: CSS选择器或XPath表达式
            
        Returns:
            bool: 是否可编辑
        """
        try:
            editable = self.locator(selector).is_editable()
            logger.info(f"检查可编辑状态: {selector} -> {editable}")
            return editable
        except Exception as e:
            logger.error(f"检查可编辑状态失败: {selector}")
            raise e
            
    def is_enabled(self, selector: str) -> bool:
        """
        检查元素是否启用
        
        Args:
            selector: CSS选择器或XPath表达式
            
        Returns:
            bool: 是否启用
        """
        try:
            enabled = self.locator(selector).is_enabled()
            logger.info(f"检查启用状态: {selector} -> {enabled}")
            return enabled
        except Exception as e:
            logger.error(f"检查启用状态失败: {selector}")
            raise e
            
    def is_hidden(self, selector: str) -> bool:
        """
        检查元素是否隐藏
        
        Args:
            selector: CSS选择器或XPath表达式
            
        Returns:
            bool: 是否隐藏
        """
        try:
            hidden = self.locator(selector).is_hidden()
            logger.info(f"检查隐藏状态: {selector} -> {hidden}")
            return hidden
        except Exception as e:
            logger.error(f"检查隐藏状态失败: {selector}")
            raise e
            
    def is_visible(self, selector: str) -> bool:
        """
        检查元素是否可见
        
        Args:
            selector: CSS选择器或XPath表达式
            
        Returns:
            bool: 是否可见
        """
        try:
            visible = self.locator(selector).is_visible()
            logger.info(f"检查可见状态: {selector} -> {visible}")
            return visible
        except Exception as e:
            logger.error(f"检查可见状态失败: {selector}")
            raise e
            
    def count(self, selector: str) -> int:
        """
        获取匹配元素的数量
        
        Args:
            selector: CSS选择器或XPath表达式
            
        Returns:
            int: 元素数量
        """
        try:
            count = self.locator(selector).count()
            logger.info(f"获取元素数量: {selector} -> {count}")
            return count
        except Exception as e:
            logger.error(f"获取元素数量失败: {selector}")
            raise e
            
    def all_inner_texts(self, selector: str) -> List[str]:
        """
        获取所有匹配元素的内部文本
        
        Args:
            selector: CSS选择器或XPath表达式
            
        Returns:
            List[str]: 内部文本列表
        """
        try:
            texts = self.locator(selector).all_inner_texts()
            logger.info(f"获取所有内部文本: {selector} -> {len(texts)} 个元素")
            return texts
        except Exception as e:
            logger.error(f"获取所有内部文本失败: {selector}")
            raise e
            
    def all_text_contents(self, selector: str) -> List[str]:
        """
        获取所有匹配元素的文本内容
        
        Args:
            selector: CSS选择器或XPath表达式
            
        Returns:
            List[str]: 文本内容列表
        """
        try:
            contents = self.locator(selector).all_text_contents()
            logger.info(f"获取所有文本内容: {selector} -> {len(contents)} 个元素")
            return contents
        except Exception as e:
            logger.error(f"获取所有文本内容失败: {selector}")
            raise e
            
    def set_input_files(self, selector: str, files: str):
        """
        设置文件输入元素的值
        
        Args:
            selector: CSS选择器或XPath表达式
            files: 文件路径
        """
        try:
            self.locator(selector).set_input_files(files)
            logger.info(f"设置文件输入: {selector} -> {files}")
        except Exception as e:
            logger.error(f"设置文件输入失败: {selector} -> {files}")
            raise e
            
    def clear(self, selector: str):
        """
        清空输入元素的内容
        
        Args:
            selector: CSS选择器或XPath表达式
        """
        try:
            self.locator(selector).clear()
            logger.info(f"清空输入: {selector}")
        except Exception as e:
            logger.error(f"清空输入失败: {selector}")
            raise e
            
    def blur(self, selector: str):
        """
        使元素失去焦点
        
        Args:
            selector: CSS选择器或XPath表达式
        """
        try:
            self.locator(selector).blur()
            logger.info(f"失去焦点: {selector}")
        except Exception as e:
            logger.error(f"失去焦点操作失败: {selector}")
            raise e
            
    def tap(self, selector: str, **kwargs):
        """
        触摸点击元素（移动端）
        
        Args:
            selector: CSS选择器或XPath表达式
            **kwargs: 点击选项
        """
        try:
            self.locator(selector).tap(**kwargs)
            logger.info(f"触摸点击: {selector}")
        except Exception as e:
            logger.error(f"触摸点击失败: {selector}")
            raise e
            
    def scroll_into_view_if_needed(self, selector: str, **kwargs):
        """
        如果需要，将元素滚动到视图中
        
        Args:
            selector: CSS选择器或XPath表达式
            **kwargs: 滚动选项
        """
        try:
            self.locator(selector).scroll_into_view_if_needed(**kwargs)
            logger.info(f"滚动到视图: {selector}")
        except Exception as e:
            logger.error(f"滚动到视图失败: {selector}")
            raise e
            
    def select_text(self, selector: str, **kwargs):
        """
        选择元素中的文本
        
        Args:
            selector: CSS选择器或XPath表达式
            **kwargs: 选择选项
        """
        try:
            self.locator(selector).select_text(**kwargs)
            logger.info(f"选择文本: {selector}")
        except Exception as e:
            logger.error(f"选择文本失败: {selector}")
            raise e
            
    def set_checked(self, selector: str, checked: bool, **kwargs):
        """
        设置元素的选中状态
        
        Args:
            selector: CSS选择器或XPath表达式
            checked: 是否选中
            **kwargs: 设置选项
        """
        try:
            self.locator(selector).set_checked(checked, **kwargs)
            logger.info(f"设置选中状态: {selector} -> {checked}")
        except Exception as e:
            logger.error(f"设置选中状态失败: {selector} -> {checked}")
            raise e
    
            
    def mock_api(self, url_pattern: str, response: Dict, method: str = "GET"):
        """
        模拟API响应
        
        Args:
            url_pattern: URL模式
            response: 响应内容
            method: HTTP方法
        """
        try:
            # 使用Playwright的路由功能模拟API
            def handle_route(route):
                route.fulfill(
                    status=200,
                    content_type="application/json",
                    body=json.dumps(response)
                )
                
            self.page.route(url_pattern, handle_route)
            logger.info(f"模拟API: {method} {url_pattern}")
        except Exception as e:
            logger.error(f"模拟API失败: {method} {url_pattern}")
            raise e
            
    def unmock_api(self, url_pattern: str):
        """
        取消模拟API
        
        Args:
            url_pattern: URL模式
        """
        try:
            self.page.unroute(url_pattern)
            logger.info(f"取消模拟API: {url_pattern}")
        except Exception as e:
            logger.error(f"取消模拟API失败: {url_pattern}")
            raise e