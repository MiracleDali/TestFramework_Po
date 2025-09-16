"""
# file:     Base/baseAutoWebPw.py
# WEB自动化
"""

import sys
import pathlib
# 获取当前文件的父目录的父目录（项目根目录）
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

import time
import os
import json
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
from Base.baseData import DataBase
from Base.baseLogger import Logger
logger = Logger('Base/baseAutoWebPw.py').getLogger()


class BaesWebPw(DataBase):
    """
    BaesWebPw - Playwright 操作基类（同步 API）
    设计目标：
      - 将常用 web 操作（导航、元素交互、等待、下载/上传、cookie、mock、执行 JS 等）
        封装为易用方法，方便在 pytest 的测试用例中直接调用。
      - 支持两种模式：由 BaesWebPw 管理 Playwright 生命周期（默认）或包装已有 page/context。
    """

    def __init__(
        self,
        accept_downloads: bool = True,  # 新建 context 时是否允许下载（默认允许）
        slow_mo: Optional[int] = None,  # 启动浏览器时的 slow_mo，用于调试（单位 ms）
        args: Optional[List[str]] = None,  # 浏览器启动参数列表，例如 ["--no-sandbox"]
        manage_playwright: bool = True,  # 是否由本类管理 Playwright 的生命周期（默认 True）
        yaml_name = None
    ):
        super().__init__(yaml_name)
        """
        如果传入 existing_page，则 BaesWebPw 仅做包装（manage_playwright=False 推荐）。
        """
        # 初始化内部变量并添加类型注解，初始值为 None 或传入值
        self._pw: Optional[Playwright] = None  # Playwright 实例（仅在 managed 时存在）
        self.browser: Optional[Browser] = None  # 浏览器实例（chromium/firefox/webkit）
        self.context: Optional[BrowserContext] = None  # 浏览器上下文（用于隔离数据）
        self.page: Optional[Page] = None  # 当前操作的 Page 对象
        self.managed = manage_playwright  # 标记是否由本类管理 Playwright 生命周期

