#gui dep
from PyQt5 import uic
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QMainWindow, QLineEdit,
            QProgressBar, QMessageBox, QHBoxLayout, QVBoxLayout, QWidget, QLabel,
            QMessageBox, QToolButton, QComboBox, QErrorMessage, qApp)
from PyQt5.QtCore import (QFile, QPoint, QRect, QSize,
        Qt, QProcess, QThread, pyqtSignal, pyqtSlot, Q_ARG , Qt, QMetaObject, QObject)
from PyQt5.QtGui import QIcon, QFont, QClipboard, QPixmap, QImage
import speedtest, time, sched, sys, os, sqlite3
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
speedtest_gui = resource_path("gui/main.ui")
conn = sqlite3.connect(resource_path('db/results.db'))
print("Opened database successfully")

s = speedtest.Speedtest()
print(s.get_best_server())
print(s.download())
print(s.upload())