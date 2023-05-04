import RPi.GPIO as GPIO
import time
import paho.mqtt.client as mqtt
import json
from time import sleep

class Buzzer:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        self.connect_to_mqtt()
        
    def beep(self, duration=0.1):
        GPIO.output(self.pin, True)
        time.sleep(duration)
        GPIO.output(self.pin, False)


    def connect_to_mqtt(self):
        mqttBroker ="127.0.0.1"
        client_name = "buzzer"
        topic = 'ultrasonic-sensor/distance'

        client = mqtt.Client(client_name)
        client.connect(mqttBroker) 
        client.subscribe(topic)
        client.on_message=self.on_message 
        client.loop_forever()
        

    def on_message(self, client, userdata, message):
        message_decoded = json.loads(message.payload.decode("utf-8"))
        distance = message_decoded.get("distance", 60)
        print(distance)
        if not (45 < distance < 76):
            print("here")





buzzer = Buzzer(23)

