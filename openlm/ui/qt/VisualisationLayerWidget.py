# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'VisualisationLayerWidget.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(312, 825)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.BaseFrame = QtWidgets.QFrame(Form)
        self.BaseFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.BaseFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.BaseFrame.setObjectName("BaseFrame")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.BaseFrame)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.pushButton_VIEW_EM = QtWidgets.QPushButton(self.BaseFrame)
        self.pushButton_VIEW_EM.setObjectName("pushButton_VIEW_EM")
        self.gridLayout_2.addWidget(self.pushButton_VIEW_EM, 0, 0, 1, 1)
        self.pushButton_VIEW_FIB = QtWidgets.QPushButton(self.BaseFrame)
        self.pushButton_VIEW_FIB.setObjectName("pushButton_VIEW_FIB")
        self.gridLayout_2.addWidget(self.pushButton_VIEW_FIB, 0, 1, 1, 1)
        self.tabWidget_Layers = QtWidgets.QTabWidget(self.BaseFrame)
        self.tabWidget_Layers.setObjectName("tabWidget_Layers")
        self.gridLayout_2.addWidget(self.tabWidget_Layers, 1, 0, 1, 2)
        self.gridLayout.addWidget(self.BaseFrame, 0, 0, 1, 1)

        self.retranslateUi(Form)
        self.tabWidget_Layers.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.pushButton_VIEW_EM.setText(_translate("Form", "EM Detector View"))
        self.pushButton_VIEW_FIB.setText(_translate("Form", "FIB Detector View"))
