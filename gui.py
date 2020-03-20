# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(389, 674)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 620, 371, 20))
        self.label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.label.setObjectName("label")
        self.statusListWidget = QtWidgets.QListWidget(self.centralwidget)
        self.statusListWidget.setGeometry(QtCore.QRect(10, 10, 371, 601))
        self.statusListWidget.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.statusListWidget.setResizeMode(QtWidgets.QListView.Adjust)
        self.statusListWidget.setSelectionRectVisible(False)
        self.statusListWidget.setObjectName("statusListWidget")
        self.githubButton = QtWidgets.QPushButton(self.centralwidget)
        self.githubButton.setGeometry(QtCore.QRect(310, 620, 71, 23))
        self.githubButton.setObjectName("githubButton")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 389, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.actionVisit_GitHub_page = QtWidgets.QAction(MainWindow)
        self.actionVisit_GitHub_page.setObjectName("actionVisit_GitHub_page")
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Brandmeister KR Monitor"))
        self.label.setText(_translate("MainWindow", "Created by VK2FAED, March 2020 (v0.1)"))
        self.githubButton.setText(_translate("MainWindow", "Visit GitHub"))
        self.actionVisit_GitHub_page.setText(_translate("MainWindow", "Visit GitHub page"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
