from mqtt.red_led.photoresistor_red_led import PhotoresistorRedLed
from .utils.singleton import Singleton
from .utils.decorators import check_initialized

class PhotoresistorRedLedService(metaclass = Singleton):
    def __init__(self) -> None:
        self.photoresistor_red_led = None

    def initialize_photoresistor_red_led(self) -> None:
        self.photoresistor_red_led = PhotoresistorRedLed()


    @check_initialized("photoresistor_red_led")
    def start_photoresistor_red_led(self) -> None:
        self.photoresistor_red_led.start_listening()

    @check_initialized("photoresistor_red_led")
    def stop_photoresistor_red_led(self) -> None:
        self.photoresistor_red_led.stop_listening()


