
import RPi.GPIO as GPIO
import time







def photoresitor():
    PHOTORESISTOR_PIN = 6
    RED_LED_PIN = 16

    GPIO.setmode(GPIO.BCM)  
    GPIO.setup(PHOTORESISTOR_PIN, GPIO.OUT)
    GPIO.setup(RED_LED_PIN, GPIO.OUT)
    GPIO.output(PHOTORESISTOR_PIN, GPIO.LOW)
    GPIO.setup(PHOTORESISTOR_PIN, GPIO.IN)
    time.sleep(0.1)
  
    count = 0
    while (GPIO.input(PHOTORESISTOR_PIN) == GPIO.LOW):
        count += 1
    
    print(count)

    if not 400 <= count <= 7000:
        return True
        # GPIO.output(RED_LED_PIN, GPIO.HIGH)
    else:
        return False
        # GPIO.output(RED_LED_PIN, GPIO.LOW)


def check_room_light():
    # RED_LED_PIN = 16
    # GPIO.setmode(GPIO.BCM)  
    # GPIO.setup(RED_LED_PIN, GPIO.OUT)
    # GPIO.output(PHOTORESISTOR_PIN, GPIO.LOW)

    try:
        i = 0
        to_light = [False for _ in range(5)]
        while True:
            to_light[i % 5] = photoresitor()
            print(to_light)
            i += 1
            if all(to_light):
                GPIO.output(RED_LED_PIN, GPIO.HIGH)
            else:
                GPIO.output(RED_LED_PIN, GPIO.LOW)


            photoresitor()
    except KeyboardInterrupt:
        GPIO.cleanup()

