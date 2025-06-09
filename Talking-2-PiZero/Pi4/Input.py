import time
import os
import RPi.GPIO as GPIO 
GPIO.setwarnings(False) 
GPIO.setmode(GPIO.BOARD) 
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 10 to be an input pin and set initial value to be pulled low (off)
RFCOMM_DEVICE = "/dev/rfcomm0"

def send_signal():
    os.system(f'echo "ON" | sudo tee {RFCOMM_DEVICE}')

try:
    while True: 
        if GPIO.input(10) == GPIO.HIGH:
            print("Button was pushed!")
            send_signal()
            time.sleep(0.5)
except KeyboardInterrupt:
    GPIO.cleanup()
        