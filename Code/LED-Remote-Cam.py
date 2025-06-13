import serial
import RPi.GPIO as GPIO
import time

LED_PIN_Left = 18
LED_PIN_Right = 23

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(LED_PIN_Left, GPIO.OUT)
GPIO.setup(LED_PIN_Right, GPIO.OUT)

DEVICE = "/dev/rfcomm0"

try:
    ser = serial.Serial(DEVICE, baudrate=9600, timeout=1)
    while True:
        line = ser.readline().decode('utf-8').strip()
        try:
            value = int(line)
            print(f"Received: {value}")
        except ValueError:
            print(f"Ignoring non-integer line: {line}")
            continue

        if value > 300:
            print("Right")
            GPIO.output(LED_PIN_Right, GPIO.HIGH)
            time.sleep(2)
            GPIO.output(LED_PIN_Right, GPIO.LOW)
        elif value < 200:
            print("Left")
            GPIO.output(LED_PIN_Left, GPIO.HIGH)
            time.sleep(2)
            GPIO.output(LED_PIN_Left, GPIO.LOW)

except serial.SerialException:
    print("Could not open serial device.")
except KeyboardInterrupt:
    GPIO.cleanup()
