from .red_led_base import RedLedBase
from client_site.services.utils.hardware_config import HardwareComponent
import threading
import json
import RPi.GPIO as GPIO

class PhotoresistorRedLed(RedLedBase):
    __PIN = 16
    __CLIENT_NAME = "photoresistor-led"
    __TOPIC = "photoresistor/count"
    __INFO = "count"
    __HARDWARE_COMPONENT = HardwareComponent.Photoresistor

    def __init__(self):
        super().__init__(
            pin = self.__PIN,
            client_name = self.__CLIENT_NAME,
            topic = self.__TOPIC,
            info = self.__INFO,
            hardware_component = self.__HARDWARE_COMPONENT
        )


    # below tried overwriting
    def start_listening(self):
        print("photoresistor start listening")
        if self.processing:
            return
        self.client.subscribe(self.topic)
        self.client.on_message = self._on_message
        self.processing = True  # Enable message processing
        self.thread = threading.Thread(target=self._message_processing_loop)
        self.thread.start()  # Start the message processing thread

    def stop_listening(self):
        print("photoresistor stop listening")
        GPIO.output(self.pin, False)
        self.processing = False  # Disable message processing
        if self.thread:
            self.thread.join()  # Wait for the thread to complete

    def _on_message(self, client, userdata, message):
        if not self.processing:  # Skip message processing if disabled
            return

        message_decoded = json.loads(message.payload.decode("utf-8"))
        value = message_decoded.get(self.info, 0)
        print("photoresistor got: ", value)

        if not self.min_threshold <= value <= self.max_threshold:
            GPIO.output(self.pin, GPIO.HIGH)
        else:
            GPIO.output(self.pin, GPIO.LOW)