"""
Brandmeister DMR Monitor for Korean Talkgroups

Author: Chanyeol Yoo (VK2CYO)
Copyright: Chanyeol Yoo, Ph.D. (VK2CYO), 2020
License: MIT
Version: v1.4
Maintainer: Chanyeol Yoo (VK2CYO)
Email: vk2cyo@gmail.com
URL: https://github.com/chanyeolyoo/BMRMonitor

Copyright (c) 2021 Chanyeol Yoo, Ph.D. (VK2CYO)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import sys
from PyQt5 import QtWidgets, QtCore, QtGui, uic
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
from numpy import random
import time
import webbrowser
import requests

tgs = [450, 45021, 45022, 45023, 45024, 45025, 45026, 45027, 45028, 45029]
VERSION = 1.4
IS_TEST = False
NUM_PADD = 50

def check_update():
    try:
        text_release = requests.get('https://api.github.com/repos/chanyeolyoo/BMRMonitor/releases/latest').text
        text_release = text_release.replace('false', 'False')
        text_release = text_release.replace('true', 'True')
        text_release = text_release.replace('null', 'None')
        resp_release = eval(text_release)
        tag_release = float(resp_release['tag_name'])
        print(tag_release)
        if (tag_release > VERSION) or (tag_release >= VERSION and IS_TEST):
            is_update_available = True
        else:
            is_update_available = False
        url_git = resp_release['html_url']
    except:
        is_update_available = False
        url_git = 'https://github.com/chanyeolyoo/BMRMonitor'
    is_update_available = is_update_available

    return is_update_available, url_git

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, monitor):
        super().__init__()
        uic.loadUi("qt.ui", self)

        self.monitor = monitor

        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        self.setFixedSize(self.size())

        self.label_version.setText(f'v{VERSION}')

        header = self.tableWidget_tgs.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)

        for tg in tgs:
            rowPos = self.tableWidget_tgs.rowCount()
            self.tableWidget_tgs.insertRow(rowPos)
            self.tableWidget_tgs.setItem(rowPos, 0, QtWidgets.QTableWidgetItem(str(tg)))   
            self.tableWidget_tgs.setItem(rowPos, 1, QtWidgets.QTableWidgetItem(str('')))   
            self.tableWidget_tgs.setItem(rowPos, 2, QtWidgets.QTableWidgetItem(str('')))   

        self.checkBox_alwaysontop.stateChanged.connect(self.checkBox_alwaysontop_changed)

        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update)

        is_update_available, url_git = check_update()
        def open_webbrowser():
            webbrowser.open(url_git)
        self.pushButton_github.clicked.connect(open_webbrowser)
        if is_update_available:
            self.pushButton_github.setText('업데이트 가능')
            self.pushButton_github.setStyleSheet("background-color: green")
        else:
            self.pushButton_github.setText('GitHub')
    
    def checkBox_alwaysontop_changed(self, state):
        if state == Qt.Checked:
            self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowStaysOnTopHint)
        self.show()

    def update(self):
        if not self.monitor.is_alive():
            for rowPos in range(self.tableWidget_tgs.rowCount()):
                self.tableWidget_tgs.item(rowPos, 1).setText(str(random.rand()))
                self.tableWidget_tgs.item(rowPos, 2).setText(str(random.rand()))
        else:
            now = time.time()
            for rowPos, tg in enumerate(self.monitor.history_tgs):
                text_active = ''
                text_inactive = ''

                history_tg = self.monitor.history_tgs[tg]
                try:
                    text_inactive = ''
                    for d in history_tg:
                        if now - d['Stop'] < self.monitor.timeout:
                            text_inactive = text_inactive + ('%s (%ds), ' % (d['SourceCall'], now - d['Stop']))
                    text_inactive = text_inactive

                    if history_tg[0]['Stop'] == 0:
                        elapsed = now-history_tg[0]['Start']
                        text_active = '%s, %s (%ds) ' % (history_tg[0]['SourceCall'], history_tg[0]['SourceName'], elapsed)
                except Exception as e:
                    pass

                if len(text_active) > 0:
                    self.tableWidget_tgs.item(rowPos, 0).setBackground(QColor(0, 255, 0))
                    self.tableWidget_tgs.item(rowPos, 1).setBackground(QColor(0, 255, 0))
                    self.tableWidget_tgs.item(rowPos, 2).setBackground(QColor(0, 255, 0))
                elif len(text_inactive) > 0:
                    self.tableWidget_tgs.item(rowPos, 0).setBackground(QColor(255, 255, 0))
                    self.tableWidget_tgs.item(rowPos, 1).setBackground(QColor(255, 255, 0))
                    self.tableWidget_tgs.item(rowPos, 2).setBackground(QColor(255, 255, 0))
                else:
                    self.tableWidget_tgs.item(rowPos, 0).setBackground(QColor(255, 255, 255))
                    self.tableWidget_tgs.item(rowPos, 1).setBackground(QColor(255, 255, 255))
                    self.tableWidget_tgs.item(rowPos, 2).setBackground(QColor(255, 255, 255))

                # self.tableWidget_tgs.item(rowPos, 1).setText(text_active)
                self.tableWidget_tgs.item(rowPos, 1).setText(text_active.ljust(NUM_PADD))
                self.tableWidget_tgs.item(rowPos, 2).setText(text_inactive)

    def show(self):
        super().show()
        self.timer.start()

    def closeEvent(self, event):
        print('closed')
        self.monitor.stop()


from monitor import Monitor
monitor = Monitor(tgs)
monitor.start()

app = QtWidgets.QApplication(sys.argv)
window = MainWindow(monitor)
window.show()
app.exec_()