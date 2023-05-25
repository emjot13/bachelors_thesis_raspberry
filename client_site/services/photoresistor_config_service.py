from mqtt_config.photoresistor_config import PhotoresistorConfig
from .utils.singleton import Singleton
from .utils.decorators import check_initialized

class PhotoresistorConfigService(metaclass = Singleton):
    def __init__(self) -> None:
        self.photoresistor_config = None
        self.is_running = False

    def initialize_photoresistor_config(self) -> None:
        if self.photoresistor_config is None:
            self.photoresistor_config = PhotoresistorConfig()

    @check_initialized("photoresistor_config")
    def start_photoresistor_config(self) -> None:
        self.photoresistor_config.start()
        self.is_running = True

    @check_initialized("photoresistor_config")
    def stop_photoresistor_config(self) -> None:
        self.photoresistor_config.stop()
        self.is_running = False

    @check_initialized("photoresistor_config")
    def photoresistor_config_current_value(self) -> int:
        return self.photoresistor_config.current_measurement()
