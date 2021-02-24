import sqlite3, sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QHeaderView, QSizePolicy, QTableWidget, 
                            QHBoxLayout, QTableWidgetItem, 
                            QWidget, QApplication)

class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.resize(350,250)
        self.setWindowTitle('pythonexplainedto.me speedtest-result')

        self.table = QTableWidget()
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        hbox = QHBoxLayout(self)
        hbox.addWidget(self.table)
        
        self.connection = sqlite3.connect("speed.db")
        self.result("SELECT download,upload,ping,date FROM speedtest")

    def result(self, query, values=None):
        cursor = self.connection.cursor()
        if values is None:
            cursor.execute(query)
        else:
            cursor.execute(query, values)

        name_of_columns = [e[0] for e in cursor.description]
        self.table.setColumnCount(len(name_of_columns))
        self.table.setRowCount(0)
        self.table.setHorizontalHeaderLabels(name_of_columns)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)  

        for i, row_data in enumerate(cursor.fetchall()):
            self.table.insertRow(self.table.rowCount())
            for j, value in enumerate(row_data):
                item = QTableWidgetItem()
                item.setData(Qt.DisplayRole, value)
                self.table.setItem(i, j, item)

app = QApplication(sys.argv)
app.setWindowIcon(QIcon('./gui/logo.png'))
ex = Window()
ex.show()
sys.exit(app.exec_())


