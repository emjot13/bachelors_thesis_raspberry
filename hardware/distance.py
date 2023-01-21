import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)

TRIG = 25
ECHO = 23

print("Distance Measurement In Progress")

GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)
try:
    while True:
        
        GPIO.output(TRIG, GPIO.LOW)
        print("Waiting For Sensor To Settle")
        time.sleep(2)
        
        GPIO.output(TRIG, GPIO.HIGH)
        print("here")
        time.sleep(0.00001)
        GPIO.output(TRIG, GPIO.LOW)
        
        while GPIO.input(ECHO)==0:
            pulse_start = time.time()
       
        print("here1")

        while GPIO.input(ECHO)==1:
            pulse_end = time.time()
        
        print("here2")

        pulse_duration = pulse_end - pulse_start
        
        distance = pulse_duration * 17150
        
        distance = round(distance, 2)
        
        print("Distance: ",distance,"cm")
        
except KeyboardInterrupt: # If there is a KeyboardInterrupt (when you press ctrl+c), exit the program
    print("Cleaning up!")
    GPIO.cleanup()
