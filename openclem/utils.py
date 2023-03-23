import serial
import serial.tools.list_ports

def write_serial_command(serial_port, command):
    serial_port.close()
    serial_port.open()
    bytelength = serial_port.write(bytes(command, 'utf-8'))
    serial_port.close()
    return bytelength

def get_available_ports():
    ports = serial.tools.list_ports.comports()
    return ports

def get_port_names(ports):
    port_names = [port.device for port in ports]
    return port_names

def connect_to_serial_port(port_name, baudrate=9600, timeout=0.1):
    serial_port = serial.Serial(port=port_name, baudrate=baudrate, timeout=timeout)
    return serial_port