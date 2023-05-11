import logging

import napari
import napari.utils.notifications
import numpy as np
from PyQt5 import QtWidgets

from openlm.spinning_disk import demo_disk, xlightv2
from openlm.ui.qt import OpenLMSpinningDiskWidget

logging.basicConfig(level=logging.INFO)

__SUPPORTED_SPINNING_DISKS__ = [xlightv2.XLightV2, demo_disk.DemoDisk]
__SUPPORTED_SPINNING_DISK_MODES__ = ["WideField", "Confocal"]


class OpenLMSpinningDiskWidget(OpenLMSpinningDiskWidget.Ui_Form, QtWidgets.QWidget):
    def __init__(
        self,
        viewer: napari.Viewer = None,
        parent=None,
    ):
        super(OpenLMSpinningDiskWidget, self).__init__(parent=parent)
        self.setupUi(self)

        self.viewer = viewer
        self.spinning_disk = None

        self.setup_connections()

        self.update_ui()

    def setup_connections(self):
        logging.info("setup_connections")

        self.comboBox_disk_type.addItems(
            sd.__name__ for sd in __SUPPORTED_SPINNING_DISKS__
        )
        self.pushButton_disk_connect.clicked.connect(self.on_connect)

        # self.checkBox_disk_onoff.stateChanged.connect(self.update_ui)
        # self.spinBox_disk_emission_filter.valueChanged.connect(self.update_ui)
        self.spinBox_disk_emission_filter.setMinimum(1)
        self.spinBox_disk_emission_filter.setMaximum(9)
        # self.spinBox_disk_position.valueChanged.connect(self.update_ui)
        self.spinBox_disk_position.setMinimum(0)
        self.spinBox_disk_position.setMaximum(2)

        self.comboBox_disk_mode.addItems(__SUPPORTED_SPINNING_DISK_MODES__)
        self.comboBox_disk_mode.currentIndexChanged.connect(self.update_ui)
        self.pushButton_disk_apply.clicked.connect(self.update_disk)

    def on_connect(self):
        self.spinning_disk: xlightv2.XLightV2 = __SUPPORTED_SPINNING_DISKS__[
            self.comboBox_disk_type.currentIndex()
        ]()
        self.spinning_disk.connect()
        logging.info(f"Connecting to {self.spinning_disk}")
        self.update_ui()

    def on_disconnect(self):
        logging.info(f"Disconnecting from {self.spinning_disk}")
        self.spinning_disk.disconnect()
        self.spinning_disk = None
        self.update_ui()

    def update_ui(self):
        logging.info(f"update_ui")

        _disk_connected = self.spinning_disk is not None
        if _disk_connected:
            self.pushButton_disk_connect.setText("Connected")
            self.pushButton_disk_connect.setStyleSheet("background-color: green")
            self.pushButton_disk_connect.clicked.disconnect()
            self.pushButton_disk_connect.clicked.connect(self.on_disconnect)
            self.comboBox_disk_type.setEnabled(False)
        else:
            self.pushButton_disk_connect.setText("Connect")
            self.pushButton_disk_connect.setStyleSheet("background-color: gray")
            self.pushButton_disk_connect.clicked.disconnect()
            self.pushButton_disk_connect.clicked.connect(self.on_connect)
            self.comboBox_disk_type.setEnabled(True)

        # set settings invisible is disk is not connected
        self.label_disk_mode.setVisible(_disk_connected)
        self.comboBox_disk_mode.setVisible(_disk_connected)
        self.checkBox_disk_onoff.setVisible(_disk_connected)
        self.label_disk_position.setVisible(_disk_connected)
        self.spinBox_disk_position.setVisible(_disk_connected)
        
        self.label_disk_emission_filter.setVisible(_disk_connected)
        self.spinBox_disk_emission_filter.setVisible(_disk_connected)
        self.pushButton_disk_apply.setVisible(_disk_connected)
        self.label_disk_status.setVisible(_disk_connected)


        if _disk_connected:
            mode = self.comboBox_disk_mode.currentText()

            if mode == "WideField":
                self.checkBox_disk_onoff.setChecked(False)
                self.spinBox_disk_position.setValue(0)
                self.spinBox_disk_emission_filter.setValue(1)

                self.spinBox_disk_position.setEnabled(False)
                self.spinBox_disk_emission_filter.setEnabled(False)

            if mode == "Confocal":
                self.checkBox_disk_onoff.setChecked(True)
                self.spinBox_disk_position.setValue(1)
                self.spinBox_disk_emission_filter.setValue(1)
                self.spinBox_disk_position.setEnabled(True)
                self.spinBox_disk_emission_filter.setEnabled(True)

    def update_disk(self):
        # apply
        logging.info(f"update_disk")

        disk_on = int(self.checkBox_disk_onoff.isChecked())
        disk_position = int(self.spinBox_disk_position.value())
        disk_emission_filter = int(self.spinBox_disk_emission_filter.value())

        if self.spinning_disk is not None:
            logging.info(
                f"Disk On: {disk_on}, Position: {disk_position}, Emission Filter: {disk_emission_filter}"
            )
            self.spinning_disk.disk_position(position=disk_position)
            self.spinning_disk.disk_onoff(onoff=disk_on)
            self.spinning_disk.emission_filter(position=disk_emission_filter)

            status = self.spinning_disk.get_status()
            # status = "Dummy status"
            logging.info(f"status: {status}")
            napari.utils.notifications.show_info(f"status: {status}")
            self.label_disk_status.setText(f"status: {status}")


def main():
    # create the viewer and window
    viewer = napari.Viewer(ndisplay=2)

    openlm_spinning_disk = OpenLMSpinningDiskWidget(viewer=viewer)

    viewer.window.add_dock_widget(
        openlm_spinning_disk, area="right", add_vertical_stretch=False
    )
    napari.run()


if __name__ == "__main__":
    main()
