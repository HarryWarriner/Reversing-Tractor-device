import RPi.GPIO as GPIO
import time
LED_PIN = 18
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(LED_PIN,GPIO.OUT)

DEVICE = "/dev/rfcomm0"

try:
    with open(DEVICE, "r") as serial:
        while True:
            line = serial.readline().strip()
            if line == "ON":
                print("Turning on LED")
                GPIO.output(LED_PIN, GPIO.HIGH)
                time.sleep(2)
                GPIO.output(LED_PIN, GPIO.LOW)
except KeyboardInterrupt:
    GPIO.cleanup()
except FileNotFoundError:
    print("Bluetooth device not connected.")
