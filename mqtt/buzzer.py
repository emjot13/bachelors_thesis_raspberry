import RPi.GPIO as GPIO
import time
import paho.mqtt.client as mqtt
import json
from time import sleep
import threading

MQTT_BROKER = "localhost"
CLIENT_NAME = "buzzer"
# TOPIC, INFO = "ultrasonic-sensor/distance", "distance"
TOPIC, INFO = "count", "count"

DISTANCE_FROM_SCREEN_LOW_IN_CM = 45
DISTANCE_FROM_SCREEN_HIGH_IN_CM = 76

class Buzzer:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        self.__connect_to_mqtt()
        
    def __beep(self, duration = 0.1):
        GPIO.output(self.pin, True)
        time.sleep(duration)
        GPIO.output(self.pin, False)


    def __connect_to_mqtt(self):
        self.client = mqtt.Client(CLIENT_NAME)
        self.client.connect(MQTT_BROKER) 


    def start_listening(self):
        self.client.subscribe(TOPIC)
        self.client.on_message=self.__on_message 
        self.client.loop_start()        

    def stop_listening(self):
        self.client.loop_stop()

    def __on_message(self, client, userdata, message):
        message_decoded = json.loads(message.payload.decode("utf-8"))
        distance = message_decoded.get(INFO, 60)
        print(distance)
        if not (DISTANCE_FROM_SCREEN_LOW_IN_CM < distance < DISTANCE_FROM_SCREEN_HIGH_IN_CM):
            print("here")

    def __del__(self):
        GPIO.cleanup()



buzzer = Buzzer(23)
buzzer.start_listening()

def stop_buzzer():
    sleep(3)
    buzzer.stop_listening()

stop_thread = threading.Thread(target=stop_buzzer)
stop_thread.start()


# sleep(1)
# buzzer.stop_listening()
