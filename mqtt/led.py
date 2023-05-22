import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import json

MQTT_BROKER = "localhost"
CLIENT_NAME = "led-light"
TOPIC, INFO = "photoresistor/light", "light_intensity"


class LedLight:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        self.__connect_to_mqtt()

    def __connect_to_mqtt(self):
        self.client = mqtt.Client(CLIENT_NAME)
        self.client.connect(MQTT_BROKER)

    def start_listening(self):
        self.client.subscribe(TOPIC)
        self.client.on_message = self.__on_message
        self.client.loop_start()

    def stop_listening(self):
        self.client.loop_stop()

    def __on_message(self, client, userdata, message):
        message_decoded = json.loads(message.payload.decode("utf-8"))
        light_intensity = message_decoded.get(INFO, 0)
        if light_intensity > 50:  # If light intensity is higher than 50, turn on the LED light
            GPIO.output(self.pin, True)
        else:
            GPIO.output(self.pin, False)

    def __del__(self):
        GPIO.cleanup()
