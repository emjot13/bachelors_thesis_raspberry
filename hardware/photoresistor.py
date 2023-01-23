
import RPi.GPIO as GPIO
import time



def photoresitor():
    PHOTORESISTOR_PIN = 6
    RED_LED_PIN = 16

    GPIO.setmode(GPIO.BCM)  
    GPIO.setup(PHOTORESISTOR_PIN, GPIO.OUT)
    GPIO.setup(RED_LED_PIN, GPIO.OUT)
    GPIO.output(PHOTORESISTOR_PIN, GPIO.LOW)

    time.sleep(0.1)
    GPIO.setup(PHOTORESISTOR_PIN, GPIO.IN)
  
    count = 0
    while (GPIO.input(PHOTORESISTOR_PIN) == GPIO.LOW):
        count += 1

    if not 400 <= count <= 11000:
        GPIO.output(RED_LED_PIN, GPIO.HIGH)
    else:
        GPIO.output(RED_LED_PIN, GPIO.LOW)


def check_room_light():
    try:
        while True:
            photoresitor()
    except KeyboardInterrupt:
        GPIO.cleanup()

