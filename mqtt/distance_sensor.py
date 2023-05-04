import time
import threading
import RPi.GPIO as GPIO
import json
import paho.mqtt.client as mqtt 


class UltrasonicSensor:
    def __init__(self, trig_pin, echo_pin):
        self.trig_pin = trig_pin
        self.echo_pin = echo_pin
        self.measuring = False

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.trig_pin, GPIO.OUT)
        GPIO.setup(self.echo_pin, GPIO.IN)
        self.connect_to_mqtt()


    def connect_to_mqtt(self):
        mqtt_broker ="localhost" 
        client_name = "UltrasonicSensor"
        mqtt_client = mqtt.Client(client_name)
        mqtt_client.connect(mqtt_broker) 
        self.mqtt_client = mqtt_client


    def publish_distance(self, distance):
        topic = 'ultrasonic-sensor/distance'
        payload = json.dumps({'distance': distance})
        self.mqtt_client.publish(topic, payload)



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

            self.publish_distance(distance)

            time.sleep(0.1)

    def start_measurement(self):
        self.measuring = True
        t = threading.Thread(target=self.measure_distance)
        t.start()

    def stop_measurement(self):
        self.measuring = False


sensor = UltrasonicSensor(trig_pin=25, echo_pin=24)

sensor.start_measurement()
