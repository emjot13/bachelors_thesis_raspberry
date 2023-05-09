import time
import threading
import RPi.GPIO as GPIO
from buzzer import Buzzer


class UltrasonicSensor:
    def __init__(self, trig_pin, echo_pin, buzzer_pin):
        self.trig_pin = trig_pin
        self.echo_pin = echo_pin
        self.buzzer_pin = buzzer_pin
        self.measuring = False
        self.distance = 0

    def measure_distance(self):
        while self.measuring:
            # Set trigger to HIGH
            GPIO.output(self.trig_pin, GPIO.HIGH)

            # Wait for 10us
            time.sleep(0.00001)

            # Set trigger to LOW
            GPIO.output(self.trig_pin, GPIO.LOW)

            # Wait for echo to start
            while GPIO.input(self.echo_pin) == GPIO.LOW:
                pass

            # Wait for echo to end
            start_time = time.time()
            while GPIO.input(self.echo_pin) == GPIO.HIGH:
                pass
            end_time = time.time()

            # Calculate distance in cm
            duration = end_time - start_time
            distance = round(duration * 17150, 2)

            # Update distance attribute
            self.distance = distance

            # Check if buzzer should beep
            if distance < 46 or distance > 76:
                GPIO.output(self.buzzer_pin, GPIO.HIGH)
            else:
                GPIO.output(self.buzzer_pin, GPIO.LOW)

            # Sleep for 0.1s before next measurement
            time.sleep(0.1)

    def start_measurement(self):
        self.measuring = True
        t = threading.Thread(target=self.measure_distance)
        t.start()

    def stop_measurement(self):
        self.measuring = False