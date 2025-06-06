import RPi.GPIO as GPIO
from time import sleep

print("Start")

GPIO.setmode(GPIO.BOARD)
pin = 12

GPIO.setup(pin, GPIO.OUT)
pwm = GPIO.PWM(pin, 50)
pwm.start(0)

print("Setup Complete")

def SetAngle(angle):
    print(angle)
    duty = angle / 18 + 2
    pwm.ChangeDutyCycle(duty)
    sleep(2)
    print("Here Now")

try:
    print("trying")
    SetAngle(90)
    sleep(2)

finally:
    pwm.stop()
    GPIO.cleanup()