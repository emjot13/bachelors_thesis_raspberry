from mqtt_config.distance_sensor_config import DistanceSensorConfig
from .utils.singleton import Singleton
from .utils.decorators import check_initialized

class DistanceSensorConfigService(metaclass = Singleton):
    def __init__(self) -> None:
        self.distance_sensor = None
        self.is_running = False

    def initialize_distance_sensor_config(self) -> None:
        if self.distance_sensor is None:
            self.distance_sensor = DistanceSensorConfig()


    @check_initialized("distance_sensor")
    def start_distance_sensor_config(self) -> None:
        self.distance_sensor.start()
        self.is_running = True

    @check_initialized("distance_sensor")
    def stop_distance_sensor_config(self) -> None:
        self.distance_sensor.stop()
        self.is_running = False

    @check_initialized("distance_sensor")
    def distance_sensor_config_current_value(self) -> int:
        return self.distance_sensor.current_measurement()
