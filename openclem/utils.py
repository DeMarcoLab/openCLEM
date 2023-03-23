import serial
import serial.tools.list_ports
from openclem.structures import SerialSettings

def write_serial_command(serial_port: serial.Serial, command):
    serial_port.close()
    serial_port.open()
    serial_port.write(bytes(command, 'utf-8'))
    response = serial_port.read_until(expected=b'\r')
    serial_port.close()
    return response

def get_available_ports():
    ports = serial.tools.list_ports.comports()
    return ports

def get_port_names(ports):
    port_names = [port.device for port in ports]
    return port_names

def connect_to_serial_port(serial_settings: SerialSettings):
    port_name = serial_settings.serial_port
    baudrate = serial_settings.baudrate
    timeout = serial_settings.timeout
    
    serial_connection = serial.Serial(port=port_name, baudrate=baudrate, timeout=timeout)
    return serial_connection