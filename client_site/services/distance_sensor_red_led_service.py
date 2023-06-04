from mqtt.red_led.distance_sensor_red_led import DistanceSensorRedLed
from .utils.singleton import Singleton
from .utils.decorators import check_initialized

class DistanceSensorRedLedService(metaclass = Singleton):
    def __init__(self) -> None:
        self.distance_sensor_red_led = None

    def initialize_distance_sensor_red_led(self) -> None:
        self.distance_sensor_red_led = DistanceSensorRedLed()


    @check_initialized("distance_sensor_red_led")
    def start_distance_sensor_red_led(self) -> None:
        self.distance_sensor_red_led.start_listening()

    @check_initialized("distance_sensor_red_led")
    def stop_distance_sensor_red_led(self) -> None:
        self.distance_sensor_red_led.stop_listening()


