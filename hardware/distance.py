import RPi.GPIO as GPIO
import time

def check_distance():
    GPIO.setmode(GPIO.BCM)

    GPIO_TRIGGER = 25
    GPIO_ECHO = 24
    RED_LED_PIN = 17
    GREEN_LED_PIN = 18
    SONIC_SPEED = 34300 # cm/s


    GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
    GPIO.setup(RED_LED_PIN, GPIO.OUT)
    GPIO.setup(GREEN_LED_PIN, GPIO.OUT)
    GPIO.setup(GPIO_ECHO, GPIO.IN)

    GPIO.output(GPIO_TRIGGER, True)
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)

    while GPIO.input(GPIO_ECHO) == 0:
        start_time = time.time()

    while GPIO.input(GPIO_ECHO) == 1:
        stop_time = time.time()

    travel_time = stop_time - start_time
    distance = (travel_time * SONIC_SPEED) / 2
    print(distance)

    if 46 <= distance <= 76:
        GPIO.output(GREEN_LED_PIN, GPIO.HIGH)
        GPIO.output(RED_LED_PIN, GPIO.LOW)
    else:
        GPIO.output(RED_LED_PIN, GPIO.HIGH)
        GPIO.output(GREEN_LED_PIN, GPIO.LOW)

 

def proper_distance_from_screen():
    try:
        while True:
            check_distance()
            time.sleep(1)
    except KeyboardInterrupt:
        GPIO.cleanup()


