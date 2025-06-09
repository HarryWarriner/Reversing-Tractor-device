import RPi.GPIO as GPIO
import time
LED_PIN_Left = 18
LED_PIN_Right = 23
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(LED_PIN_Left,GPIO.OUT)
GPIO.setup(LED_PIN_Right,GPIO.OUT)

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
            if value > 300:
                print("Right")
                GPIO.output(LED_PIN_Right, GPIO.HIGH)
                time.sleep(2)
                GPIO.output(LED_PIN_Right, GPIO.LOW)

            if value < 200:
                print("Left")
                GPIO.output(LED_PIN_Left, GPIO.HIGH)
                time.sleep(2)
                GPIO.output(LED_PIN_Left, GPIO.LOW)
except KeyboardInterrupt:
    GPIO.cleanup()
except FileNotFoundError:
    print("Bluetooth device not connected.")
