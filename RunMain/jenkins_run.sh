#!bin/bash

nginx_host=${1}
nginx_port=${2}
nginx_user=${3}
nginx_allure_path=${4}
auto_type=${5}
report_type=${6}
data_driver_type=${7}
test_project=${8}
test_url=${9}
send_report_nginx=${10}

echo "############################################################"
echo "Installing Requirements..."
echo "############################################################"

# 在共享卷 /workspace 下创建一个虚拟环境 venv
# 虚拟环境可以隔离依赖，避免污染系统 Python
if [ ! -d "/workspace/venv" ]; then
    echo "创建 venv 虚拟环境到 /workspace/venv"
    python3 -m venv /workspace/venv || { echo "Failed to create virtual environment"; exit 1; }
fi
# 激活虚拟环境
# 激活后，pip 和 python 命令都会指向 /workspace/venv 里的环境
source /workspace/venv/bin/activate
pip install --upgrade pip
# 输出安装命令（可选，仅打印到日志中）
echo "pip install -r ./requirements.txt --upgrade"
# 安装 requirements.txt 中列出的第三方库到虚拟环境
# 依赖会被安装到 /workspace/venv/lib/python3.13/site-packages/
# 容器删除也不会影响共享卷里的虚拟环境
pip install -r ./requirements.txt --upgrade


echo "############################################################"
echo "Build Argument"
echo "############################################################"
python3 ./ExtTools/buildargument.py \
  --nginx_host "$nginx_host" \
  --nginx_port "$nginx_port" \
  --nginx_user "$nginx_user" \
  --nginx_allure_path "$nginx_allure_path" \
  --auto_type "$auto_type" \
  --report_type "$report_type" \
  --data_driver_type "$data_driver_type" \
  --test_project "$test_project" \
  --test_url "$test_url" \
  --send_report_nginx "$send_report_nginx"

echo "############################################################"
echo "Test Starting..."
echo "############################################################"
echo ""

# python3 ./RunMain/run.py
python3 ./RunMain/run.py

