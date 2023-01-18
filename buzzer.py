import RPi.GPIO as GPIO
import time



GPIO.setmode(GPIO.BOARD)
GPIO.setup(16, GPIO.OUT)

for x in range(5):
    GPIO.output(16, True)
    print("on")
    time.sleep(1)
    GPIO.output(16, False)
    time.sleep(1)

GPIO.cleanup()