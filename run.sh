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
echo "pip install -r ./requirements.txt --break-system-packages"
pip install -r ./requirements.txt --break-system-packages


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

python3 ./RunMain/run.py

