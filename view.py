import sqlite3, sys, os
from speedtest import Speedtest
from PyQt5 import uic
from PyQt5.QtCore import QObject, QRunnable, Qt, QFile, QThreadPool, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (QHeaderView, QPushButton, QSizePolicy, QTableWidget, 
                            QVBoxLayout, QTableWidgetItem, 
                            QWidget, QApplication)

try:
    from PyQt5.QtWinExtras import QtWin
    myappid = 'speed.test.python.program'
    QtWin.setCurrentProcessExplicitAppUserModelID(myappid)    
except ImportError:
    pass

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
appbg = resource_path('./gui/bg.png')
s = Speedtest()
mbps = 1000000


class SpeedWindow(QWidget):
    def __init__(self):
        super(SpeedWindow, self).__init__()
        UIFile = QFile(speedGUI)
        UIFile.open(QFile.ReadOnly)
        uic.loadUi(UIFile, self)
        UIFile.close()

        self.bg = QPixmap(appbg)
        self.appbg.setPixmap(self.bg)

        self.Window = Window()
    
        self.startTest.clicked.connect(lambda: self.runTest())
        self.oldTest.clicked.connect(lambda: self.Window.show())

    def runTest(self):
        self.pool = QThreadPool.globalInstance()
        self.runnable = Worker()
        self.runnable.signals.result.connect(self.updateLabel)
        self.startTest.setDisabled(True)
        self.startTest.setText('Running Test...')
        self.pool.start(self.runnable)
        
    def updateLabel(self,data):
        download = data[0]
        upload = data[1]
        ping = data[2]

        self.downResult.clear()
        self.upResult.clear()
        self.pingResult.clear()
        self.downResult.setText(f"{download} mbps")
        self.upResult.setText(f"{upload} mbps")
        self.pingResult.setText(f"{ping} ms")
        self.startTest.setText("Speedtest")
        self.startTest.setDisabled(False)

class WorkerSignals(QObject):
    result = pyqtSignal(tuple)

class Worker(QRunnable):
    signals = WorkerSignals()

    def __init__(self):
        super(Worker, self).__init__()

    def run(self):
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
        conn.commit()
        conn.close()
        self.signals.result.emit(tuple(data))


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
            cursor.execute("SELECT download,upload,ping,date FROM speedtest ORDER BY id DESC")
        else:
            cursor.execute("SELECT download,upload,ping,date FROM speedtest ORDER BY id DESC", values)

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

style = '''
QLabel {
    color: #eeeeee;
}

QPushButton,
QLineEdit {
    background-color: #eeeeee;
    border: 3px;
    border-color: #000000;
    height: 20 px;
}
QPushButton:hover {
    color: #000000;
    selection-background-color: #222831;
    background-color: #FFFFFF;
}  
QPushButton:pressed {
    color: #000000;
    background-color: #EEEEEE;
}  
'''

app = QApplication(sys.argv)
app.setWindowIcon(QIcon(logo))
if os.name == 'nt':
    app.setStyleSheet(style)
else:
    pass
ex = SpeedWindow()
ex.show()
sys.exit(app.exec_())


