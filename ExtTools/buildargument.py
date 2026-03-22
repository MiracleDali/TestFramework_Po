"""
# file:     Base/utils.py
# 读取-配置文件.ini
# 打包zip文件
"""

import sys
import argparse
from pathlib import Path
# 获取当前文件的父目录的父目录（项目根目录）
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
# print(sys.path)

from configparser import RawConfigParser
from Base.basePath import BasePath


def read_config_ini(config_path):
    """ 读取-配置文件.ini """
    config = RawConfigParser()    # 创建RawConfigParser对象
    config.read(config_path, encoding='utf-8')
    return config

def print_all_config(config_path):
    """ 打印整个配置文件的内容 """
    config = read_config_ini(config_path)
    
    print("=" * 60)
    print("配置文件内容:")
    print("=" * 60)
    
    # 遍历所有section
    for section_name in config.sections():
        print(f"[{section_name}]")
        
        # 遍历section中的所有选项
        for option in config.options(section_name):
            value = config.get(section_name, option)
            print(f"{option} = {value}")
        
        print()  # 空行分隔
    
    print("=" * 60)

def write_config_ini(config_path, *args, **kwargs):
    """ 写入-配置文件.ini """
    config = RawConfigParser()    
    config.read(config_path, encoding='utf-8')

    mappings = {
        'NGINX_HOST': ('nginx配置', 'host'),
        'NGINX_PORT': ('nginx配置', 'port'),
        'NGINX_USER': ('nginx配置', 'user'),
        'NGINX_ALLURE_PATH': ('nginx配置', 'allure_path'),
        'AUTO_TYPE': ('项目运行设置', 'AUTO_TYPE'),
        'REPORT_TYPE': ('项目运行设置', 'REPORT_TYPE'),
        'DATA_DRIVER_TYPE': ('项目运行设置', 'DATA_DRIVER_TYPE'),
        'TEST_PROJECT': ('项目运行设置', 'TEST_PROJECT'),
        'TEST_URL': ('项目运行设置', 'TEST_URL'),
        'SEND_REPORT_NGINX': ('项目运行设置', 'SEND_REPORT_NG')
    }
    
    for key, value in kwargs.items():
        if value is not None:  # 只更新非None的值
            if key in mappings:
                section, option = mappings[key]
                # 确保section存在
                if not config.has_section(section):
                    config.add_section(section)
                config.set(section, option, str(value))
                print(f"已更新: [{section}] {option} = {value}")
            else:
                print(f"警告: 未找到参数映射 {key}")
    
    # 写入文件
    with open(config_path, 'w', encoding='utf-8') as f:
        config.write(f)
    
    print("配置文件更新完成")
    


def main():
    parser = argparse.ArgumentParser(
        description='构建参数配置工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
                    示例:
                    python buildargument.py --env test
                    python buildargument.py --config ./config.ini --env prod
                '''
    )
    
    parser.add_argument('-nghost', '--nginx_host', type=str, help='nginx的IP地址')
    parser.add_argument('-ngport', '--nginx_port', type=str)
    parser.add_argument('-nguser', '--nginx_user', type=str)
    parser.add_argument('-ngpath', '--nginx_allure_path', type=str)
    parser.add_argument('-auto', '--auto_type', type=str)
    parser.add_argument('-report', '--report_type', type=str)
    parser.add_argument('-ddtype', '--data_driver_type', type=str)
    parser.add_argument('-project', '--test_project', type=str)
    parser.add_argument('-url', '--test_url', type=str)
    parser.add_argument('-srnginx', '--send_report_nginx', type=str)
    
    args = parser.parse_args()

    config_args = {    
        'NGINX_HOST': args.nginx_host,
        'NGINX_PORT': args.nginx_port,
        'NGINX_USER': args.nginx_user,
        'NGINX_ALLURE_PATH': args.nginx_allure_path,
        'AUTO_TYPE': args.auto_type,
        'REPORT_TYPE': args.report_type,
        'DATA_DRIVER_TYPE': args.data_driver_type,
        'TEST_PROJECT': args.test_project,
        'TEST_URL': args.test_url,
        'SEND_REPORT_NGINX': args.send_report_nginx
    }
    print(config_args)

    write_config_ini(config_path=BasePath.CONFIG_FILE, **config_args)
    config = read_config_ini(BasePath.CONFIG_FILE)
    print_all_config(BasePath.CONFIG_FILE)
    

if __name__ == '__main__':
    main()