from typing import Tuple
from ai.fatigue_detection.main import FatigueDetector
from .utils.singleton import Singleton
from .utils.decorators import check_initialized

class FatigueDetectorService(metaclass = Singleton):
    def __init__(self) -> None:
        self.detector = FatigueDetector()

    def initialize_detector(self, params: Tuple[int, int, float, float, int]) -> None:
        self.detector = FatigueDetector(*params)

    @check_initialized('detector')
    def start_detector(self) -> None:
        self.detector.start()

    @check_initialized('detector')
    def stop_detector(self) -> None:
        self.detector.stop()
