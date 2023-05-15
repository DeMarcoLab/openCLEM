# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'OpenLMPositionWidget.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(427, 300)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.label_coordinate_list = QtWidgets.QLabel(Form)
        self.label_coordinate_list.setObjectName("label_coordinate_list")
        self.gridLayout.addWidget(self.label_coordinate_list, 11, 0, 1, 3)
        self.doubleSpinBox_translation_z = QtWidgets.QDoubleSpinBox(Form)
        self.doubleSpinBox_translation_z.setMinimum(-10000000000.0)
        self.doubleSpinBox_translation_z.setMaximum(10000000000.0)
        self.doubleSpinBox_translation_z.setObjectName("doubleSpinBox_translation_z")
        self.gridLayout.addWidget(self.doubleSpinBox_translation_z, 3, 2, 1, 1)
        self.doubleSpinBox_translation_x = QtWidgets.QDoubleSpinBox(Form)
        self.doubleSpinBox_translation_x.setMinimum(-100000000000.0)
        self.doubleSpinBox_translation_x.setMaximum(1000000000000.0)
        self.doubleSpinBox_translation_x.setObjectName("doubleSpinBox_translation_x")
        self.gridLayout.addWidget(self.doubleSpinBox_translation_x, 3, 0, 1, 1)
        self.pushButton_save_coordinate = QtWidgets.QPushButton(Form)
        self.pushButton_save_coordinate.setObjectName("pushButton_save_coordinate")
        self.gridLayout.addWidget(self.pushButton_save_coordinate, 10, 2, 1, 1)
        self.pushButton_remove_coordinate = QtWidgets.QPushButton(Form)
        self.pushButton_remove_coordinate.setObjectName("pushButton_remove_coordinate")
        self.gridLayout.addWidget(self.pushButton_remove_coordinate, 10, 1, 1, 1)
        self.pushButton_move_to_microscope = QtWidgets.QPushButton(Form)
        self.pushButton_move_to_microscope.setObjectName("pushButton_move_to_microscope")
        self.gridLayout.addWidget(self.pushButton_move_to_microscope, 5, 0, 1, 3)
        self.label_position_list = QtWidgets.QLabel(Form)
        self.label_position_list.setObjectName("label_position_list")
        self.gridLayout.addWidget(self.label_position_list, 14, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 6, 0, 1, 3)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 17, 0, 1, 3)
        self.doubleSpinBox_translation_y = QtWidgets.QDoubleSpinBox(Form)
        self.doubleSpinBox_translation_y.setMinimum(-10000000.0)
        self.doubleSpinBox_translation_y.setMaximum(100000000.0)
        self.doubleSpinBox_translation_y.setObjectName("doubleSpinBox_translation_y")
        self.gridLayout.addWidget(self.doubleSpinBox_translation_y, 3, 1, 1, 1)
        self.label_title = QtWidgets.QLabel(Form)
        self.label_title.setObjectName("label_title")
        self.gridLayout.addWidget(self.label_title, 8, 0, 1, 1)
        self.pushButton_move_to_position = QtWidgets.QPushButton(Form)
        self.pushButton_move_to_position.setObjectName("pushButton_move_to_position")
        self.gridLayout.addWidget(self.pushButton_move_to_position, 15, 0, 1, 3)
        self.comboBox_move_to_system = QtWidgets.QComboBox(Form)
        self.comboBox_move_to_system.setObjectName("comboBox_move_to_system")
        self.gridLayout.addWidget(self.comboBox_move_to_system, 14, 1, 1, 1)
        self.comboBox_positions = QtWidgets.QComboBox(Form)
        self.comboBox_positions.setObjectName("comboBox_positions")
        self.gridLayout.addWidget(self.comboBox_positions, 14, 2, 1, 1)
        self.pushButton_add_coordinate = QtWidgets.QPushButton(Form)
        self.pushButton_add_coordinate.setObjectName("pushButton_add_coordinate")
        self.gridLayout.addWidget(self.pushButton_add_coordinate, 10, 0, 1, 1)
        self.label_microscope_translation = QtWidgets.QLabel(Form)
        self.label_microscope_translation.setObjectName("label_microscope_translation")
        self.gridLayout.addWidget(self.label_microscope_translation, 2, 0, 1, 3)
        self.label_title_2 = QtWidgets.QLabel(Form)
        self.label_title_2.setObjectName("label_title_2")
        self.gridLayout.addWidget(self.label_title_2, 1, 0, 1, 3)
        self.label_microscope_position = QtWidgets.QLabel(Form)
        self.label_microscope_position.setObjectName("label_microscope_position")
        self.gridLayout.addWidget(self.label_microscope_position, 4, 0, 1, 3)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label_coordinate_list.setText(_translate("Form", "TextLabel"))
        self.pushButton_save_coordinate.setText(_translate("Form", "Save Positions"))
        self.pushButton_remove_coordinate.setText(_translate("Form", "Remove Position"))
        self.pushButton_move_to_microscope.setText(_translate("Form", "Move to Microscope"))
        self.label_position_list.setText(_translate("Form", "Selected Position"))
        self.label_title.setText(_translate("Form", "Experiment Positions"))
        self.pushButton_move_to_position.setText(_translate("Form", "Move To Position"))
        self.pushButton_add_coordinate.setText(_translate("Form", "Add Position"))
        self.label_microscope_translation.setText(_translate("Form", "Microscope Coordinate Translation (x, y, z) (mm)"))
        self.label_title_2.setText(_translate("Form", "Microscope Positions"))
        self.label_microscope_position.setText(_translate("Form", "Current Position"))
