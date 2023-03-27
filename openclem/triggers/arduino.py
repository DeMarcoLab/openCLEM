import time
import serial
import serial.tools.list_ports

DEFAULT_SERIAL_PORT = 'COM7'  # default laser serial communication port

class Arduino:
    """Arduino Class"""
    def __init__(self, port=DEFAULT_SERIAL_PORT):
        self.SERIAL_PORT = port
        self.connection = connect_serial_port(self.SERIAL_PORT)

    def _write_serial_command(self, command):
        self.connection.close()
        self.connection.open()
        time.sleep(1)  # required, not sure why
        self.connection.write(bytes(command, 'utf-8'))
        self.connection.close()


def connect_serial_port(port=DEFAULT_SERIAL_PORT, baudrate=115200, timeout=3):
    """Serial port for communication with the lasers.

    Parameters
    ----------
    port : str, optional
        Serial port device name, by default 'COM6'.
    baudrate : int, optional
        Rate of communication, by default 115200 bits per second.
    timeout : int, optional
        Timeout period, by default 1 second.

    Returns
    -------
    pyserial Serial() object
        Serial port for communication with the lasers.
    """
    return serial.Serial(port, baudrate=baudrate, timeout=timeout)
