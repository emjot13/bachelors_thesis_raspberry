import time
from typing import Tuple
import cv2
from . import landmarks
from hardware.buzzer import intermittent_beep
import database.client as database
import threading
from imutils.video import VideoStream




class FatigueDetector:
    __FRAME_SIZE = (450, 450)
    __TIME_FOR_CAMERA_SETUP = 1

    def __init__(
        self,
        closed_eyes_threshold_in_seconds: int = 3,
        FPS: int = 24,
        eye_aspect_ratio_threshold: float = 0.40,
        yawn_threshold: float = 10,
        database_writes_frequency_in_seconds: int = 30) -> None:
        
        self.__eye_aspect_ratio_threshold = eye_aspect_ratio_threshold
        self.__yawn_threshold = yawn_threshold
        self.__database_writes_frequency_in_seconds = database_writes_frequency_in_seconds
        self.__FPS = FPS
        
        self.__closed_eyes_threshold_in_frames = FPS * closed_eyes_threshold_in_seconds
        self.__landmarks = landmarks.Landmarks()
        self.__global_yawning_counter = 0
        self.__global_sleeping_counter = 0
        self.__running = False
        self.__database_writer = threading.Thread(target = self.__write_to_database_every_x_seconds)
        self.__buzzer_thread = None
        self.__buzzer_lock = threading.Lock()

    def __write_to_database_every_x_seconds(self) -> None:
        while True:
            time.sleep(self.__database_writes_frequency_in_seconds)
            database.insert_data(self.__global_yawning_counter, self.__global_sleeping_counter)


    def __check_user_state(self, eyes_aspect_ratio: float, lips_distance: float) -> None:
        has_closed_eyes = eyes_aspect_ratio < self.__eye_aspect_ratio_threshold
        if has_closed_eyes:
            self.__closed_eyes_frame_counter += 1
            had_closed_eyes_for_longer_than_threshold = self.__closed_eyes_frame_counter >= self.__closed_eyes_threshold_in_frames
            if had_closed_eyes_for_longer_than_threshold:
                self.__is_sleeping = True
                with self.__buzzer_lock:
                    if self.__buzzer_thread is None or not self.__buzzer_thread.is_alive():
                        self.__buzzer_thread = threading.Thread(target = intermittent_beep)
                        self.__buzzer_thread.start()
            return
        else:
            self.__closed_eyes_frame_counter = 0
        
        was_sleeping_in_previous_frame = self.__is_sleeping and eyes_aspect_ratio > self.__eye_aspect_ratio_threshold
        if was_sleeping_in_previous_frame:
            self.__global_sleeping_counter += 1
            self.__closed_eyes_frame_counter = 0
            self.__is_sleeping = False
            return

        is_only_yawning = not self.__is_sleeping and lips_distance > self.__yawn_threshold
        if is_only_yawning:
            self.__is_yawning = True
            return 
        
        was_yawning_in_previous_frame = self.__is_yawning and lips_distance < self.__yawn_threshold
        if was_yawning_in_previous_frame:
            self.__is_yawning = False
            self.__global_yawning_counter += 1      


    def __analyze_frame(self, rects: Tuple[int, int, int, int], gray_image: Tuple[int, int]) -> None:
        for (bottom_left_corner_x, bottom_left_corner_y, width, height) in rects:
            bottom_left_corner = (bottom_left_corner_x, bottom_left_corner_y)
            top_right_corner = (bottom_left_corner_x + width, bottom_left_corner_y + height)
            rect_coordinates = (*bottom_left_corner, *top_right_corner)
            eyes_aspect_ratio = self.__landmarks.eyes_aspect_ratio(gray_image, rect_coordinates)
            lips_distance = self.__landmarks.lip_distance(gray_image, rect_coordinates)
            self.__check_user_state(eyes_aspect_ratio, lips_distance)


    def __run(self) -> None:
        print("started fatigue analysis")
        self.__is_yawning, self.__is_sleeping = False, False
        self.__closed_eyes_frame_counter = 0

        vs = VideoStream(framerate=self.__FPS).start()
        time.sleep(self.__TIME_FOR_CAMERA_SETUP)

        while self.__running:
            frame = cv2.resize(vs.read(), self.__FRAME_SIZE)
            gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rects = self.__landmarks.get_rects(gray_image)
            self.__analyze_frame(rects, gray_image)

        vs.stop()


    def start(self) -> None:
        self.__running = True
        detector_tread = threading.Thread(target=self.__run)
        detector_tread.start()
        self.__database_writer.start()


    
    def stop(self) -> None:
        self.__running = False
        self.__database_writer.join()


