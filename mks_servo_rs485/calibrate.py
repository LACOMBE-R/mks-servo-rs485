import time
import serial
import minimalmodbus
import keyboard
from scan import list_serial_ports
from servo import Servo, MotorType

# Configuration
BAUDRATE = 38400
GEAR_RATIO = 4.0  # rapport de réduction
ACC_STEP = 50     # incrément de vitesse en °/s²
DEC_STEP = 80     # décrément de vitesse en °/s²
SPEED_MAX = 500   # vitesse max en °/s
TICK = 0.05       # durée d'un cycle en seconde (50ms)

def connect_motor(port, address):
    """Connexion au moteur."""
    instrument = minimalmodbus.Instrument(port, address)
    instrument.serial.baudrate = BAUDRATE
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

def move_motor(motor, delta_angle, speed=1000, acc=50):
    """Déplacer de delta_angle degrés."""
    motor.move_to_relative_angle(acc=acc, speed=speed, angle=delta_angle)

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
    print("Homing terminé.")

    # Vitesse actuelle
    pan_speed = 0.0
    tilt_speed = 0.0

    print("\nCommandes clavier actives :")
    print("← → pour PAN (gauche/droite)")
    print("↑ ↓ pour TILT (haut/bas)")
    print("ESC pour quitter")

    try:
        while True:
            # Gestion PAN
            if keyboard.is_pressed('left'):
                pan_speed = max(pan_speed - ACC_STEP * TICK, -SPEED_MAX)
            elif keyboard.is_pressed('right'):
                pan_speed = min(pan_speed + ACC_STEP * TICK, SPEED_MAX)
            else:
                # Décélération naturelle PAN
                if pan_speed > 0:
                    pan_speed = max(pan_speed - DEC_STEP * TICK, 0)
                elif pan_speed < 0:
                    pan_speed = min(pan_speed + DEC_STEP * TICK, 0)

            # Gestion TILT
            if keyboard.is_pressed('up'):
                tilt_speed = min(tilt_speed + ACC_STEP * TICK, SPEED_MAX)
            elif keyboard.is_pressed('down'):
                tilt_speed = max(tilt_speed - ACC_STEP * TICK, -SPEED_MAX)
            else:
                # Décélération naturelle TILT
                if tilt_speed > 0:
                    tilt_speed = max(tilt_speed - DEC_STEP * TICK, 0)
                elif tilt_speed < 0:
                    tilt_speed = min(tilt_speed + DEC_STEP * TICK, 0)

            # Application mouvement en fonction de vitesse actuelle
            if abs(pan_speed) > 1:
                move_motor(pan, delta_angle=pan_speed * TICK, speed=abs(int(pan_speed)), acc=50)

            if abs(tilt_speed) > 1:
                move_motor(tilt, delta_angle=tilt_speed * TICK, speed=abs(int(tilt_speed)), acc=50)

            if keyboard.is_pressed('esc'):
                print("Arrêt demandé.")
                break

            time.sleep(TICK)

    except KeyboardInterrupt:
        print("\nArrêt manuel demandé.")

if __name__ == "__main__":
    main()
