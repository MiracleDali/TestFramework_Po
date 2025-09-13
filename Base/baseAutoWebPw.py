"""
# file:     Base/baseAutoWebPw.py
# WEB自动化
"""

import sys
import pathlib
# 获取当前文件的父目录的父目录（项目根目录）
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))


from playwright.sync_api import (
    sync_playwright,  # 启动/停止 Playwright 的入口（同步版本）
    Playwright,  # Playwright 类型，用于类型注解
    Browser,  # 浏览器类型注解（如 chromium/firefox/webkit 的浏览器实例）
    BrowserContext,  # 浏览器上下文类型注解（用于隔离 cookie / storage 等）
    Page,  # 页面类型注解（代表单个选项卡/页面）
    TimeoutError as PlaywrightTimeoutError,  # 将 Playwright 的超时异常重命名，方便捕获
    expect,  # Playwright 的断言工具（用于元素断言）
)

# 导入类型、工具函数与标准库
from typing import Optional, Dict, Any, Callable, List, Union  # 类型注解常用类型
import time  # 用于实现 sleep / 超时等待（简单封装）
import os  # 文件与路径操作的标准库
import json  # 将 Python 对象序列化为 JSON，用于 mock 返回体等
from Base.baseLogger import Logger
logger = Logger('Base/baseAutoWebPw.py').getLogger()


class BaesWebPw:
    """
    BaesWebPw - Playwright 操作基类（同步 API）
    设计目标：
      - 将常用 web 操作（导航、元素交互、等待、下载/上传、cookie、mock、执行 JS 等）
        封装为易用方法，方便在 pytest 的测试用例中直接调用。
      - 支持两种模式：由 BaesWebPw 管理 Playwright 生命周期（默认）或包装已有 page/context。
    """

    def __init__(
        self,
        browser_type: str = "chromium",  # 'chromium' | 'firefox' | 'webkit'，默认使用 chromium
        headless: bool = True,  # 是否以 headless 模式启动浏览器（默认 True）
        viewport: Optional[Dict[str, int]] = None,  # 可选的视口大小，例如 {"width": 1280, "height": 720}
        accept_downloads: bool = True,  # 新建 context 时是否允许下载（默认允许）
        slow_mo: Optional[int] = None,  # 启动浏览器时的 slow_mo，用于调试（单位 ms）
        args: Optional[List[str]] = None,  # 浏览器启动参数列表，例如 ["--no-sandbox"]
        manage_playwright: bool = True,  # 是否由本类管理 Playwright 的生命周期（默认 True）
        existing_page: Optional[Page] = None,  # 如果传入现成的 page，则包装该 page（不管理生命周期）
        default_timeout: int = 30000,  # 默认超时时间，单位毫秒（Playwright 使用 ms）
    ):
        """
        如果传入 existing_page，则 BaesWebPw 仅做包装（manage_playwright=False 推荐）。
        """
        # 初始化内部变量并添加类型注解，初始值为 None 或传入值
        self._pw: Optional[Playwright] = None  # Playwright 实例（仅在 managed 时存在）
        self.browser: Optional[Browser] = None  # 浏览器实例（chromium/firefox/webkit）
        self.context: Optional[BrowserContext] = None  # 浏览器上下文（用于隔离数据）
        self.page: Optional[Page] = None  # 当前操作的 Page 对象
        self.managed = manage_playwright  # 标记是否由本类管理 Playwright 生命周期
        self._browser_type = browser_type  # 保存浏览器类型以便后续使用
        self.default_timeout = default_timeout  # 保存默认超时时间（毫秒）

        # 如果传入了现成的 Page 对象，则只做包装（不启动/停止 Playwright）
        if existing_page is not None:
            self.managed = False  # 既然有现成 page，我们就不管理 Playwright 生命周期
            self.page = existing_page  # 直接将现成的 page 绑定到实例
            self.context = existing_page.context  # 从 page 获取对应的 context
            logger.info("BaesWebPw: wrapped existing page (not managing playwright lifecycle).")  # 记录信息日志
            return  # 返回，构造函数结束

        # 如果需要由本类管理 Playwright，则在此启动 Playwright、创建浏览器和 context
        if self.managed:
            self._pw = sync_playwright().start()  # 启动 Playwright（同步 API）
            browser_launcher = getattr(self._pw, browser_type)  # 根据 browser_type 获取对应的启动函数
            launch_kwargs: Dict[str, Any] = {"headless": headless}  # 初始化启动参数字典，至少包含 headless

            # 如果 slow_mo 有值，则将其加入启动参数中（用于调试慢动作）
            if slow_mo:
                launch_kwargs["slow_mo"] = slow_mo

            # 如果有额外的启动参数（args），也加入到启动参数字典
            if args:
                launch_kwargs["args"] = args

            # 使用构造出的参数启动浏览器（chromium.launch(...)）
            self.browser = browser_launcher.launch(**launch_kwargs)
            # 准备创建 context 的参数：是否接受下载、视口设置等
            context_opts = {
                "accept_downloads": accept_downloads,
                "viewport": viewport,
            }
            # 删除字典中值为 None 的项，Playwright 在 new_context 时不希望接收 None 值
            context_opts = {k: v for k, v in context_opts.items() if v is not None}
            # 创建 browser context（与 browser 相互独立，便于隔离存储/cookie）
            self.context = self.browser.new_context(**context_opts)
            # 为新创建的 context 设置默认超时时间（针对 context 内的 page 操作）
            self.context.set_default_timeout(self.default_timeout)
            # 在 context 中新建一个 page（默认是第一个标签页）
            self.page = self.context.new_page()
            # 记录日志表示浏览器已成功启动
            logger.info(f"BaesWebPw: launched {browser_type} (headless={headless}).")

    # -------------------------
    # 生命周期相关方法
    # -------------------------
    def new_context(self, **kwargs) -> BrowserContext:
        """创建并返回一个新的 context（不替换当前 context）"""
        assert self.browser, "浏览器未启动"  # 若 browser 为空则抛 AssertionError
        return self.browser.new_context(**kwargs)  # 返回新创建的 context，参数可传入例如 viewport 等

    def new_page(self, context: Optional[BrowserContext] = None) -> Page:
        """在指定 context（或默认 context）中创建新的 Page 并返回"""
        ctx = context or self.context  # 如果未传 context，则使用当前实例的 context
        assert ctx, "browser context 未创建"  # 确保 context 存在，否则抛出 AssertionError
        return ctx.new_page()  # 在 context 中创建并返回新的 Page 对象

    def close(self):
        """优雅关闭 page/context/browser/playwright（如果是 managed）"""
        try:
            if self.page:
                try:
                    self.page.close()  # 关闭 page（如果存在）
                except Exception:
                    pass  # 忽略关闭 page 时的任何异常，继续关闭后续资源
            if self.context:
                try:
                    self.context.close()  # 关闭 context（如果存在）
                except Exception:
                    pass  # 忽略关闭 context 时的异常
            if self.browser:
                try:
                    self.browser.close()  # 关闭浏览器（如果存在）
                except Exception:
                    pass  # 忽略关闭 browser 时的异常
        finally:
            # 如果此实例管理 Playwright 的生命周期，则停止 Playwright（释放底层资源）
            if self.managed and self._pw:
                try:
                    self._pw.stop()  # 停止 Playwright（同步 API 的 stop）
                except Exception:
                    pass  # 忽略 stop 时的异常
            logger.info("BaesWebPw: closed browser/context/page (if managed).")  # 记录关闭完成日志

    def __enter__(self):
        # 支持 with 上下文管理器协议，返回自己以便在 with 块中使用
        return self

    def __exit__(self, exc_type, exc, tb):
        # 当 with 块结束或者抛出异常时，会调用此方法以确保资源被关闭
        self.close()

    # -------------------------
    # 低层辅助方法
    # -------------------------
    def _locator_of(self, selector_or_locator):
        """如果传入字符串 selector，则返回 page.locator(selector)；否则假定已经是 locator/element handle"""
        # 如果传入的参数是字符串类型，则认为是选择器，返回 page.locator(selector)
        if isinstance(selector_or_locator, str):
            return self.page.locator(selector_or_locator)
        # 否则直接返回参数（假定已经是 locator 或 element handle）
        return selector_or_locator

    def _safe_action(self, func: Callable, on_error_screenshot: Optional[str] = None):
        """
        执行 func，并在出现异常时（PlaywrightTimeoutError 或其他）尝试保存截图（如果指定路径）。
        func 是一个无参 callable。
        """
        try:
            return func()  # 尝试执行传入的函数并返回其结果
        except PlaywrightTimeoutError as e:
            # 捕获 Playwright 的超时异常，记录异常堆栈
            logger.exception("Playwright timeout error.")
            # 如果指定了错误截图路径，则尝试保存截图以便排查
            if on_error_screenshot:
                try:
                    self.take_screenshot(on_error_screenshot)  # 保存截图到指定路径
                    logger.info(f"screenshot saved to {on_error_screenshot}")  # 记录保存成功日志
                except Exception:
                    logger.exception("failed to save screenshot on timeout")  # 记录截图保存失败
            # 再次抛出异常以便调用方知道失败
            raise
        except Exception:
            # 捕获所有其它异常并记录
            logger.exception("Unexpected error in _safe_action")
            # 若指定错误截图路径，尝试保存截图
            if on_error_screenshot:
                try:
                    self.take_screenshot(on_error_screenshot)
                except Exception:
                    logger.exception("failed to save screenshot on error")
            # 重新抛出异常
            raise

    # -------------------------
    # 页面导航相关方法
    # -------------------------
    def goto(self, url: str, wait_until: str = "load", timeout: Optional[int] = None):
        """导航到 url。wait_until 可传 'load'|'domcontentloaded'|'networkidle' 等（Playwright 支持）"""
        # 使用 _safe_action 包装 page.goto，确保超时或错误时能截屏（如提供 on_error_screenshot）
        return self._safe_action(lambda: self.page.goto(url, wait_until=wait_until, timeout=timeout or self.default_timeout))

    def reload(self, timeout: Optional[int] = None):
        # 重新加载当前页面，默认使用实例的 default_timeout（毫秒）
        return self._safe_action(lambda: self.page.reload(timeout=timeout or self.default_timeout))

    def go_back(self, timeout: Optional[int] = None):
        # 浏览器后退操作，支持 timeout 参数
        return self._safe_action(lambda: self.page.go_back(timeout=timeout or self.default_timeout))

    def go_forward(self, timeout: Optional[int] = None):
        # 浏览器前进操作，支持 timeout 参数
        return self._safe_action(lambda: self.page.go_forward(timeout=timeout or self.default_timeout))

    def wait_for_load_state(self, state: str = "load", timeout: Optional[int] = None):
        # 等待页面达到指定的 load state（'load'、'domcontentloaded'、'networkidle' 等）
        return self._safe_action(lambda: self.page.wait_for_load_state(state=state, timeout=timeout or self.default_timeout))

    def title(self) -> str:
        # 返回当前页面的 title 字符串
        return self.page.title()

    def url(self) -> str:
        # 返回当前页面的 url（字符串）
        return self.page.url

    # -------------------------
    # 元素操作
    # -------------------------
    def click(
        self,
        selector: Union[str, Any],  # 选择器或 locator
        timeout: Optional[int] = None,  # 单次操作超时时间（毫秒）
        force: bool = False,  # 是否强制点击（忽略可见性/可交互性）
        position: Optional[Dict[str, int]] = None,  # 点击坐标相对于元素的位置，例如 {"x": 10, "y": 5}
        button: str = "left",  # 使用的鼠标按钮 'left'|'right'|'middle'
        click_count: int = 1,  # 点击次数（如双击 click_count=2）
        on_error_screenshot: Optional[str] = None,  # 出错时保存截图的路径（可选）
    ):
        # 获取 locator（若传入字符串则用 page.locator，否则直接使用传入对象）
        locator = self._locator_of(selector)
        # 使用 _safe_action 执行 locator.click，并传入可能的截图路径
        return self._safe_action(
            lambda: locator.click(timeout=timeout or self.default_timeout, force=force, position=position, button=button, click_count=click_count),
            on_error_screenshot=on_error_screenshot,
        )

    def dblclick(self, selector: Union[str, Any], timeout: Optional[int] = None, on_error_screenshot: Optional[str] = None):
        # 执行双击操作，使用 locator.dblclick 并包装到 _safe_action 中
        locator = self._locator_of(selector)
        return self._safe_action(lambda: locator.dblclick(timeout=timeout or self.default_timeout), on_error_screenshot=on_error_screenshot)

    def fill(self, selector: Union[str, Any], text: str, timeout: Optional[int] = None):
        # 将文本填入输入框（使用 locator.fill）
        locator = self._locator_of(selector)
        return self._safe_action(lambda: locator.fill(text, timeout=timeout or self.default_timeout))

    def type_text(self, selector: Union[str, Any], text: str, delay: Optional[float] = None, timeout: Optional[int] = None):
        # 使用模拟键入的方法输入文本（可以设置每个字符间的延迟 delay）
        locator = self._locator_of(selector)
        return self._safe_action(lambda: locator.type(text, delay=delay, timeout=timeout or self.default_timeout))

    def press(self, selector: Union[str, Any], key: str, timeout: Optional[int] = None):
        # 在元素上按下某个键（例如 "Enter"、"Tab"），使用 locator.press
        locator = self._locator_of(selector)
        return self._safe_action(lambda: locator.press(key, timeout=timeout or self.default_timeout))

    def hover(self, selector: Union[str, Any], timeout: Optional[int] = None):
        # 将鼠标悬停在指定元素上，使用 locator.hover
        locator = self._locator_of(selector)
        return self._safe_action(lambda: locator.hover(timeout=timeout or self.default_timeout))

    def select_option(self, selector: Union[str, Any], value: Optional[Union[str, List[str]]] = None, label: Optional[str] = None, index: Optional[int] = None):
        # 选择下拉框选项，支持通过 value、label 或 index 指定选中项
        locator = self._locator_of(selector)
        opts: Dict[str, Any] = {}  # 构造 select_option 支持的参数字典
        if value is not None:
            opts["value"] = value  # 按 value 值选择
        if label is not None:
            opts["label"] = label  # 按 label 选择
        if index is not None:
            opts["index"] = index  # 按索引选择
        return self._safe_action(lambda: locator.select_option(opts))

    def check(self, selector: Union[str, Any], timeout: Optional[int] = None):
        # 勾选 checkbox/radio（如果尚未勾选）
        locator = self._locator_of(selector)
        return self._safe_action(lambda: locator.check(timeout=timeout or self.default_timeout))

    def uncheck(self, selector: Union[str, Any], timeout: Optional[int] = None):
        # 取消勾选 checkbox（如果已勾选）
        locator = self._locator_of(selector)
        return self._safe_action(lambda: locator.uncheck(timeout=timeout or self.default_timeout))

    def is_visible(self, selector: Union[str, Any]) -> bool:
        # 返回元素是否可见（True/False）
        locator = self._locator_of(selector)
        return locator.is_visible()

    def is_enabled(self, selector: Union[str, Any]) -> bool:
        # 返回元素是否可交互 / 启用（True/False）
        locator = self._locator_of(selector)
        return locator.is_enabled()

    def is_checked(self, selector: Union[str, Any]) -> bool:
        # 返回 checkbox / radio 是否处于勾选状态
        locator = self._locator_of(selector)
        return locator.is_checked()

    def inner_text(self, selector: Union[str, Any]) -> str:
        # 返回元素的内部文本（不含 HTML 标签）
        locator = self._locator_of(selector)
        return locator.inner_text()

    def text_content(self, selector: Union[str, Any]) -> Optional[str]:
        # 返回元素的 textContent（可能为 None）
        locator = self._locator_of(selector)
        return locator.text_content()

    def get_attribute(self, selector: Union[str, Any], name: str) -> Optional[str]:
        # 获取元素的指定属性值（例如 'href'、'value' 等）
        locator = self._locator_of(selector)
        return locator.get_attribute(name)

    def count(self, selector: Union[str, Any]) -> int:
        # 返回匹配该选择器的元素数量（locator.count）
        locator = self._locator_of(selector)
        return locator.count()

    # -------------------------
    # Waiting & assertions
    # -------------------------
    def wait_for_selector(self, selector: str, state: str = "visible", timeout: Optional[int] = None):
        """
        state: 'attached' | 'detached' | 'visible' | 'hidden'
        """
        # 等待指定选择器出现/隐藏/附着/分离（具体行为由 state 决定）
        return self._safe_action(lambda: self.page.wait_for_selector(selector, state=state, timeout=timeout or self.default_timeout))

    def wait_for_timeout(self, ms: int):
        # 简单等待指定毫秒数（以阻塞方式 sleep）
        time.sleep(ms / 1000.0)  # 将毫秒转换为秒并调用 time.sleep

    def wait_for_response(self, url_or_predicate: Union[str, Callable], timeout: Optional[int] = None):
        # 等待满足条件的网络响应（可以传 URL 或 predicate 函数）
        if isinstance(url_or_predicate, str):
            # 如果是字符串，则按 URL 字符串匹配等待响应
            return self._safe_action(lambda: self.page.wait_for_response(url_or_predicate, timeout=timeout or self.default_timeout))
        else:
            # 如果是函数或其他可调用对象，则把它当作 predicate 使用
            return self._safe_action(lambda: self.page.wait_for_response(url_or_predicate, timeout=timeout or self.default_timeout))

    def expect_element_text(self, selector: Union[str, Any], expected: Union[str, List[str]], timeout: Optional[int] = None):
        # 使用 Playwright 的 expect() 断言工具来断言元素文本（支持字符串或字符串列表）
        locator = self._locator_of(selector)
        return expect(locator).to_have_text(expected, timeout=timeout or self.default_timeout)

    # -------------------------
    # JS / evaluation / frames
    # -------------------------
    def eval_on_selector(self, selector: str, expression: str, arg: Any = None):
        # 在指定选择器对应的元素上执行 document.querySelector(selector).<expression> 的评估
        return self.page.eval_on_selector(selector, expression, arg)

    def evaluate(self, expression: str, arg: Any = None):
        # 在页面上下文中执行任意 JS 表达式（字符串），并可传递参数 arg
        return self.page.evaluate(expression, arg)

    def frame(self, name_or_url: str):
        # 获取 frame（按 name 或者按 url 匹配）
        for f in self.page.frames:
            # 如果 frame 的 name 与传入相同，或者传入字符串出现在 frame.url 中，则返回该 frame
            if f.name == name_or_url or (name_or_url in (f.url or "")):
                return f
        # 如果没有匹配的 frame，则返回 None
        return None

    # -------------------------
    # File upload / download
    # -------------------------
    def upload_file(self, selector: str, *file_paths: str):
        """
        selector: 指向 input[type=file] 的选择器
        file_paths: 一个或多个文件路径
        """
        # 使用 page.set_input_files 将文件路径设置到 input[type=file] 元素，从而实现文件上传
        return self._safe_action(lambda: self.page.set_input_files(selector, list(file_paths)))

    def download_and_save(self, action: Callable, save_path: Optional[Union[str, pathlib.Path]] = None, timeout: Optional[int] = None):
        """
        action: 一个触发下载的函数（例如一个点击操作）
        返回: 保存后的文件完整路径（如果 save_as 被调用）
        用法:
            def trigger():
                page.click("a#download")
            path = download_and_save(trigger, "/tmp")
        """
        # 使用默认超时时间或传入的 timeout
        timeout = timeout or self.default_timeout
        # 使用 page.expect_download 上下文管理器等待下载触发
        with self.page.expect_download(timeout=timeout) as download_info:
            action()  # 执行触发下载的函数，例如点击下载按钮
        download = download_info.value  # 获取 Download 对象
        suggested = download.suggested_filename  # Playwright 建议的文件名（由响应或 URL 提供）
        if save_path:
            # 如果指定了 save_path，则将下载文件保存到指定的路径或目录
            target = pathlib.Path(save_path)
            if target.is_dir():
                # 如果传入的是目录，则使用建议文件名拼接成完整路径
                dest = str(target / suggested)
            else:
                # 如果传入的是具体文件名或不存在的路径，则直接当作目标路径
                dest = str(target)
            download.save_as(dest)  # 将下载文件保存为目标路径
            return dest  # 返回保存后的完整路径
        else:
            # 若未指定 save_path，则返回临时路径（download.path()）
            return str(download.path())

    # -------------------------
    # Network & mocking
    # -------------------------
    def set_extra_http_headers(self, headers: Dict[str, str]):
        # 设置请求的额外 HTTP headers，用于伪造 UA / token 等
        return self.page.set_extra_http_headers(headers)

    def route_mock(self, url_or_pattern: str, status: int = 200, body: Union[str, Dict] = "", headers: Optional[Dict[str, str]] = None):
        """
        简单的 mock：通过 route.fulfill 返回指定的响应（适合 mock API）
        """
        # 定义处理器函数，Playwright 在拦截到匹配请求时会调用该 handler
        def handler(route, request):
            b = body  # 默认 body 原样返回
            h = headers or {}  # 如果传入 headers，则使用；否则使用空字典
            if isinstance(body, (dict, list)):
                # 如果 body 是 Python 对象（字典或列表），将其序列化为 JSON 字符串并设置 Content-Type
                b = json.dumps(body)
                h.setdefault("Content-Type", "application/json; charset=utf-8")
            # 使用 route.fulfill 返回自定义的响应（status、body、headers）
            route.fulfill(status=status, body=b, headers=h)

        # 在 page 上注册路由拦截器（pattern 可以是字符串或正则等 Playwright 支持的模式）
        self.page.route(url_or_pattern, handler)
        logger.info(f"route_mock registered for {url_or_pattern}")  # 记录已注册 mock 路由

    def unroute(self, url_or_pattern: str):
        # 取消之前注册的路由拦截（停止 mock）
        self.page.unroute(url_or_pattern)
        logger.info(f"route removed for {url_or_pattern}")  # 记录已移除路由的日志

    # -------------------------
    # Cookie / storage
    # -------------------------
    def add_cookies(self, cookies: List[Dict[str, Any]]):
        """cookies: list of cookie dicts (name, value, domain, path, etc.)"""
        # 将 cookies 添加到当前 context（用于模拟已登录状态等）
        return self.context.add_cookies(cookies)

    def get_cookies(self, urls: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        # 获取 context 下的 cookies；可指定针对特定 url 的 cookies
        return self.context.cookies(urls or [])

    def clear_cookies(self, **filters):
        """可按 name/domain/path 过滤删除（若无参数则清除所有）"""
        # Playwright context 提供 clear_cookies，但注意 API 取决于 Playwright 版本
        return self.context.clear_cookies(**filters)

    def storage_state(self, path: Optional[str] = None) -> Dict[str, Any]:
        """获取 storage state（可传 path 保存）"""
        if path:
            # 如果传入 path，则将 storage state 写入该文件（并返回空字典表示已保存）
            self.context.storage_state(path=path)
            return {}
        # 否则返回当前 context 的 storage_state 字典（包括 cookies 与 localStorage 等）
        return self.context.storage_state()

    # -------------------------
    # Screenshot / element screenshot
    # -------------------------
    def take_screenshot(self, path: str, full_page: bool = False):
        # 将页面截图保存到指定路径（会自动创建目录）
        parent = os.path.dirname(path)  # 获取目标路径的父目录
        if parent and not os.path.exists(parent):
            os.makedirs(parent, exist_ok=True)  # 如果父目录不存在则创建（递归）
        return self.page.screenshot(path=path, full_page=full_page)  # 返回 Playwright 的 screenshot 结果（通常是 bytes 或 None）

    def element_screenshot(self, selector: Union[str, Any], path: str):
        # 对元素进行截图并保存到指定路径
        loc = self._locator_of(selector)  # 获取 locator 或直接使用传入的 locator
        parent = os.path.dirname(path)  # 获取父目录
        if parent and not os.path.exists(parent):
            os.makedirs(parent, exist_ok=True)  # 创建父目录（若不存在）
        return loc.screenshot(path=path)  # 使用 locator.screenshot 保存元素截图

    # -------------------------
    # Advanced actions
    # -------------------------
    def drag_and_drop(self, source_selector: str, target_selector: str, **options):
        """page.drag_and_drop or locator.drag_to"""
        # 直接调用 Playwright 的 page.drag_and_drop 方法实现拖放
        return self.page.drag_and_drop(source_selector, target_selector, **options)

    def dispatch_event(self, selector: str, event: str, event_options: Dict[str, Any] = None):
        # 在元素上触发自定义事件（例如 'input'、'change'、'keydown' 等），可传 event_options
        return self.page.dispatch_event(selector, event, event_options or {})

    # -------------------------
    # Utilities for pytest integration
    # -------------------------
    def attach_screenshot_to_allure(self, path: str, name: str = "screenshot"):
        """如果环境装了 allure-pytest，可以用来 attach（非强依赖）"""
        try:
            import allure  # 动态导入 allure，避免硬性依赖
            with open(path, "rb") as f:
                allure.attach(f.read(), name=name, attachment_type=allure.attachment_type.PNG)  # 将截图以二进制形式 attach 到 Allure 报告
        except Exception:
            # 如果导入失败或 attach 失败，则记录异常（例如没有安装 allure）
            logger.exception("attach to allure failed (maybe allure not installed)")

    # 可按需继续扩展：cookie 操作更复杂的 wrapper、JS 注入、trace/har 记录、video、viewport/geo/permissions 等。
    # 上述注释说明此类还有很多可扩展的方向，例如加入自动失败截图 Hook、HAR 导出、视频录制等功能。