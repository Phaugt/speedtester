#gui dep
from PyQt5 import uic, QtSql
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QMainWindow, QLineEdit,
            QProgressBar, QMessageBox, QHBoxLayout, QVBoxLayout, QWidget, QLabel,
            QMessageBox, QToolButton, QComboBox, QErrorMessage, qApp, QToolBar,
            QStatusBar)
from PyQt5.QtCore import (QFile, QPoint, QRect, QSize, Qt,
            QProcess, QThread, pyqtSignal, pyqtSlot, Q_ARG , Qt, QMetaObject, QObject)
from PyQt5.QtGui import QIcon, QFont, QClipboard, QPixmap, QImage
import speedtest, time, sched, sys, os, sqlite3
from sqlite3 import Error
#icon taskbar
try:
    from PyQt5.QtWinExtras import QtWin
    myappid = 'youtube.python.download.program'
    QtWin.setCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass
#pyinstaller
def resource_path(relative_path):
  if hasattr(sys, '_MEIPASS'):
      return os.path.join(sys._MEIPASS, relative_path)
  return os.path.join(os.path.abspath('.'), relative_path)
# Import .ui forms for the GUI using function resource_path()
speedtest_gui = resource_path("./gui/main.ui")
config_gui = resource_path("./gui/config.ui")
sched_gui = resource_path("./gui/sched.ui")
speed_icon = resource_path('./icons/96_speed.png')
results_db = resource_path('./db/results.db')
#Db
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()
#UI
class UI(QMainWindow):
    def __init__(self):
        super(UI, self).__init__()
        self.c = Config()
        self.s = Schedule()
        UIFile = QFile(resource_path(speedtest_gui))
        UIFile.open(QFile.ReadOnly)
        uic.loadUi(UIFile, self)
        UIFile.close()
        self.createStatusBar()  
        #buttons
        self.actionConfig.triggered.connect(self.show_Config)
        self.actionConfig.setStatusTip("Change the configuration of the software")
        self.actionSchedule.triggered.connect(self.show_Schedule)
        self.actionSchedule.setStatusTip("Change the schedule of background tests")
        self.actionExit.triggered.connect(qApp.quit)
        self.actionExit.setStatusTip("Exit software")
        self.starttest.clicked.connect(self.cmdstarttest)
        self.starttest.setStatusTip("Start Download/Upload Speedtest from the closest server!")

        #speedtestthread
        self.speedtest = Speedtest()
        thread = QThread(self)
        thread.start()
        self.speedtest.moveToThread(thread)

        #table

    def showMessage(self, message):
        self.showMessage(message)

    def createStatusBar(self):
        self.statusBar().showMessage("Ready")
 
    def msgbox(self, message):
        QMessageBox.warning(self, "Message", message)
    
    def show_Config(self):
        self.c.show()


    def show_Schedule(self):
        self.s.show()

    
    @pyqtSlot()
    def cmdstarttest(self):
        s = speedtest.Speedtest()
        QMetaObject.invokeMethod(self.speedtest, "up_down_closest",
        Qt.QueuedConnection,
        Q_ARG(object, s))



    
class Speedtest(QObject):
    start = pyqtSignal(str)
    #speed_results = {"download": s.results,upload, ping, server, timestamp, bytes_sent, bytes_received, share, client, testtype}
    #create_connection(resource_path(results_db))
    #sqlite_insert_query = """INSERT INTO results(download, upload, ping, server, timestamp, bytes_sent, bytes_received, share, client, testtype) VALUES "?, ?, ?, ?, ?, ?, ?, ?, ?, ?"""
    @pyqtSlot(object)
    def up_down_closest(self, s):
        s.get_best_server()
        s.download()
        s.upload()
        speed_results = s.results
        #(speed_results.get('download'),speed_results.get('upload'),speed_results.get('ping'),speed_results.get('server'),speed_results.get('timestamp'),speed_results.get('bytes_sent'),speed_results.get('bytes_received'),speed_results.get('download'),"",speed_results.get('client'),"direct_test")

        try:
            sqliteConnection = sqlite3.connect(resource_path(results_db))
            cursor = sqliteConnection.cursor()
            print("Connected to SQLite")

            sqlite_insert_with_param = """INSERT INTO results 
            (download, upload, ping, server, timestamp, bytes_sent, bytes_received, share, client, testtype) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""
    
            #data_tuple = (speed_results.get('download'),speed_results.get('upload'),speed_results.get('ping'),speed_results.get('server'),speed_results.get('timestamp'),speed_results.get('bytes_sent'),speed_results.get('bytes_received'),speed_results.get('download'),"",speed_results.get('client'),"direct_test")
            data_tuple = (int(s.results.download),int(s.results.upload),int(s.results.ping),str(s.results.server),str(s.results.timestamp),int(s.results.bytes_sent),int(s.results.bytes_received),str(""),str(s.results.client),str("direct_test"))
            cursor.execute(sqlite_insert_with_param, data_tuple)
            sqliteConnection.commit()
            print("Python Variables inserted successfully into SqliteDb_developers table")

            cursor.close()

        except sqlite3.Error as error:
            print("Failed to insert Python variable into sqlite table", error)
        finally:
            if (sqliteConnection):
                sqliteConnection.close()
                print("The SQLite connection is closed")

#Config
class Config(QWidget):
    def __init__(self):
        super().__init__()
        UIFile = QFile(resource_path(config_gui))
        UIFile.open(QFile.ReadOnly)
        uic.loadUi(UIFile, self)
        UIFile.close()
#Schedule
class Schedule(QWidget):
    def __init__(self):
        super().__init__()
        UIFile = QFile(resource_path(sched_gui))
        UIFile.open(QFile.ReadOnly)
        uic.loadUi(UIFile, self)
        UIFile.close()


app = QApplication(sys.argv)
app.setWindowIcon(QIcon(resource_path(speed_icon)))
window = UI()
window.show()
app.exec_()