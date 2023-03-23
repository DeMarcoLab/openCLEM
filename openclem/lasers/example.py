from openclem.lasers.ldi import LdiLaserController
from openclem.structures import SerialSettings

serial_settings = SerialSettings(serial_port='COM8', 
                                 baudrate=9600, 
                                 timeout=1)


laser_controller = LdiLaserController()
laser_controller.connect(serial_settings=serial_settings)
lasers = laser_controller.lasers
