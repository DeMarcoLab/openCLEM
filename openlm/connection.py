# connections

# serial (usb)
import serial

def write_serial_command(port: serial.Serial, command):
    port.close()
    port.open()
    port.write(bytes(command, "utf-8"))
    response = port.read_until(expected=b"\r")
    port.close()
    return response


def get_available_ports():
    ports = serial.tools.list_ports.comports()
    return ports


def get_port_names(ports):
    port_names = [port.device for port in ports]
    return port_names


def connect_to_serial_port(port, baudrate=9600, timeout=1):

    serial_connection = serial.Serial(
        port=port, baudrate=baudrate, timeout=timeout
    )
    return serial_connection

# socket (tcp/ip)
