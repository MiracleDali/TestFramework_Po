# file:     Base/baseAutoWebPw.py
# WEB自动化 (Playwright) — 严格使用 YAML 顶层 key（找不到直接抛错）

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List, Iterator, Callable
from datetime import datetime
import json
import contextlib

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


class WebBase(DataBase):
    """Playwright WEB自动化基类"""

    def __init__(self, yaml_name: Optional[str] = None):
        """
        初始化Playwright基类
        """
        super().__init__(yaml_name)
        self.config = read_config_ini(BP.CONFIG_FILE)
        self.page: Page = GlobalManager().get_value('page')
        try:
            self.page.set_default_timeout(int(self.config['WEB自动化配置']['pw_timeout']))
        except Exception:
            self.page.set_default_timeout(10000)
        self.default_timeout = 10000  # 超时时间（毫秒）
        # 当前上下文 frame（如果已切换到 iframe，设置为 Frame 对象；否则为 None）
        self._current_frame: Optional[Frame] = None
        # 记录当前对话框消息
        self.dialog_message = None

    # -----------------------
    # Frame / IFrame 支持
    # -----------------------
    def get_frame_by_name(self, name: str) -> Optional[Frame]:
        try:
            frame = self.page.frame(name=name)
            logger.info(f"get_frame_by_name: name={name} -> {frame}")
            return frame
        except Exception as e:
            logger.error(f"get_frame_by_name 失败: {name} -> {e}")
            return None

    def get_frame_by_url(self, url_substring: str) -> Optional[Frame]:
        try:
            for f in self.page.frames:
                if f.url and url_substring in f.url:
                    logger.info(f"get_frame_by_url: found frame with url {f.url}")
                    return f
            logger.warning(f"get_frame_by_url: no frame contains '{url_substring}'")
            return None
        except Exception as e:
            logger.error(f"get_frame_by_url 失败: {url_substring} -> {e}")
            return None

    def get_frame_by_index(self, index: int) -> Optional[Frame]:
        try:
            frames = self.page.frames
            frame = frames[index]
            logger.info(f"get_frame_by_index: index={index} -> {frame}")
            return frame
        except Exception as e:
            logger.error(f"get_frame_by_index 失败: {index} -> {e}")
            return None

    def get_frame_by_selector(self, selector: str, timeout: Optional[int] = None) -> Optional[Frame]:
        """
        通过选择器找到 <iframe> 或 <frame> 元素并返回该元素对应的 Frame（使用 element_handle.content_frame()）
        selector 必须是 YAML key（顶层 key）或直接是 selector 字符串 —— 但按当前严格逻辑，应使用 YAML key。
        找不到 YAML key 时将抛出 KeyError。
        """
        try:
            timeout = timeout or self.default_timeout
            resolved = self._resolve_selector_if_key(selector)
            self.page.wait_for_selector(resolved, timeout=timeout)
            elem: Optional[ElementHandle] = self.page.query_selector(resolved)
            if not elem:
                logger.warning(f"get_frame_by_selector: 未找到元素 {selector} (resolved: {resolved})")
                return None
            frame = elem.content_frame()
            if frame:
                logger.info(f"get_frame_by_selector: selector={selector} -> frame {frame.url}")
            else:
                logger.warning(f"get_frame_by_selector: selector={selector} 找到元素但未关联 frame")
            return frame
        except Exception as e:
            logger.error(f"get_frame_by_selector 失败: {selector} -> {e}")
            return None

    def get_frame_by_element(self, element: ElementHandle) -> Optional[Frame]:
        try:
            frame = element.content_frame()
            logger.info(f"get_frame_by_element -> {frame}")
            return frame
        except Exception as e:
            logger.error(f"get_frame_by_element 失败 -> {e}")
            return None

    def enter_frame(self, *, name: Optional[str] = None, index: Optional[int] = None,
                    url_substring: Optional[str] = None, selector: Optional[str] = None,
                    timeout: Optional[int] = None) -> Optional[Frame]:
        """
        切换当前上下文到某个 frame（存储到 self._current_frame），返回找到的 Frame。
        优先级: selector -> name -> index -> url_substring
        selector 应传 YAML key（顶层 key）
        """
        try:
            frame = None
            if selector:
                frame = self.get_frame_by_selector(selector, timeout=timeout)
            elif name:
                frame = self.get_frame_by_name(name)
            elif index is not None:
                frame = self.get_frame_by_index(index)
            elif url_substring:
                frame = self.get_frame_by_url(url_substring)
            else:
                raise ValueError("enter_frame 需要传入 selector/name/index/url_substring 之一")

            if not frame:
                raise RuntimeError("未找到目标 frame")
            self._current_frame = frame
            logger.info(f"enter_frame -> current_frame set to {frame.url}")
            return frame
        except Exception as e:
            logger.error(f"enter_frame 失败 -> {e}")
            raise

    def exit_frame(self):
        try:
            self._current_frame = None
            logger.info("exit_frame -> 回到主页面上下文")
        except Exception as e:
            logger.error(f"exit_frame 失败 -> {e}")
            raise

    @contextlib.contextmanager
    def frame_context(self, *, name: Optional[str] = None, index: Optional[int] = None,
                      url_substring: Optional[str] = None, selector: Optional[str] = None,
                      timeout: Optional[int] = None) -> Iterator[Frame]:
        prev = self._current_frame
        try:
            frame = self.enter_frame(name=name, index=index, url_substring=url_substring, selector=selector,
                                     timeout=timeout)
            yield frame
        finally:
            self._current_frame = prev
            logger.info("frame_context exit -> 恢复之前的 frame 上下文")

    def get_locator_data(self, locator_key: str, change_data: Optional[dict] = None) -> str:
        """
        从 yaml 中读取 locator 数据。locator_key 示例: "username"
        严格从 YAML 顶层查找 key；找不到则直接抛 KeyError（不再有任何回退/容错）。
        YAML 示例（顶层）：
            username: "[name='_58_login']"
            password: "//input[@type='submit']"
        返回 selector 字符串，例如 "[name='_58_login']" 或 "//input[@type='submit']"
        """
        res = self.get_element_data(change_data)  # 你的 DataBase.get_element_data()
        if not isinstance(res, dict):
            raise TypeError("get_element_data 返回值必须是字典类型，且顶层包含 locator key")
        if locator_key not in res:
            # 严格要求：必须在顶层找到，否则直接抛错
            raise KeyError(f"YAML 顶层未找到 locator_key: {locator_key}")
        selector = res[locator_key]
        return selector

    def _resolve_selector_if_key(self, selector_or_key: str) -> str:
        """
        严格解析：把传入字符串当作 YAML key（顶层）去获取 selector；
        若不存在则抛出 KeyError（不再回退）。
        """
        sel = self.get_locator_data(selector_or_key)
        return sel

    def _resolve_selector_to_playwright(self, selector: str) -> str:
        """
        将 selector 字符串简单规范化以便 Playwright 识别：
        - 如果以 // 开头则视为 xpath，返回 'xpath=...'
        - 其它直接返回（Playwright 默认识别 css selector）
        """
        s = selector.strip()
        if s.startswith("//") or s.startswith("(//"):
            return f'xpath={s}'
        return s

    def locator(self, selector: str, has_text: Optional[str] = None, has: Optional[str] = None) -> Locator:
        """
        获取定位器（会优先在当前 frame 上查找，如果未切换 frame 则在 page 上查找）
        selector 必须是 YAML 顶层 key（如 "username"）—— 否则会抛 KeyError。
        """
        resolved = self._resolve_selector_if_key(selector)
        pw_selector = self._resolve_selector_to_playwright(resolved)

        has_locator = None
        if has:
            # has 也必须是 YAML key（顶层）
            has_sel = self._resolve_selector_if_key(has)
            has_pw = self._resolve_selector_to_playwright(has_sel)
            if self._current_frame:
                has_locator = self._current_frame.locator(has_pw)
            else:
                has_locator = self.page.locator(has_pw)

        if self._current_frame:
            return self._current_frame.locator(pw_selector, has_text=has_text, has=has_locator)
        else:
            logger.info(f"locator -> 【{selector}】={pw_selector}")
            return self.page.locator(pw_selector, has_text=has_text, has=has_locator)

    # -----------------------
    # Dialog / 弹窗 处理
    # -----------------------

    def handle_accept_dialog(self, dialog, text=None):
        """处理弹窗并点击确定按钮"""
        self.page.wait_for_timeout(1000)
        if dialog.type == 'prompt' and text is not None:
            dialog.accept(text)
            logger.info(f"prompt {dialog.type} 点击确定，输入内容: {text}")
        else:
            dialog.accept()
            logger.info(f"{dialog.type} 类型弹窗，点击确定")

    def handle_dismiss_dialog(self, dialog):
        """处理弹窗并点击取消按钮"""
        self.page.wait_for_timeout(500)
        dialog.dismiss()
        logger.info(f"{dialog.type} 类型弹窗，点击取消")

    def handle_get_dialog_message(self, dialog):
        """获取弹窗消息,并取消弹窗"""
        self.page.wait_for_timeout(500)
        message = dialog.message
        dialog.dismiss()
        logger.info(f"获取到弹窗信息: {message}")
        self.dialog_message = message

    def on_dialog(self, handler_type=None, text=None, get_message=False):
        """注册弹窗处理函数
        Args:
            handler_type: 处理类型 'accept'|'dismiss'
            text: 需要输入的文本（仅对prompt类型的弹窗有效）
            get_message: 是否获取弹窗消息
        参数使用：
            self.on_dialog(handler_type='accept')
            self.on_dialog(handler_type='dismiss')
            self.on_dialog(handler_type='accept', text='hello, world!')
            self.on_dialog(get_message=True)
        hand = self.on_dialog(handler_type='accept')  # 使用
        off = self.off_dialog(hand)  # 注销
        """
        def dialog_handler(dialog):
            if handler_type == 'accept':
                self.handle_accept_dialog(dialog, text)
            elif handler_type == 'dismiss':
                self.handle_dismiss_dialog(dialog)
            elif get_message:
                return self.handle_get_dialog_message(dialog)
        
        try:
            self.page.on("dialog", dialog_handler)
            logger.info(f"on_dialog -> handler registered with type: {handler_type}")
            return dialog_handler
        except Exception as e:
            logger.error(f"on_dialog 注册失败 -> {e}")
            raise

    def off_dialog(self, handler: Callable[[Dialog], None]):
        """ 
        注销之前注册的对话框处理函数。
        hand = self.on_dialog(handler_type='accept')  # 使用
        off = self.off_dialog(hand)  # 注销
        """
        try:
            self.page.remove_listener("dialog", handler)
            logger.info("off_dialog -> handler unregistered")
        except Exception as e:
            logger.error(f"off_dialog 注销失败 -> {e}")
            # 不抛出以保持容错

    # -----------------------
    # 其余方法（使用新的 locator() 实现，保持函数名不变）
    # -----------------------
    def goto(self, url: str, wait_until: str = "load", timeout: Optional[int] = None):
        try:
            self.page.goto(url, wait_until=wait_until, timeout=timeout or self.default_timeout)
            logger.info(f"导航到URL: {url}")
        except Exception as e:
            logger.exception(f"导航到URL失败: {url} -> {e}")
            raise e

    def get_by_role(self, role, **kwargs) -> Locator:
        if self._current_frame:
            return self._current_frame.get_by_role(role, **kwargs)
        return self.page.get_by_role(role, **kwargs)

    def get_by_text(self, text: str, exact: bool = False) -> Locator:
        if self._current_frame:
            return self._current_frame.get_by_text(text, exact=exact)
        return self.page.get_by_text(text, exact=exact)

    def get_by_label(self, text: str) -> Locator:
        if self._current_frame:
            return self._current_frame.get_by_label(text)
        return self.page.get_by_label(text)

    def get_by_placeholder(self, text: str) -> Locator:
        if self._current_frame:
            return self._current_frame.get_by_placeholder(text)
        return self.page.get_by_placeholder(text)

    def get_by_test_id(self, test_id: str) -> Locator:
        if self._current_frame:
            return self._current_frame.get_by_test_id(test_id)
        return self.page.get_by_test_id(test_id)

    def click(self, selector: str, **kwargs):
        try:
            self.locator(selector).click(**kwargs)
            logger.info(f"点击元素: 【{selector}】")
        except Exception as e:
            logger.error(f"点击元素失败: 【{selector}】 -> {e}")
            raise e

    def dblclick(self, selector: str, **kwargs):
        try:
            self.locator(selector).dblclick(**kwargs)
            logger.info(f"双击元素: {selector}")
        except Exception as e:
            logger.error(f"双击元素失败: {selector} -> {e}")
            raise e

    def fill(self, selector: str, value: str, **kwargs):
        try:
            self.locator(selector).fill(value, **kwargs)
            logger.info(f"填充表单: {selector} -> 内容:（{value}）")
        except Exception as e:
            logger.error(f"填充表单失败: {selector} -> {e}")
            raise e

    def type(self, selector: str, text: str, **kwargs):
        try:
            self.locator(selector).type(text, **kwargs)
            logger.info(f"输入文本: {selector} -> {text}")
        except Exception as e:
            logger.error(f"输入文本失败: {selector} -> {e}")
            raise e

    def press(self, selector: str, key: str, **kwargs):
        try:
            self.locator(selector).press(key, **kwargs)
            logger.info(f"按下按键: {selector} -> {key}")
        except Exception as e:
            logger.error(f"按下按键失败: {selector} -> {e}")
            raise e

    def select_option(self, selector: str, value: str, **kwargs):
        try:
            self.locator(selector).select_option(value, **kwargs)
            logger.info(f"选择选项: {selector} -> {value}")
        except Exception as e:
            logger.error(f"选择下拉失败: {selector} -> {e}")
            raise e

    def check(self, selector: str, **kwargs):
        try:
            self.locator(selector).check(**kwargs)
            logger.info(f"勾选元素: {selector}")
        except Exception as e:
            logger.error(f"勾选元素失败: {selector} -> {e}")
            raise e

    def uncheck(self, selector: str, **kwargs):
        try:
            self.locator(selector).uncheck(**kwargs)
            logger.info(f"取消勾选元素: {selector}")
        except Exception as e:
            logger.error(f"取消勾选元素失败: {selector} -> {e}")
            raise e

    def hover(self, selector: str, **kwargs):
        try:
            self.locator(selector).hover(**kwargs)
            logger.info(f"鼠标悬停: {selector}")
        except Exception as e:
            logger.error(f"鼠标悬停失败: {selector} -> {e}")
            raise e

    def focus(self, selector: str, **kwargs):
        try:
            self.locator(selector).focus(**kwargs)
            logger.info(f"聚焦元素: {selector}")
        except Exception as e:
            logger.error(f"聚焦元素失败: {selector} -> {e}")
            raise e

    def drag_to(self, source_selector: str, target_selector: str, **kwargs):
        try:
            source = self.locator(source_selector)
            target = self.locator(target_selector)
            source.drag_to(target, **kwargs)
            logger.info(f"拖放元素: {source_selector} -> {target_selector}")
        except Exception as e:
            logger.error(f"拖放元素失败: {source_selector} -> {target_selector} -> {e}")
            raise e

    def screenshot(self, selector: Optional[str] = None, **kwargs) -> bytes:
        try:
            if selector:
                screenshot = self.locator(selector).screenshot(**kwargs)
                logger.info(f"元素截图: {selector}")
            else:
                screenshot = self.page.screenshot(**kwargs)
                logger.info("页面截图")
            return screenshot
        except Exception as e:
            logger.error(f"截图失败 -> {e}")
            raise e

    def wait_for_timeout(self, timeout: int):
        self.page.wait_for_timeout(timeout)
        logger.info(f"等待 {timeout} 毫秒")

    def wait_for_selector(self, selector: str, **kwargs):
        # selector 必须是 YAML key（顶层）
        sel = self._resolve_selector_if_key(selector)
        pw_sel = self._resolve_selector_to_playwright(sel)
        if self._current_frame:
            self._current_frame.wait_for_selector(pw_sel, **kwargs)
        else:
            self.page.wait_for_selector(pw_sel, **kwargs)
        logger.info(f"等待元素出现: {selector}")

    def wait_for_url(self, url: str, **kwargs):
        self.page.wait_for_url(url, **kwargs)
        logger.info(f"等待URL: {url}")

    def wait_for_load_state(self, state: str = "load", **kwargs):
        self.page.wait_for_load_state(state, **kwargs)
        logger.info(f"等待加载状态: {state}")

    def expect(self, selector: str):
        """
        获取断言对象（支持当前 frame）
        selector 必须是 YAML key（顶层）
        """
        return expect(self.locator(selector))

    def evaluate(self, expression: str, arg: Any = None) -> Any:
        try:
            if self._current_frame:
                result = self._current_frame.evaluate(expression, arg)
            else:
                result = self.page.evaluate(expression, arg)
            logger.info(f"执行JavaScript: {expression}")
            return result
        except Exception as e:
            logger.error(f"执行JavaScript失败: {expression} -> {e}")
            raise e

    def evaluate_handle(self, expression: str, arg: Any = None) -> Any:
        try:
            if self._current_frame:
                result = self._current_frame.evaluate_handle(expression, arg)
            else:
                result = self.page.evaluate_handle(expression, arg)
            logger.info(f"执行JavaScript并返回句柄: {expression}")
            return result
        except Exception as e:
            logger.error(f"执行JavaScript并返回句柄失败: {expression} -> {e}")
            raise e

    def dispatch_event(self, locator: Locator, event_type: str, event_init: Dict = None):
        try:
            locator.dispatch_event(event_type, event_init)
            logger.info(f"分派事件: {locator} -> {event_type}")
        except Exception as e:
            logger.error(f"分派事件失败: {locator} -> {event_type} -> {e}")
            raise e

    # 以下为读取/操作元素属性的便捷方法（仍使用 locator(selector)）
    def get_attribute(self, selector: str, name: str) -> Optional[str]:
        try:
            value = self.locator(selector).get_attribute(name)
            logger.info(f"获取属性: {selector} -> {name} = {value}")
            return value
        except Exception as e:
            logger.error(f"获取属性失败: {selector} -> {name} -> {e}")
            raise e

    def inner_text(self, selector: str) -> str:
        try:
            text = self.locator(selector).inner_text()
            logger.info(f"获取内部文本: {selector} -> {text}")
            return text
        except Exception as e:
            logger.error(f"获取内部文本失败: {selector} -> {e}")
            raise e

    def text_content(self, selector: str) -> Optional[str]:
        try:
            content = self.locator(selector).text_content()
            logger.info(f"获取文本内容: {selector} -> {content}")
            return content
        except Exception as e:
            logger.error(f"获取文本内容失败: {selector} -> {e}")
            raise e

    def input_value(self, selector: str) -> str:
        try:
            value = self.locator(selector).input_value()
            logger.info(f"获取输入值: {selector} -> {value}")
            return value
        except Exception as e:
            logger.error(f"获取输入值失败: {selector} -> {e}")
            raise e

    def is_checked(self, selector: str) -> bool:
        try:
            checked = self.locator(selector).is_checked()
            logger.info(f"检查选中状态: {selector} -> {checked}")
            return checked
        except Exception as e:
            logger.error(f"检查选中状态失败: {selector} -> {e}")
            raise e

    def is_disabled(self, selector: str) -> bool:
        try:
            disabled = self.locator(selector).is_disabled()
            logger.info(f"检查禁用状态: {selector} -> {disabled}")
            return disabled
        except Exception as e:
            logger.error(f"检查禁用状态失败: {selector} -> {e}")
            raise e

    def is_editable(self, selector: str) -> bool:
        try:
            editable = self.locator(selector).is_editable()
            logger.info(f"检查可编辑状态: {selector} -> {editable}")
            return editable
        except Exception as e:
            logger.error(f"检查可编辑状态失败: {selector} -> {e}")
            raise e

    def is_enabled(self, selector: str) -> bool:
        try:
            enabled = self.locator(selector).is_enabled()
            logger.info(f"检查启用状态: {selector} -> {enabled}")
            return enabled
        except Exception as e:
            logger.error(f"检查启用状态失败: {selector} -> {e}")
            raise e

    def is_hidden(self, selector: str) -> bool:
        try:
            hidden = self.locator(selector).is_hidden()
            logger.info(f"检查隐藏状态: {selector} -> {hidden}")
            return hidden
        except Exception as e:
            logger.error(f"检查隐藏状态失败: {selector} -> {e}")
            raise e

    def is_visible(self, selector: str) -> bool:
        try:
            visible = self.locator(selector).is_visible()
            logger.info(f"检查可见状态: {selector} -> {visible}")
            return visible
        except Exception as e:
            logger.error(f"检查可见状态失败: {selector} -> {e}")
            raise e

    def count(self, selector: str) -> int:
        try:
            count = self.locator(selector).count()
            logger.info(f"获取元素数量: {selector} -> {count}")
            return count
        except Exception as e:
            logger.error(f"获取元素数量失败: {selector} -> {e}")
            raise e

    def all_inner_texts(self, selector: str) -> List[str]:
        try:
            texts = self.locator(selector).all_inner_texts()
            logger.info(f"获取所有内部文本: {selector} -> {len(texts)} 个元素")
            return texts
        except Exception as e:
            logger.error(f"获取所有内部文本失败: {selector} -> {e}")
            raise e

    def all_text_contents(self, selector: str) -> List[str]:
        try:
            contents = self.locator(selector).all_text_contents()
            logger.info(f"获取所有文本内容: {selector} -> {len(contents)} 个元素")
            return contents
        except Exception as e:
            logger.error(f"获取所有文本内容失败: {selector} -> {e}")
            raise e

    def set_input_files(self, selector: str, files: str):
        try:
            upload = self.locator(selector)
            upload.set_input_files(files)
            logger.info(f"设置文件输入: {selector} -> {files}")
        except Exception as e:
            logger.error(f"设置文件输入失败: {selector} -> {files} -> {e}")
            raise e

    def clear(self, selector: str):
        try:
            self.locator(selector).fill("")
            logger.info(f"清空输入: {selector}")
        except Exception as e:
            logger.error(f"清空输入失败: {selector} -> {e}")
            raise e

    def blur(self, selector: str):
        try:
            self.locator(selector).blur()
            logger.info(f"失去焦点: {selector}")
        except Exception as e:
            logger.error(f"失去焦点操作失败: {selector} -> {e}")
            raise e

    def tap(self, selector: str, **kwargs):
        try:
            self.locator(selector).tap(**kwargs)
            logger.info(f"触摸点击: {selector}")
        except Exception as e:
            logger.error(f"触摸点击失败: {selector} -> {e}")
            raise e

    def scroll_into_view_if_needed(self, selector: str, **kwargs):
        try:
            self.locator(selector).scroll_into_view_if_needed(**kwargs)
            logger.info(f"滚动到视图: {selector}")
        except Exception as e:
            logger.error(f"滚动到视图失败: {selector} -> {e}")
            raise e

    def select_text(self, selector: str, **kwargs):
        try:
            self.locator(selector).select_text(**kwargs)
            logger.info(f"选择文本: {selector}")
        except Exception as e:
            logger.error(f"选择文本失败: {selector} -> {e}")
            raise e

    def set_checked(self, selector: str, checked: bool, **kwargs):
        try:
            self.locator(selector).set_checked(checked, **kwargs)
            logger.info(f"设置选中状态: {selector} -> {checked}")
        except Exception as e:
            logger.error(f"设置选中状态失败: {selector} -> {checked} -> {e}")
            raise e

    def mock_api(self, url_pattern: str, response: Dict, method: str = "GET"):
        try:
            def handle_route(route):
                route.fulfill(
                    status=200,
                    content_type="application/json",
                    body=json.dumps(response)
                )

            self.page.route(url_pattern, handle_route)
            logger.info(f"模拟API: {method} {url_pattern}")
        except Exception as e:
            logger.error(f"模拟API失败: {method} {url_pattern} -> {e}")
            raise e

    def unmock_api(self, url_pattern: str):
        try:
            self.page.unroute(url_pattern)
            logger.info(f"取消模拟API: {url_pattern}")
        except Exception as e:
            logger.error(f"取消模拟API失败: {url_pattern} -> {e}")
            raise e