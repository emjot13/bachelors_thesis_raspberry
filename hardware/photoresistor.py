
import RPi.GPIO as GPIO
import time

PHOTORESISTOR_PIN = 6


def photoresitor():
        #Output on the pin for 
    GPIO.setup(PHOTORESISTOR_PIN, GPIO.OUT)
    GPIO.output(PHOTORESISTOR_PIN, GPIO.LOW)
    time.sleep(0.1)

    #Change the pin back to input
    GPIO.setup(PHOTORESISTOR_PIN, GPIO.IN)

      
    count = 0
    while (GPIO.input(PHOTORESISTOR_PIN) == GPIO.LOW):
        count += 1
    print(count)


def check_room_light():
    GPIO.setmode(GPIO.BCM)  
    GPIO.setup(PHOTORESISTOR_PIN, GPIO.OUT)
    GPIO.setup(PHOTORESISTOR_PIN, GPIO.IN)


    try:
        while True:
            photoresitor()
    except KeyboardInterrupt:
        GPIO.cleanup()

# check_room_light()