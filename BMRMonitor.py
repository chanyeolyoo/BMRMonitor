
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem
from gui import Ui_MainWindow

from gevent import monkey as curious_george
curious_george.patch_all(thread=False, select=False)

import threading
import time
import webbrowser

from utils import *
import talkgroups
from MonitorTalkgroups import MonitorTalkgroups


class DataStream():
    tgs = [[]]
    running = True
    def __init__(self, tgs, window):
        self.tgs = tgs
        self.window = window

        self.monitorTalkgroups = MonitorTalkgroups(self.tgs)
        self.monitorTalkgroups.start()

        self.update = threading.Thread(target=self.update_ui, args=(self.monitorTalkgroups,), daemon=True)
        self.update.start()

    def stop(self):
        self.running = False
        self.update.join()
        self.monitorTalkgroups.stop()

    def update_ui(self, monitorTalkgroups):
        while self.running:
            timenow = time.time()
            data_array = monitorTalkgroups.get()
            for i in range(len(data_array)):
                data = data_array[i]
                if data['status'] == 'inactive':
                    if timenow-data['last_active'] > 60:
                        self.window.set_item_white(i)
                    else:
                        self.window.set_item_yellow(i)
                elif data['status'] == 'active':
                    self.window.set_item_green(i)
                elif data['status'] == 'noconn':
                    self.window.set_item_red(i)

            # self.print_active(data_array)
            time.sleep(1)

    def print_active(self, data_array):
        for i in range(len(data_array)):
            data = data_array[i]
            tg = talkgroups.tgs[i]
            if data['status'] == 'active':
                print('TG%d: %s (%s)' % (tg['id'], data['status'], get_duration_str(int(time.time()-data['timestamp']))))


class MainWindow(QMainWindow):
    running = True

    def __init__(self):
        super(MainWindow, self).__init__()
        self.init_ui()

        self.data_stream = DataStream(talkgroups.tgs, self)

    def init_ui(self):
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())

        self.ui.githubButton.clicked.connect(self.github_clicked)
        self.ui.statusListWidget.itemDoubleClicked.connect(self.item_double_clicked)
        
        for tg in talkgroups.tgs:            
            line = self.get_line(tg)
            self.ui.statusListWidget.addItem(line)

    def get_line(self, tg):
        line = '[%s] %s' % (tg['id'], tg['name'])
        return line

    def item_double_clicked(self, item):
        idx = self.ui.statusListWidget.row(item)
        url = 'https://hose.brandmeister.network/group/' + str(talkgroups.tgs[idx]['id'])
        webbrowser.open(url)

    def github_clicked(self):
        webbrowser.open('https://github.com/chanyeolyoo/BMRMonitor')

    def closeEvent(self, event):
        self.data_stream.stop()
        event.accept()
    
    def refresh(self):
        self.hide()
        self.show()

    def set_item_bg(self, idx, c):
        # QtCore.Qt.green
        self.ui.statusListWidget.item(idx).setBackground(c)
        self.ui.statusListWidget.hide()
        self.ui.statusListWidget.show()

    def set_item_white(self, idx):
        self.set_item_bg(idx, QtCore.Qt.white)

    def set_item_green(self, idx):
        self.set_item_bg(idx, QtCore.Qt.green)

    def set_item_yellow(self, idx):
        self.set_item_bg(idx, QtCore.Qt.yellow)

    def set_item_red(self, idx):
        self.set_item_bg(idx, QtCore.Qt.red)

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()

    sys._excepthook = sys.excepthook 
    def exception_hook(exctype, value, traceback):
        print(exctype, value, traceback)
        sys._excepthook(exctype, value, traceback) 
        sys.exit(1) 
    sys.excepthook = exception_hook 

    sys.exit(app.exec_())