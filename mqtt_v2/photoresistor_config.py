import paho.mqtt.client as mqtt
import json
import time

BROKER = "localhost"
CLIENT_NAME = "photoresistor_config"

class PhotoresistorConfig:
    def __init__(self, topic = "count"):
        self.__client = mqtt.Client()
        self.__client.on_message = self.__on_message
        self.__current_measurement = 0
        self.__topic = topic

        self.__client.connect(BROKER)
        self.subscribe()

    
    def subscribe(self):
        # self.subscriptions[topic] = callback
        self.__client.subscribe(self.__topic)
    
    def start(self):
        self.__client.loop_start()
    
    def stop(self):
        self.__client.loop_stop()
        self.__current_measurement = 0


    def current_measurement(self):
        return self.__current_measurement
    
    def __on_message(self, client, userdata, message):
        payload = json.loads(message.payload.decode("utf-8"))
        count = payload["count"]
        print("PhotoresistorConfig: ", count)

        self.__current_measurement = count


