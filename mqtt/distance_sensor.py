import time
import threading
import RPi.GPIO as GPIO
import json
import paho.mqtt.client as mqtt 


MQTT_BROKER ="localhost" 
CLIENT_NAME = "UltrasonicSensor"
TOPIC = 'ultrasonic-sensor/distance'
TRIGGER_SENSOR_TIME = 0.00001 # 10us
SONIC_SPEED_IN_CM_PER_SEC = 34300 
TIME_BETWEEN_MEASUREMENTS = 0.1 # 100ms


class UltrasonicSensor:
    def __init__(self, trig_pin, echo_pin):
        self.trig_pin = trig_pin
        self.echo_pin = echo_pin
        self.measuring = False
        self.__set_up_gpio()
        self.__connect_to_mqtt()

    @staticmethod
    def calculate_distance_in_cm(travel_time):
        return (travel_time * SONIC_SPEED_IN_CM_PER_SEC) 


    def __set_up_gpio(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.trig_pin, GPIO.OUT)
        GPIO.setup(self.echo_pin, GPIO.IN)

    def __connect_to_mqtt(self):
        mqtt_client = mqtt.Client(CLIENT_NAME)
        mqtt_client.connect(MQTT_BROKER) 
        self.mqtt_client = mqtt_client


    def __publish_distance(self, distance):
        payload = json.dumps({'distance': distance})
        self.mqtt_client.publish(TOPIC, payload)


    def __measure_distance(self):
        while self.measuring:
            # Set trigger to HIGH
            GPIO.output(self.trig_pin, GPIO.HIGH)

            # Wait for 10us
            time.sleep(TRIGGER_SENSOR_TIME)

            # Set trigger to LOW
            GPIO.output(self.trig_pin, GPIO.LOW)


            while GPIO.input(self.echo_pin) == GPIO.LOW:
                start_time = time.time()

            while GPIO.input(self.echo_pin) == GPIO.HIGH:
                stop_time = time.time()

            travel_time = (stop_time - start_time) / 2
            # dividing by 2 cause the pulse goes there and back
            
            distance_in_cm = self.calculate_distance_in_cm(travel_time)

            self.__publish_distance(distance_in_cm)

            time.sleep(TIME_BETWEEN_MEASUREMENTS)

    def start_measurement(self):
        self.measuring = True
        t = threading.Thread(target=self.__measure_distance)
        t.start()

    
    def stop_measurement(self):
        self.measuring = False

    
    def __del__(self):
        GPIO.cleanup()


sensor = UltrasonicSensor(trig_pin=25, echo_pin=24)

sensor.start_measurement()
