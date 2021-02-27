import sqlite3, sys, os, threading
from speedtest import Speedtest
from PyQt5 import uic
from PyQt5.QtCore import Qt, QFile
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QHeaderView, QPushButton, QSizePolicy, QTableWidget, 
                            QVBoxLayout, QTableWidgetItem, 
                            QWidget, QApplication)

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)

def createDB():
    conn = sqlite3.connect('speed.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS speedtest(
                    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    download INTEGER, 
                    upload INTEGER, 
                    ping INTEGER,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
                )''')
    conn.commit()
    conn.close()

speedGUI = resource_path('./gui/main.ui')
createDB()
logo = resource_path('./gui/logo.png')
s = Speedtest()
mbps = 1000000

class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.resize(400,250)
        self.setWindowTitle('pythonexplainedto.me speedtest-result')

        self.table = QTableWidget()
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.refresh = QPushButton()
        self.refresh.setText("Refresh data")
        self.refresh.clicked.connect(lambda: self.result())
        hbox = QVBoxLayout(self)
        hbox.addWidget(self.refresh)
        hbox.addWidget(self.table)

        self.result()

    def result(self, values=None):
        self.table.clear()
        self.connection = sqlite3.connect("speed.db")
        self.connection.commit()
        cursor = self.connection.cursor()
        if values is None:
            cursor.execute("SELECT download,upload,ping,date FROM speedtest")
        else:
            cursor.execute("SELECT download,upload,ping,date FROM speedtest", values)

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

class Speedtest(QWidget):
    def __init__(self):
        super(Speedtest, self).__init__()
        UIFile = QFile(speedGUI)
        UIFile.open(QFile.ReadOnly)
        uic.loadUi(UIFile, self)
        UIFile.close()

        w = Window()

        self.startTest.clicked.connect(lambda: self.worker())
        self.oldTest.clicked.connect(lambda: w.show())

    def worker(self):
        """start a thread"""
        t = threading.Thread(target=self.speeddb())
        t.start()

    def updateLabel(self, upload, download, ping):
        
        self.downResult.clear()
        self.upResult.clear()
        self.pingResult.clear()

        self.downResult.setText(f"{download} mbps")
        self.upResult.setText(f"{upload} mbps")
        self.pingResult.setText(f"{ping} ms")

    def speeddb(self):
        """runs a speedtest to the closest server 
        and then inserts the value to the database"""
        conn = sqlite3.connect('speed.db')
        c = conn.cursor()
        s.get_best_server()
        s.download(threads=64)
        s.upload(threads=64)
        data = (int(s.results.download//mbps),
                int(s.results.upload//mbps),
                int(s.results.ping))
        c.execute('''INSERT INTO speedtest 
                    (download, upload, ping) 
                    VALUES (?,?,?)''',
                    data)
        self.updateLabel(str(s.results.upload//mbps),str(s.results.download//mbps),str(s.results.ping))
        conn.commit()
        conn.close()

app = QApplication(sys.argv)
app.setWindowIcon(QIcon(logo))
ex = Speedtest()
ex.show()
sys.exit(app.exec_())


