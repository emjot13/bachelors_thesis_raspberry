import time
import threading
import RPi.GPIO as GPIO
import json
import paho.mqtt.client as mqtt 


MQTT_BROKER ="localhost" 
CLIENT_NAME = "RoomLightSensor"
TOPIC = 'room-light-sensor/count'
TIME_BETWEEN_MEASUREMENTS = 0.3 # 0.3s


class RoomLightSensor:
    def __init__(self, photoresistor_pin):
        self.photoresistor_pin = photoresistor_pin
        self.measuring = False
        self.__set_up_gpio()
        self.__connect_to_mqtt()

    def __set_up_gpio(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)


    def __connect_to_mqtt(self):
        mqtt_client = mqtt.Client(CLIENT_NAME)
        mqtt_client.connect(MQTT_BROKER) 
        self.mqtt_client = mqtt_client

    def __publish_count(self, count):
        payload = json.dumps({'count': count})
        self.mqtt_client.publish(TOPIC, payload)

    def __measure_count(self):
        while self.measuring:
            GPIO.setup(self.photoresistor_pin, GPIO.OUT)
            time.sleep(0.001)

            # Change the pin mode to input
            GPIO.setup(self.photoresistor_pin, GPIO.IN)            

            count = 0
            while (GPIO.input(self.photoresistor_pin) == GPIO.LOW):
                count += 1
            
            print(count)

            self.__publish_count(count)

            time.sleep(TIME_BETWEEN_MEASUREMENTS)

    def start_measurement(self):
        self.measuring = True
        t = threading.Thread(target=self.__measure_count)
        t.start()

    def stop_measurement(self):
        self.measuring = False

    def __del__(self):
        GPIO.cleanup()


sensor = RoomLightSensor(photoresistor_pin=6)

sensor.start_measurement()
