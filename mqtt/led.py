import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import json
from time import sleep
from client_site.services.utils.hardware_config import min_max_values_for_hardware_component, HardwareComponent 


MQTT_BROKER = "localhost"
CLIENT_NAME = "led-light"
TOPIC, INFO =  "photoresistor/count", "count"


import threading

class LedLight:
    def __init__(self, pin: int):
        self.pin = pin
        self.processing = False  # Flag to control message processing
        self.min_threshold, self.max_threshold = min_max_values_for_hardware_component(HardwareComponent.Photoresistor)

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT, initial = GPIO.LOW)
        self.__connect_to_mqtt()

    def __connect_to_mqtt(self):
        self.client = mqtt.Client(CLIENT_NAME)
        self.client.connect(MQTT_BROKER)

    def start_listening(self):
        if self.processing:
           return
        self.client.subscribe(TOPIC)
        self.client.on_message = self.__on_message
        self.processing = True  # Enable message processing
        self.thread = threading.Thread(target=self.__message_processing_loop)
        self.thread.start()  # Start the message processing thread

    def stop_listening(self):
        print("stop listening in LedLight")
        GPIO.output(self.pin, False)
        self.processing = False  # Disable message processing
        if self.thread:
            self.thread.join()  # Wait for the thread to complete

    def __on_message(self, client, userdata, message):
        if not self.processing:  # Skip message processing if disabled
            return

        message_decoded = json.loads(message.payload.decode("utf-8"))
        value = message_decoded.get(INFO, 0)
        if not self.min_threshold <= value <= self.max_threshold:  # If light intensity is higher than 50, turn on the LED light
            GPIO.output(self.pin, GPIO.HIGH)
        else:
            GPIO.output(self.pin, GPIO.LOW)

    def __message_processing_loop(self):
        self.client.loop_start()  # Start the MQTT client loop

        while self.processing:
            sleep(0.1)  # Adjust sleep duration as needed

        self.client.loop_stop()  # Stop the MQTT client loop

    def __del__(self):
        GPIO.cleanup()






