# import RPi.GPIO as GPIO
# import time
# from led import led
# import threading
 
# #GPIO Mode (BOARD / BCM)

# def configuration():
#     # stop_green = True
#     # stop_red = True
#     # green_led = threading.Thread(target=led, args=("green", lambda: stop_green))
#     # red_led = threading.Thread(target=led, args=("red", lambda: stop_red))


#     GPIO.setmode(GPIO.BCM)
    
#     #set GPIO Pins
#     GPIO_TRIGGER = 25
#     GPIO_ECHO = 24
    
#     #set GPIO direction (IN / OUT)
#     GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
#     GPIO.setup(GPIO_ECHO, GPIO.IN)
 
#     # set Trigger to HIGH
#     GPIO.output(GPIO_TRIGGER, True)
 
#     # set Trigger after 0.01ms to LOW
#     time.sleep(0.00001)
#     GPIO.output(GPIO_TRIGGER, False)

#     while True:   
#         # save StartTime
#         while GPIO.input(GPIO_ECHO) == 0:
#             StartTime = time.time()
    
#         # save time of arrival
#         while GPIO.input(GPIO_ECHO) == 1:
#             StopTime = time.time()
    
#         # time difference between start and arrival
#         TimeElapsed = StopTime - StartTime
#         # multiply with the sonic speed (34300 cm/s)
#         # and divide by 2, because there and back
#         distance = (TimeElapsed * 34300) / 2
#         print(distance)
#         # if 46 <= distance <= 76:
#         #     # if not stop_red:
#         #     #     red_led.join()
#         #     # stop_red = True
#         #     # stop_green = False
#         #     # green_led.start()

#         # else:
#             # if not stop_green:
#             #     green_led.join()
#             # stop_green = True
#             # stop_red = False
#             # red_led.start()


 
 
# if __name__ == '__main__':
#     try:
#         configuration()
#     except KeyboardInterrupt:
#         print("Measurement stopped by User")
#         GPIO.cleanup()


#Libraries
import RPi.GPIO as GPIO
import time
 
#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
#set GPIO Pins
GPIO_TRIGGER = 25
GPIO_ECHO = 24
 
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
 
def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance
 
if __name__ == '__main__':
    try:
        while True:
            dist = distance()
            print ("Measured Distance = %.1f cm" % dist)
            time.sleep(1)
 
        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()