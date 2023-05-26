from client_site.services.utils.hardware_config import HardwareComponent, min_max_values_for_hardware_component
import paho.mqtt.client as mqtt
from time import sleep
import threading
import RPi.GPIO as GPIO
import json

# info for me - it is the one next to the green led

class DistanceSensorRedLed():
    __PIN = 17
    __CLIENT_NAME = "distance-sensor-led"
    __TOPIC = "distance_sensor/distance_in_cm"
    __INFO = "distance_in_cm"
    __HARDWARE_COMPONENT = HardwareComponent.Distance_sensor
    __MQTT_BROKER = "localhost"
    __DEFAULT_DISTANCE_VALUE = 50
    

    def __init__(self):
        self.processing = False  # Flag to controlling message processing
        self.min_threshold, self.max_threshold = min_max_values_for_hardware_component(self.__HARDWARE_COMPONENT)

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.__PIN, GPIO.OUT, initial = GPIO.LOW)
        self.__connect_to_mqtt()

    def __connect_to_mqtt(self):
        self.client = mqtt.Client(self.__CLIENT_NAME)
        self.client.connect(self.__MQTT_BROKER)

    def update_thresholds(self):
        self.__min_threshold, self.__max_threshold = min_max_values_for_hardware_component(self.__HARDWARE_COMPONENT)


    def start_listening(self):
        print("distance start")
        if self.processing:
            return
        self.client.subscribe(self.__TOPIC)
        self.client.on_message = self.__on_message
        self.processing = True  # Enable message processing
        self.thread = threading.Thread(target=self.__message_processing_loop)
        self.thread.start()  # Start the message processing thread

    def stop_listening(self):
        print("distance stop")
        GPIO.output(self.__PIN, False)
        self.processing = False  # Disable message processing
        if self.thread:
            self.thread.join()  # Wait for the thread to complete

    def __on_message(self, client, userdata, message):
        if not self.processing:  # Skip message processing if disabled
            return

        message_decoded = json.loads(message.payload.decode("utf-8"))
        value = message_decoded.get(self.__INFO, self.__DEFAULT_DISTANCE_VALUE)
        print("distance: ", value)
        if not self.min_threshold <= value <= self.max_threshold:
            GPIO.output(self.__PIN, GPIO.HIGH)
        else:
            GPIO.output(self.__PIN, GPIO.LOW)

    def __message_processing_loop(self):
        self.client.loop_start()  
        while self.processing:
            sleep(0.1)  # sleep to block this loop, else it terminates

        self.client.loop_stop()  

    def __del__(self):
        GPIO.cleanup()