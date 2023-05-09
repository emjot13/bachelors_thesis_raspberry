from typing import Tuple
from ai.fatigue_detection.mainv2 import FatigueDetector

class FatigueDetectorService:
    def __init__(self) -> None:
        self.detector = None

    def initialize_detector(self, params: Tuple[int, int, float, float, int]) -> None:
        if self.detector is None:
            self.detector = FatigueDetector(*params)

    def start_detector(self) -> None:
        if self.detector is not None:
            self.detector.start()

    def stop_detector(self) -> None:
        if self.detector is not None:
            self.detector.stop()
