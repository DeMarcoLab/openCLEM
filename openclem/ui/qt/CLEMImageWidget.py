# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'CLEMImageWidget.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(308, 281)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.lineEdit_save_label = QtWidgets.QLineEdit(Form)
        self.lineEdit_save_label.setObjectName("lineEdit_save_label")
        self.gridLayout.addWidget(self.lineEdit_save_label, 5, 0, 1, 2)
        self.comboBox_imaging_mode = QtWidgets.QComboBox(Form)
        self.comboBox_imaging_mode.setObjectName("comboBox_imaging_mode")
        self.gridLayout.addWidget(self.comboBox_imaging_mode, 1, 1, 1, 2)
        self.pushButton_save_image = QtWidgets.QPushButton(Form)
        self.pushButton_save_image.setObjectName("pushButton_save_image")
        self.gridLayout.addWidget(self.pushButton_save_image, 5, 2, 1, 1)
        self.label_imaging_mode = QtWidgets.QLabel(Form)
        self.label_imaging_mode.setObjectName("label_imaging_mode")
        self.gridLayout.addWidget(self.label_imaging_mode, 1, 0, 1, 1)
        self.line = QtWidgets.QFrame(Form)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 3, 0, 1, 2)
        self.pushButton_acquire_image = QtWidgets.QPushButton(Form)
        self.pushButton_acquire_image.setObjectName("pushButton_acquire_image")
        self.gridLayout.addWidget(self.pushButton_acquire_image, 4, 0, 1, 3)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 7, 0, 1, 3)
        self.label_title = QtWidgets.QLabel(Form)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_title.setFont(font)
        self.label_title.setObjectName("label_title")
        self.gridLayout.addWidget(self.label_title, 0, 0, 1, 2)
        self.pushButton_move_microscope = QtWidgets.QPushButton(Form)
        self.pushButton_move_microscope.setObjectName("pushButton_move_microscope")
        self.gridLayout.addWidget(self.pushButton_move_microscope, 8, 0, 1, 3)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.lineEdit_save_label.setText(_translate("Form", "image"))
        self.pushButton_save_image.setText(_translate("Form", "Save Image"))
        self.label_imaging_mode.setText(_translate("Form", "Mode"))
        self.pushButton_acquire_image.setText(_translate("Form", "Acquire Image"))
        self.label_title.setText(_translate("Form", "Imaging"))
        self.pushButton_move_microscope.setText(_translate("Form", "Move to Microscope"))
