import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import json
import threading
from time import sleep
from client_site.services.utils.hardware_config import min_max_values_for_hardware_component, HardwareComponent 


class RedLedBase:
    __MQTT_BROKER = "localhost"


    def __init__(self, pin: int, client_name: str, topic: str, info: str, hardware_component: HardwareComponent):
        self.pin = pin
        self.topic = topic
        self.info = info
        self.processing = False  # Flag to control message processing
        self.min_threshold, self.max_threshold = min_max_values_for_hardware_component(hardware_component)

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT, initial=GPIO.LOW)
        self._connect_to_mqtt(client_name)

    def _connect_to_mqtt(self, client_name):
        self.client = mqtt.Client(client_name)
        self.client.connect(self.__MQTT_BROKER)

    def start_listening(self):
        # print(cls)
        if self.processing:
            return
        self.client.subscribe(self.topic)
        self.client.on_message = self.__on_message
        self.processing = True  # Enable message processing
        self.thread = threading.Thread(target=self.__message_processing_loop)
        self.thread.start()  # Start the message processing thread

    def stop_listening(self):
        GPIO.output(self.pin, False)
        self.processing = False  # Disable message processing
        if self.thread:
            self.thread.join()  # Wait for the thread to complete

    def _on_message(self, client, userdata, message):
        if not self.processing:  # Skip message processing if disabled
            return

        message_decoded = json.loads(message.payload.decode("utf-8"))
        value = message_decoded.get(self.info, 0)
        if not self.min_threshold <= value <= self.max_threshold:
            GPIO.output(self.pin, GPIO.HIGH)
        else:
            GPIO.output(self.pin, GPIO.LOW)

    def _message_processing_loop(self):
        self.client.loop_start()  # Start the MQTT client loop

        while self.processing:
            sleep(0.1)  # Adjust sleep duration as needed

        self.client.loop_stop()  # Stop the MQTT client loop

    def __del__(self):
        GPIO.cleanup()




