import serial

def build_mks_command(address, function, value):
    """Construit une trame MKS avec checksum 8 bits"""
    crc = (0xFA + address + function + value) & 0xFF
    return bytes([0xFA, address, function, value, crc])

def send_activate_modbus(port_name, motor_address):
    command = build_mks_command(motor_address, function=0x8E, value=0x01)

    with serial.Serial(
        port=port_name,
        baudrate=38400,      # adapte si ton moteur est à 115200
        bytesize=8,
        parity=serial.PARITY_NONE,
        stopbits=1,
        timeout=1
    ) as ser:
        print(f"Envoi de {command.hex(' ').upper()} sur {port_name} pour moteur adresse {motor_address}")
        ser.write(command)
        ser.flush()
        print("Commande envoyée.")

if __name__ == "__main__":
    port = input("Port COM (ex: COM3, /dev/ttyUSB0) : ")
    motor_address = int(input("Adresse du moteur (ex: 1 ou 2) : "))
    send_activate_modbus(port, motor_address)
