import RPi.GPIO as GPIO
import time


def led(color, interval = 1, times = 10):

    GPIO.setmode(GPIO.BCM)
    LED_PIN = 17 if color == "red" else 18
    GPIO.setup(LED_PIN, GPIO.OUT)
    for _ in range(times):
        GPIO.output(LED_PIN, GPIO.HIGH)
        time.sleep(interval)
        GPIO.output(LED_PIN, GPIO.LOW)
        time.sleep(interval)
    GPIO.cleanup()


led("red")