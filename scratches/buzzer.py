import RPi.GPIO as GPIO
import time

class Buzzer:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(self.pin, GPIO.OUT)
        
    def beep(self, duration=0.1):
        GPIO.output(self.pin, True)
        time.sleep(duration)
        GPIO.output(self.pin, False)
