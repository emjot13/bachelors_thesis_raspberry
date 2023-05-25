import json
import enum
from typing import Union, Tuple, Dict


__HARDWARE_CONFIG_PATH = "./mqtt_config/hardware_config.json"
# relative to manage.py file!
__FILE_OPEN_MODE = "r+"
# for reading and writing at the same time
__INDENT = 4
# it makes json prettier :D


class HardwareComponent(enum.Enum):
    Photoresistor = "photoresistor"
    Distance_sensor = "distance_sensor"




def modify_min_max_values_for_hardware_component(hardware: HardwareComponent, min_threshold: Union[float, int], max_threshold: Union[float, int]) -> None:
    with open(__HARDWARE_CONFIG_PATH, __FILE_OPEN_MODE) as file:
        data = json.load(file)

        data[hardware.value]["min"] = min_threshold
        data[hardware.value]["max"] = max_threshold

        # Move the file cursor to the beginning of the file
        file.seek(0)

        json.dump(data, file, indent = __INDENT)
        file.truncate()


def min_max_values_for_hardware_component(hardware: HardwareComponent):
    with open(__HARDWARE_CONFIG_PATH, __FILE_OPEN_MODE) as file:
        data: Dict[str, Dict[str, Union[float, int]]] = json.load(file)

    min_threshold = data[hardware.value]["min"] 
    max_threshold = data[hardware.value]["max"]

    return min_threshold, max_threshold
