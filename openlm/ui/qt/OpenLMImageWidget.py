# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'OpenLMImageWidget.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(401, 339)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.label_title = QtWidgets.QLabel(Form)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_title.setFont(font)
        self.label_title.setObjectName("label_title")
        self.gridLayout.addWidget(self.label_title, 0, 0, 1, 2)
        self.tabWidget = QtWidgets.QTabWidget(Form)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.tab)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.comboBox_imaging_mode = QtWidgets.QComboBox(self.tab)
        self.comboBox_imaging_mode.setObjectName("comboBox_imaging_mode")
        self.gridLayout_2.addWidget(self.comboBox_imaging_mode, 0, 2, 1, 1)
        self.pushButton_acquire_image = QtWidgets.QPushButton(self.tab)
        self.pushButton_acquire_image.setObjectName("pushButton_acquire_image")
        self.gridLayout_2.addWidget(self.pushButton_acquire_image, 1, 0, 1, 3)
        self.lineEdit_save_label = QtWidgets.QLineEdit(self.tab)
        self.lineEdit_save_label.setObjectName("lineEdit_save_label")
        self.gridLayout_2.addWidget(self.lineEdit_save_label, 2, 0, 1, 1)
        self.pushButton_save_image = QtWidgets.QPushButton(self.tab)
        self.pushButton_save_image.setObjectName("pushButton_save_image")
        self.gridLayout_2.addWidget(self.pushButton_save_image, 2, 2, 1, 1)
        self.label_imaging_mode = QtWidgets.QLabel(self.tab)
        self.label_imaging_mode.setObjectName("label_imaging_mode")
        self.gridLayout_2.addWidget(self.label_imaging_mode, 0, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem, 3, 0, 1, 3)
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.tab_2)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.spinBox_tile_n_rows = QtWidgets.QSpinBox(self.tab_2)
        self.spinBox_tile_n_rows.setMinimum(1)
        self.spinBox_tile_n_rows.setProperty("value", 1)
        self.spinBox_tile_n_rows.setObjectName("spinBox_tile_n_rows")
        self.gridLayout_3.addWidget(self.spinBox_tile_n_rows, 1, 1, 1, 1)
        self.label_header_volume = QtWidgets.QLabel(self.tab_2)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_header_volume.setFont(font)
        self.label_header_volume.setObjectName("label_header_volume")
        self.gridLayout_3.addWidget(self.label_header_volume, 4, 0, 1, 2)
        self.label_header_tile = QtWidgets.QLabel(self.tab_2)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_header_tile.setFont(font)
        self.label_header_tile.setObjectName("label_header_tile")
        self.gridLayout_3.addWidget(self.label_header_tile, 0, 0, 1, 2)
        self.label_tile_rows = QtWidgets.QLabel(self.tab_2)
        self.label_tile_rows.setObjectName("label_tile_rows")
        self.gridLayout_3.addWidget(self.label_tile_rows, 1, 0, 1, 1)
        self.checkBox_workflow_return_to_origin = QtWidgets.QCheckBox(self.tab_2)
        self.checkBox_workflow_return_to_origin.setObjectName("checkBox_workflow_return_to_origin")
        self.gridLayout_3.addWidget(self.checkBox_workflow_return_to_origin, 6, 0, 1, 1)
        self.label_workflow_run_info = QtWidgets.QLabel(self.tab_2)
        self.label_workflow_run_info.setText("")
        self.label_workflow_run_info.setObjectName("label_workflow_run_info")
        self.gridLayout_3.addWidget(self.label_workflow_run_info, 8, 0, 1, 3)
        self.doubleSpinBox_tile_dx = QtWidgets.QDoubleSpinBox(self.tab_2)
        self.doubleSpinBox_tile_dx.setMaximum(100000000.0)
        self.doubleSpinBox_tile_dx.setObjectName("doubleSpinBox_tile_dx")
        self.gridLayout_3.addWidget(self.doubleSpinBox_tile_dx, 3, 1, 1, 1)
        self.label_workflow_info = QtWidgets.QLabel(self.tab_2)
        self.label_workflow_info.setText("")
        self.label_workflow_info.setObjectName("label_workflow_info")
        self.gridLayout_3.addWidget(self.label_workflow_info, 7, 0, 1, 3)
        self.doubleSpinBox_vol_dz = QtWidgets.QDoubleSpinBox(self.tab_2)
        self.doubleSpinBox_vol_dz.setMaximum(1000000.0)
        self.doubleSpinBox_vol_dz.setObjectName("doubleSpinBox_vol_dz")
        self.gridLayout_3.addWidget(self.doubleSpinBox_vol_dz, 5, 2, 1, 1)
        self.spinBox_vol_n_slices = QtWidgets.QSpinBox(self.tab_2)
        self.spinBox_vol_n_slices.setMinimum(1)
        self.spinBox_vol_n_slices.setObjectName("spinBox_vol_n_slices")
        self.gridLayout_3.addWidget(self.spinBox_vol_n_slices, 5, 1, 1, 1)
        self.doubleSpinBox_tile_dy = QtWidgets.QDoubleSpinBox(self.tab_2)
        self.doubleSpinBox_tile_dy.setMaximum(10000000.0)
        self.doubleSpinBox_tile_dy.setObjectName("doubleSpinBox_tile_dy")
        self.gridLayout_3.addWidget(self.doubleSpinBox_tile_dy, 3, 2, 1, 1)
        self.spinBox_tile_n_cols = QtWidgets.QSpinBox(self.tab_2)
        self.spinBox_tile_n_cols.setMinimum(1)
        self.spinBox_tile_n_cols.setProperty("value", 1)
        self.spinBox_tile_n_cols.setObjectName("spinBox_tile_n_cols")
        self.gridLayout_3.addWidget(self.spinBox_tile_n_cols, 1, 2, 1, 1)
        self.label_volume = QtWidgets.QLabel(self.tab_2)
        self.label_volume.setObjectName("label_volume")
        self.gridLayout_3.addWidget(self.label_volume, 5, 0, 1, 1)
        self.pushButton_run_tiling = QtWidgets.QPushButton(self.tab_2)
        self.pushButton_run_tiling.setObjectName("pushButton_run_tiling")
        self.gridLayout_3.addWidget(self.pushButton_run_tiling, 9, 0, 1, 3)
        self.label_tile_movement = QtWidgets.QLabel(self.tab_2)
        self.label_tile_movement.setObjectName("label_tile_movement")
        self.gridLayout_3.addWidget(self.label_tile_movement, 3, 0, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_3.addItem(spacerItem1, 10, 0, 1, 3)
        self.tabWidget.addTab(self.tab_2, "")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.tab_3)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.pushButton_move_microscope = QtWidgets.QPushButton(self.tab_3)
        self.pushButton_move_microscope.setObjectName("pushButton_move_microscope")
        self.gridLayout_4.addWidget(self.pushButton_move_microscope, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab_3, "")
        self.gridLayout.addWidget(self.tabWidget, 8, 0, 1, 1)
        self.line = QtWidgets.QFrame(Form)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 4, 0, 1, 2)

        self.retranslateUi(Form)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label_title.setText(_translate("Form", "Imaging"))
        self.pushButton_acquire_image.setText(_translate("Form", "Acquire Image"))
        self.lineEdit_save_label.setText(_translate("Form", "image"))
        self.pushButton_save_image.setText(_translate("Form", "Save Image"))
        self.label_imaging_mode.setText(_translate("Form", "Mode"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("Form", "Image"))
        self.label_header_volume.setText(_translate("Form", "Volumes"))
        self.label_header_tile.setText(_translate("Form", "Tiles"))
        self.label_tile_rows.setText(_translate("Form", "n_rows, n_cols"))
        self.checkBox_workflow_return_to_origin.setText(_translate("Form", "Return to origin"))
        self.label_volume.setText(_translate("Form", "n_slices, dz (um)"))
        self.pushButton_run_tiling.setText(_translate("Form", "Run Workflow"))
        self.label_tile_movement.setText(_translate("Form", "dx, dy (um)"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("Form", "Workflow"))
        self.pushButton_move_microscope.setText(_translate("Form", "Move to Microscope"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("Form", "Movement"))
