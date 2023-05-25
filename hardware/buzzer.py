import RPi.GPIO as GPIO
from time import sleep



def beep(interval_sec = 0.5, times = 2):
    GPIO.setmode(GPIO.BCM)
    buzzer = 23
    GPIO.setup(buzzer, GPIO.OUT)

    for _ in range(times):
        GPIO.output(buzzer, GPIO.HIGH)
        sleep(interval_sec) 
        GPIO.output(buzzer, GPIO.LOW)
        sleep(interval_sec)
    GPIO.cleanup()



# beep()