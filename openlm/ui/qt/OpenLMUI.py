# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'OpenLMUI.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(361, 514)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 3, 0, 1, 2)
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.tab)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.pushButton_connect_hardware = QtWidgets.QPushButton(self.tab)
        self.pushButton_connect_hardware.setObjectName("pushButton_connect_hardware")
        self.gridLayout_2.addWidget(self.pushButton_connect_hardware, 1, 0, 1, 2)
        self.label_config_filename = QtWidgets.QLabel(self.tab)
        self.label_config_filename.setObjectName("label_config_filename")
        self.gridLayout_2.addWidget(self.label_config_filename, 0, 0, 1, 1)
        self.lineEdit_config_filename = QtWidgets.QLineEdit(self.tab)
        self.lineEdit_config_filename.setObjectName("lineEdit_config_filename")
        self.gridLayout_2.addWidget(self.lineEdit_config_filename, 0, 1, 1, 1)
        self.label_hardware_status = QtWidgets.QLabel(self.tab)
        self.label_hardware_status.setText("")
        self.label_hardware_status.setWordWrap(True)
        self.label_hardware_status.setObjectName("label_hardware_status")
        self.gridLayout_2.addWidget(self.label_hardware_status, 2, 0, 1, 1)
        self.tabWidget.addTab(self.tab, "")
        self.gridLayout.addWidget(self.tabWidget, 2, 0, 1, 2)
        self.label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 361, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionLoad_Config = QtWidgets.QAction(MainWindow)
        self.actionLoad_Config.setObjectName("actionLoad_Config")
        self.menuFile.addAction(self.actionLoad_Config)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton_connect_hardware.setText(_translate("MainWindow", "Connect to Hardware"))
        self.label_config_filename.setText(_translate("MainWindow", "Config"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "General"))
        self.label.setText(_translate("MainWindow", "openlm"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.actionLoad_Config.setText(_translate("MainWindow", "Load Config"))