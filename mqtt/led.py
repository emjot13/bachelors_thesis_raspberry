import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import json
from time import sleep

MQTT_BROKER = "localhost"
CLIENT_NAME = "led-light"
# TOPIC, INFO = "photoresistor/light", "light_intensity"
TOPIC, INFO = "count", "count"


# class LedLight:
#     def __init__(self, pin):
#         self.pin = pin
#         GPIO.setmode(GPIO.BCM)
#         GPIO.setup(self.pin, GPIO.OUT)
#         self.__connect_to_mqtt()

#     def __connect_to_mqtt(self):
#         self.client = mqtt.Client(CLIENT_NAME)
#         self.client.connect(MQTT_BROKER)

#     def start_listening(self):
#         self.client.subscribe(TOPIC)
#         self.client.on_message = self.__on_message
#         self.client.loop_start()

#     def stop_listening(self):
#         self.client.loop_stop()

#     def __on_message(self, client, userdata, message):
#         message_decoded = json.loads(message.payload.decode("utf-8"))
#         light_intensity = message_decoded.get(INFO, 0)
#         if light_intensity > 50:  # If light intensity is higher than 50, turn on the LED light
#             GPIO.output(self.pin, True)
#         else:
#             GPIO.output(self.pin, False)

#     def __del__(self):
#         GPIO.cleanup()

import threading

class LedLight:
    def __init__(self, pin):
        self.pin = pin
        self.processing = False  # Flag to control message processing
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        self.__connect_to_mqtt()
        self.thread = threading.Thread(target=self.__message_processing_loop)  # Create a thread for message processing

    def __connect_to_mqtt(self):
        self.client = mqtt.Client(CLIENT_NAME)
        self.client.connect(MQTT_BROKER)

    def start_listening(self):
        self.client.subscribe(TOPIC)
        self.client.on_message = self.__on_message
        self.processing = True  # Enable message processing
        self.thread.start()  # Start the message processing thread

    def stop_listening(self):
        self.processing = False  # Disable message processing
        self.thread.join()  # Wait for the thread to complete

    def __on_message(self, client, userdata, message):
        if not self.processing:  # Skip message processing if disabled
            return

        message_decoded = json.loads(message.payload.decode("utf-8"))
        light_intensity = message_decoded.get(INFO, 0)
        if light_intensity > 50:  # If light intensity is higher than 50, turn on the LED light
            GPIO.output(self.pin, True)
        else:
            GPIO.output(self.pin, False)

    def __message_processing_loop(self):
        self.client.loop_start()  # Start the MQTT client loop

        while self.processing:
            time.sleep(0.1)  # Adjust sleep duration as needed

        self.client.loop_stop()  # Stop the MQTT client loop

    def __del__(self):
        GPIO.cleanup()


red_led = LedLight(17)
red_led.start_listening()
sleep(5)