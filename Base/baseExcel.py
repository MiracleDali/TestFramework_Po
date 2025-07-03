"""
# file:     Base/baseExcel.py
# excel,文件读写
"""

import pandas as pd


class ExcelRead:
    def __init__(self, excel_path: str , sheet_name: str = "Sheet1"):
        self.table = pd.read_excel(excel_path, sheet_name)
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



if __name__ == "__main__":
    file_path = r'E:\TestFramework_Po\Data\DataDriver\ExcelDriver\project01_auto_test\1.xlsx'

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
    write.write_excel(file_path, 'Sheet1', d_02)

    # 读取excel
    data = ExcelRead(file_path, 'Sheet1')
    print('excel转换为字典信息,', data.dict_date())
    print('excel,行信息', data.get_row_info(1))
    print(data.get_col_info("name"))
    print(data.get_cell_info(1, "id"))







