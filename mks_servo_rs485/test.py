import time
import serial
import minimalmodbus
from scan import list_serial_ports
from servo import Servo, MotorType

def connect_motor(port, address):
    """Connexion au moteur."""
    instrument = minimalmodbus.Instrument(port, address)
    instrument.serial.baudrate = 38400
    instrument.serial.timeout = 1
    instrument.serial.parity = serial.PARITY_NONE
    instrument.serial.stopbits = serial.STOPBITS_ONE
    instrument.mode = minimalmodbus.MODE_RTU
    return Servo(
        mb=instrument,
        motor_type=MotorType.SERVO_57_D,
        address=address,
        max_current=5200,
        hold_current_percent=50,
        full_steps=200,
        micro_steps=16
    )

def main():
    ports = list_serial_ports()
    if not ports:
        print("Aucun port série disponible.")
        return

    print("Ports disponibles :")
    for idx, p in enumerate(ports):
        print(f"{idx}: {p}")

    port_idx = int(input("Choisis le numéro du port COM : "))
    if port_idx < 0 or port_idx >= len(ports):
        print("Numéro de port invalide.")
        return
    port = ports[port_idx]

    # Connexion moteurs
    pan = connect_motor(port, 1)
    tilt = connect_motor(port, 2)

    print("\nHoming des deux axes...")
    pan.go_home()
    tilt.go_home()
    time.sleep(2)  # attendre un peu que le home se termine
    print("Homing terminé.")

    # Phase d'enseignement Position A
    print("\nDéplacer manuellement le robot pour définir Position A.")
    pan.disable()
    tilt.disable()
    input("Place le robot à Position A, puis appuie sur Entrée...")

    pan.enable()
    tilt.enable()
    time.sleep(0.2)  # petit délai pour permettre l'activation

    pan_A = pan.read_angle_carry()
    tilt_A = tilt.read_angle_carry()
    print(f"Position A enregistrée : PAN={pan_A:.2f}°, TILT={tilt_A:.2f}°")

    # Phase d'enseignement Position B
    print("\nDéplacer manuellement le robot pour définir Position B.")
    pan.disable()
    tilt.disable()
    input("Place le robot à Position B, puis appuie sur Entrée...")

    pan.enable()
    tilt.enable()
    time.sleep(0.2)

    pan_B = pan.read_angle_carry()
    tilt_B = tilt.read_angle_carry()
    print(f"Position B enregistrée : PAN={pan_B:.2f}°, TILT={tilt_B:.2f}°")

    input("\nAppuie sur Entrée pour commencer le déplacement de A vers B...")

    # Paramètres de mouvement
    acc = 100    # Accélération (pulses/sec²)
    speed = 1000  # Vitesse max (pulses/sec)

    # Déplacement vers A
    print("\nDéplacement vers Position A...")
    pan.move_to_absolute_angle(acc=acc, speed=speed, angle=pan_A)
    tilt.move_to_absolute_angle(acc=acc, speed=speed, angle=tilt_A)
    time.sleep(5)

    # Déplacement vers B
    print("\nDéplacement vers Position B...")
    pan.move_to_absolute_angle(acc=acc, speed=speed, angle=pan_B)
    tilt.move_to_absolute_angle(acc=acc, speed=speed, angle=tilt_B)
    time.sleep(5)

    print("\nDéplacements terminés.")

if __name__ == "__main__":
    main()