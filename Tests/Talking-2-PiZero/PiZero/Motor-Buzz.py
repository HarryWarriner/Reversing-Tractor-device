import RPi.GPIO as GPIO
import time

MOTOR_PIN_LEFT = 18
MOTOR_PIN_RIGHT = 17
MOTOR_PIN_FAR_LEFT = 19
MOTOR_PIN_FAR_RIGHT = 20

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(MOTOR_PIN_LEFT,GPIO.OUT)
GPIO.setup(MOTOR_PIN_RIGHT,GPIO.OUT)
GPIO.setup(MOTOR_PIN_FAR_LEFT,GPIO.OUT)
GPIO.setup(MOTOR_PIN_FAR_RIGHT,GPIO.OUT)


def blink_motor(pin, blinks = 3, on_time = 0.5, off_time = 0.2):
    for i in range(blinks):
        GPIO.output(pin,GPIO.HIGH)
        time.sleep(on_time)
        GPIO.output(pin,GPIO.LOW)
        time.sleep(off_time)

DEVICE = "/dev/rfcomm0"

try:
    with open(DEVICE, "r") as serial:
        while True:
            line = serial.readline().strip()

            try:
                value = int(line)
            except ValueError:
                print(f"Ignoring non-integer line: {line}")
                continue
            if 375 < value <= 500:
                print("Right")
                blink_motor(MOTOR_PIN_FAR_RIGHT)

            if 125 < value <= 250:
                print("Right")
                blink_motor(MOTOR_PIN_LEFT)
                
            if 250 < value <= 375:
                print("Right")
                blink_motor(MOTOR_PIN_RIGHT)

            if value <= 125:
                print("Left")
                blink_motor(MOTOR_PIN_FAR_LEFT)
                
except KeyboardInterrupt:
    GPIO.cleanup()
except FileNotFoundError:
    print("Bluetooth device not connected.")
