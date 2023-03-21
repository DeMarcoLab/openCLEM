def _write_serial_command(SERIAL_PORT, command):
    SERIAL_PORT.close()
    SERIAL_PORT.open()
    bytelength = SERIAL_PORT.write(bytes(command, 'utf-8'))
    SERIAL_PORT.close()
    return bytelength
