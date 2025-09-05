import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QToolBar,  
                               QWidget, QTreeWidget, QTreeWidgetItem, QScrollArea, QVBoxLayout) 
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction

import sys
from pathlib import Path
# 获取当前文件的父目录的父目录（项目根目录）
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
 
from Base.baseYaml  import read_yaml, write_yaml
from Base.basePath  import BasePath as BP
 
 
class MainWindow(QMainWindow):
    def __init__(self, data):
        super(MainWindow, self).__init__()
        tbar = self.addToolBar('Driver') 
        submitAct = QAction('提交', self)
        selectAll = QAction('全选', self)
        selectAllCancel = QAction('取消全选', self)
        submitAct.triggered.connect(self.go) 
        selectAll.triggered.connect(self.select_all) 
        selectAllCancel.triggered.connect(self.select_all_cancel) 
        tbar.addActions([submitAct,  selectAll, selectAllCancel])
        self.root_list  = []
        w = QWidget()
        self.setCentralWidget(w) 
        self.topFiller  = QWidget()
        self.tree  = QTreeWidget()
        self.tree.setColumnCount(2) 
        self.tree.setHeaderLabels([' 用例名称', '用例函数'])
        self.tree.setColumnWidth(0,  400)
        self.tree.clicked.connect(self.select_child) 
 
        for i, k in enumerate(data):
            root = QTreeWidgetItem(self.tree) 
            root.setText(0,  data[k]['comment'])
            root.setCheckState(0,  Qt.Checked)
            self.root_list.append((root,  k))
            for v in data[k]:
                if v == "comment":
                    continue
                checkbox_child = QTreeWidgetItem(root)
                checkbox_child.setText(0,  data[k][v])
                checkbox_child.setText(1,  v)
                checkbox_child.setCheckState(0,  Qt.Checked)
 
        self.tree.itemChanged.connect(self.select_child) 
        # 创建一个滚动条
        self.scroll  = QScrollArea()
        self.scroll.setWidget(self.tree) 
        self.tree.setMinimumSize(800,  800)  # 设置滚动条的尺寸
        self.vbox  = QVBoxLayout()
        self.vbox.addWidget(self.scroll) 
        w.setLayout(self.vbox) 
        self.statusBar().showMessage("Star*") 
        self.resize(600,  800)
 
    def select_child(self, *args):
        if len(args) != 2:
            return
        item, column = args 
        count = item.childCount() 
        if item.checkState(column)  == Qt.Checked:
            for f in range(count):
                if item.child(f).checkState(0)  != Qt.Checked:
                    item.child(f).setCheckState(0,  Qt.Checked)
        if item.checkState(column)  == Qt.Unchecked:
            for f in range(count):
                if item.child(f).checkState(0)  != Qt.Unchecked:
                    item.child(f).setCheckState(0,  Qt.Unchecked)
 
    def select_all(self):
        for item, value in self.root_list: 
            item.setCheckState(0,  Qt.Checked)
 
    def select_all_cancel(self):
        for item, value in self.root_list: 
            item.setCheckState(0,  Qt.Unchecked)
 
    def go(self):
        select = {}
        for item, value in self.root_list: 
            child_count = item.childCount() 
            select[value] = []
            for f in range(child_count):
                if item.child(f).checkState(0)  == Qt.Checked:
                    select[value].append(item.child(f).text(1)) 
            if not select[value]:
                del select[value]
        write_yaml(BP.TEST_CASES, select)
 
def run():
    data = read_yaml(BP.TEMP_CASES)
    app = QApplication(sys.argv) 
    mainwindow = MainWindow(data)
    mainwindow.setWindowTitle(' 自动化测试用例执行程序')
    mainwindow.show() 
    sys.exit(app.exec()) 
 
if __name__ == '__main__':
    run() 