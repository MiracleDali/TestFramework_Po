"""
# file:     Base/baseYaml.py
# yaml,文件读写
"""

import yaml
import os

def read_yaml(yaml_path):
    """
    读取yaml文件
    :param yaml_path: yaml文件的真实路径
    :return: [{}, {}]
    """
    if not os.path.isfile(yaml_path):
        raise FileNotFoundError(f"文件路径不存在，请检查路径是否正确: {yaml_path}")

    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            cfg = f.read()
    except UnicodeDecodeError as e:
        raise ValueError("文件编码异常, 请确认是否为合法的UTF-8文件") from e

    content = yaml.load(cfg, Loader=yaml.FullLoader)
    return content

def write_yaml(yaml_path, data):
    """
    写入yaml文件
    :param yaml_path: yaml文件的真实路径
    :param data: 写入的数据
    :return:
    """
    try:
        with open(yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(data=data, stream=f, allow_unicode=True)
    except OSError as e:
        print(f"文件操作错误: {e}")
    except yaml.YAMLError as e:
        print(f"YAML序列化失败: {e}")
    except UnicodeEncodeError as e:
        print(f"编码错误: 数据包含无法用UTF-8编码的字符: {e}")
    except (TypeError, ValueError) as e:
        print(f"数据格式错误: {e}")
    except Exception as e:
        print(f"未知错误: {e}")
    else:
        print("YAML文件保存成功！")




if __name__ == '__main__':
    print(read_yaml(r'D:\2_python_file\TestFramework_Po\Data\DataDriver\YamlDriver\p01_client_xsglxt\02学生管理系统注册.yaml'))