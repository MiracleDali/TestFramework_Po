"""
# file:     Base/baseExcel.py
# excel,文件读写
"""

import sys
from pathlib import Path
Base_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(Base_dir))

import pandas as pd
from Base.basePath import BasePath as BP


class Excel_Csv_Edit:
    def __init__(self, file_path: str, sheet_name: str = None):

        if sheet_name:
            self.table = pd.read_excel(file_path, sheet_name)
        elif not sheet_name:
            self.table = pd.read_csv(file_path)

        # 获取第一行为key值
        self.keys = self.table.columns.tolist()
        # 获取行数和列数
        self.rows, self.cols = self.table.shape

    def dict_date(self):
        """ 将表格数据转换为字典列表，每行对应一个字典 """
        if self.rows < 1:
            print("总行数小于1")
            return []

        result = []
        for i in range(self.rows):
            row_dict = {
                self.keys[j]: self.table.iloc[i, j] for j in range(self.cols)
            }
            result.append(row_dict)
        # print('dict_date', result)
        return result

    def get_row_info(self, row):
        """
        获取excel中对应行信息，row--行数（int）
        从第一行开始
        """
        if row < 1:
            print("行数不能为0和负数")
            return []
        else:
            test_datas = self.dict_date()
            row_data = test_datas[row - 1]
            # print(行信息, row_data)
            return row_data

    def get_col_info(self, name):
        """ 获取excel中对应列信息，name--列名"""
        name_data = []
        if name not in self.keys:
            print("列名不存在")
            return []
        else:
            for i in range(self.rows):
                name_data.append(self.table.loc[i, name])
            return name_data

    def get_cell_info(self, row, name):
        """获取exl中某一单元格信息，row--行数（int）；name--列名(char)"""
        if row < 1:
            print("行数不能为0和负数")
            return []
        if row > self.rows:
            print("行数超出")
            return []
        if name not in self.keys:
            print("列名不存在")
            return []

        return self.table.loc[row - 1, name]


class ExcelWrite:
    def __init__(self):
        self.df = None   # 初始化dataframe为空

    def write_excel(self, excel_path: str, sheet_name: str, list_data):
        # 将list_data(字典列表)转换为dataframe
        self.df = pd.DataFrame(list_data)
        print(self.df)

        # 写入excel文件
        self.df.to_excel(
            excel_path,
            sheet_name=sheet_name,
            index=False,    # 不写入行索引
        )

    def write_csv(self, csv_path: str, list_data):
        # 将list_data(字典列表)转换为dataframe
        self.df = pd.DataFrame(list_data)
        # print(self.df)

        # 写入csv文件
        self.df.to_csv(
            csv_path,
            index=False,    # 不写入行索引
        )



if __name__ == "__main__":
    file_path = (Path(BP.DATA_DRIVER_DIR) / 'ExcelDriver' / 'p03_http_gjgl' / '01稿件系统登录.csv')
    # file_path = r'D:\2_python_file\TestFramework_Po\Data\DataDriver\ExcelDriver\p03_http_gjgl\01.csv'

    # 创建字典列表 可以使用下面两种方法进行创建
    d_01 = [
        {"id": 1, "name": "张三"},
        {"id": 2, "name": "张三"},
        {"id": 33, "name": "张三"},
    ]
    d_02 = ({
        "id": [i for i in range(1, 5)],
        "name": [f'name{i}' for i in range(1, 5)],
        "age": [i for i in range(21, 25)],
    })

    # 写入excel
    write = ExcelWrite()
    # write.write_excel(file_path, 'Sheet1', d_02)
    # 写入csv
    # write.write_csv(file_path, d_02)


    # 读取excel
    # data = Excel_Csv_Edit(file_path, 'Sheet1')
    # print('excel转换为字典信息,', data.dict_date())
    # print('excel,行信息', data.get_row_info(1))
    # print(data.get_col_info("name"))
    # print(data.get_cell_info(1, "id"))

    # 读取csv
    data = Excel_Csv_Edit(file_path)
    print('csv转换为字典信息,', data.dict_date())
    # print('excel,行信息', data.get_row_info(1))
    # print(data.get_col_info("name"))
    # print(data.get_cell_info(1, "id"))







