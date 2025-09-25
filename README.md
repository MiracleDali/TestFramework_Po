# TestFramework_Po

#### 介绍
一个专注于测试框架开发的开源项目，旨在提供高效、灵活的测试解决方案，支持Po设计模式，适用于多种测试场景。

#### 软件架构
1. 支持[API, UI, CLIENT]多种测试场景
2. 支持[Selenium, Pytest, Requests, Playwright]多种测试工具
3. 使用[Po]设计模式
4. 驱动数据-测试数据分离


#### 安装教程
1.  pip install -r .\requirements.txt  安装依赖包
2.  Python3.13 环境
3.  推荐使用 .venv 虚拟环境


#### 使用说明
1. python run.py                        # 运行所有用例
2. python run.py -m smoke               # 运行标记为 "smoke" 的用例
3. python run.py -m "smoke or ui"       # 运行标记为 "smoke" 或 "ui" 的用例
4. python run.py -m "not smoke"         # 运行标记不为 "smoke" 的用例
5. python run.py -m "(smoke or api) and not slow"    # 运行标记为 "smoke" 或 "api"，且不包含 "slow" 的用例

#### 参与贡献
1.  Fork 本仓库
2.  新建 Feat_xxx 分支
3.  提交代码
4.  新建 Pull Request


#### 特技
1.  使用 Readme\_XXX.md 来支持不同的语言，例如 Readme\_en.md, Readme\_zh.md
