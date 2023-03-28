# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'CLEMLaserWidget.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(394, 432)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.label_laser_exposure = QtWidgets.QLabel(Form)
        self.label_laser_exposure.setObjectName("label_laser_exposure")
        self.gridLayout.addWidget(self.label_laser_exposure, 10, 0, 1, 1)
        self.label_lc_type = QtWidgets.QLabel(Form)
        self.label_lc_type.setObjectName("label_lc_type")
        self.gridLayout.addWidget(self.label_lc_type, 2, 0, 1, 1)
        self.label_laser_id = QtWidgets.QLabel(Form)
        self.label_laser_id.setObjectName("label_laser_id")
        self.gridLayout.addWidget(self.label_laser_id, 7, 0, 1, 1)
        self.label_laser_wavelength = QtWidgets.QLabel(Form)
        self.label_laser_wavelength.setObjectName("label_laser_wavelength")
        self.gridLayout.addWidget(self.label_laser_wavelength, 8, 0, 1, 1)
        self.label_laser_color = QtWidgets.QLabel(Form)
        self.label_laser_color.setObjectName("label_laser_color")
        self.gridLayout.addWidget(self.label_laser_color, 12, 0, 1, 1)
        self.label_title = QtWidgets.QLabel(Form)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_title.setFont(font)
        self.label_title.setObjectName("label_title")
        self.gridLayout.addWidget(self.label_title, 0, 0, 1, 1)
        self.lineEdit_lc_type = QtWidgets.QLineEdit(Form)
        self.lineEdit_lc_type.setObjectName("lineEdit_lc_type")
        self.gridLayout.addWidget(self.lineEdit_lc_type, 2, 1, 1, 1)
        self.checkBox_laser_enabled = QtWidgets.QCheckBox(Form)
        self.checkBox_laser_enabled.setObjectName("checkBox_laser_enabled")
        self.gridLayout.addWidget(self.checkBox_laser_enabled, 12, 1, 1, 1)
        self.lineEdit_lc_name = QtWidgets.QLineEdit(Form)
        self.lineEdit_lc_name.setObjectName("lineEdit_lc_name")
        self.gridLayout.addWidget(self.lineEdit_lc_name, 1, 1, 1, 1)
        self.pushButton_apply_laser_settings = QtWidgets.QPushButton(Form)
        self.pushButton_apply_laser_settings.setObjectName("pushButton_apply_laser_settings")
        self.gridLayout.addWidget(self.pushButton_apply_laser_settings, 13, 0, 1, 2)
        self.label_selected_laser = QtWidgets.QLabel(Form)
        self.label_selected_laser.setObjectName("label_selected_laser")
        self.gridLayout.addWidget(self.label_selected_laser, 5, 0, 1, 1)
        self.label_laser_power = QtWidgets.QLabel(Form)
        self.label_laser_power.setObjectName("label_laser_power")
        self.gridLayout.addWidget(self.label_laser_power, 9, 0, 1, 1)
        self.line = QtWidgets.QFrame(Form)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 4, 0, 1, 2)
        self.label_laser_name = QtWidgets.QLabel(Form)
        self.label_laser_name.setObjectName("label_laser_name")
        self.gridLayout.addWidget(self.label_laser_name, 6, 0, 1, 1)
        self.label_lc_name = QtWidgets.QLabel(Form)
        self.label_lc_name.setObjectName("label_lc_name")
        self.gridLayout.addWidget(self.label_lc_name, 1, 0, 1, 1)
        self.comboBox_selected_laser = QtWidgets.QComboBox(Form)
        self.comboBox_selected_laser.setObjectName("comboBox_selected_laser")
        self.gridLayout.addWidget(self.comboBox_selected_laser, 5, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 14, 0, 1, 2)
        self.lineEdit_laser_name = QtWidgets.QLineEdit(Form)
        self.lineEdit_laser_name.setObjectName("lineEdit_laser_name")
        self.gridLayout.addWidget(self.lineEdit_laser_name, 6, 1, 1, 1)
        self.lineEdit_laser_id = QtWidgets.QLineEdit(Form)
        self.lineEdit_laser_id.setObjectName("lineEdit_laser_id")
        self.gridLayout.addWidget(self.lineEdit_laser_id, 7, 1, 1, 1)
        self.spinBox_laser_wavelength = QtWidgets.QSpinBox(Form)
        self.spinBox_laser_wavelength.setMaximum(10000000)
        self.spinBox_laser_wavelength.setObjectName("spinBox_laser_wavelength")
        self.gridLayout.addWidget(self.spinBox_laser_wavelength, 8, 1, 1, 1)
        self.doubleSpinBox_laser_power = QtWidgets.QDoubleSpinBox(Form)
        self.doubleSpinBox_laser_power.setDecimals(2)
        self.doubleSpinBox_laser_power.setMaximum(1.0)
        self.doubleSpinBox_laser_power.setSingleStep(0.01)
        self.doubleSpinBox_laser_power.setObjectName("doubleSpinBox_laser_power")
        self.gridLayout.addWidget(self.doubleSpinBox_laser_power, 9, 1, 1, 1)
        self.doubleSpinBox_laser_exposure = QtWidgets.QDoubleSpinBox(Form)
        self.doubleSpinBox_laser_exposure.setDecimals(2)
        self.doubleSpinBox_laser_exposure.setMaximum(10000000.0)
        self.doubleSpinBox_laser_exposure.setProperty("value", 1.0)
        self.doubleSpinBox_laser_exposure.setObjectName("doubleSpinBox_laser_exposure")
        self.gridLayout.addWidget(self.doubleSpinBox_laser_exposure, 10, 1, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label_laser_exposure.setText(_translate("Form", "Exposure (ms)"))
        self.label_lc_type.setText(_translate("Form", "Type"))
        self.label_laser_id.setText(_translate("Form", "ID"))
        self.label_laser_wavelength.setText(_translate("Form", "Wavelength (nm)"))
        self.label_laser_color.setText(_translate("Form", "Colour"))
        self.label_title.setText(_translate("Form", "Laser Controller"))
        self.checkBox_laser_enabled.setText(_translate("Form", "Enabled"))
        self.pushButton_apply_laser_settings.setText(_translate("Form", "Apply Laser Settings"))
        self.label_selected_laser.setText(_translate("Form", "Laser"))
        self.label_laser_power.setText(_translate("Form", "Power"))
        self.label_laser_name.setText(_translate("Form", "Name"))
        self.label_lc_name.setText(_translate("Form", "Name"))
