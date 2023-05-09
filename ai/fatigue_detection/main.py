import time
from typing import Tuple
import cv2
from . import landmarks
from hardware.buzzer import beep
import database.client as database
import threading
from imutils.video import VideoStream




class FatigueDetector:
    def __init__(
        self,
        closed_eyes_seconds_threshold: int = 3,
        FPS: int = 24,
        eye_aspect_ratio_threshold: float = 0.25,
        yawn_threshold: float = 10,
        database_writes_frequency_seconds: int = 10) -> None:
        
        self.eye_aspect_ratio_threshold = eye_aspect_ratio_threshold
        self.yawn_threshold = yawn_threshold
        self.database_writes_frequency_seconds = database_writes_frequency_seconds
        self.FPS = FPS
        self.closed_eyes_threshold_fps = FPS * closed_eyes_seconds_threshold
        self.landmarks = landmarks.Landmarks()
        self.yawning_counter = 0
        self.sleeping_counter = 0
        self.running = False
        self.database_writer = threading.Thread(target=self.__write_to_database_every_x_seconds)
        self.buzzer = threading.Thread(target=beep)
        

    def __write_to_database_every_x_seconds(self) -> None:
        while True:
            time.sleep(self.database_writes_frequency_seconds)
            database.insert_data(self.yawning_counter, self.sleeping_counter)


    def __analyze_frame(self, rects: Tuple[int, int, int, int], gray_image: any) -> None:
        frame_counter = 0
        is_yawning, is_sleeping = False, False

        for (x, y, w, h) in rects:
            rect = (x, y, x + w, y + h)
            eyes_aspect_ratio = self.landmarks.eyes_aspect_ratio(gray_image, rect)
            lips_distance = self.landmarks.lip_distance(gray_image, rect)
            print(eyes_aspect_ratio)

            was_sleeping = is_sleeping and eyes_aspect_ratio > self.eye_aspect_ratio_threshold
            has_closed_eyes = eyes_aspect_ratio < self.eye_aspect_ratio_threshold
            is_just_yawning = not is_sleeping and lips_distance > self.yawn_threshold
            was_yawning =  is_yawning and lips_distance < self.yawn_threshold

            if was_sleeping:
                self.sleeping_counter += 1
                frame_counter = 0
                is_sleeping = False
                self.buzzer.start()

            if has_closed_eyes:
                print("closed eyes")
                frame_counter += 1
            
            if frame_counter >= self.closed_eyes_threshold_fps:
                is_sleeping = True

            if is_just_yawning:
                is_yawning = True

            elif was_yawning:
                is_yawning = False
                self.yawning_counter += 1
                print(self.yawning_counter)


    def __run(self) -> None:
        print("started fatigue analysis")

        vs = VideoStream(framerate=self.FPS).start()
        time.sleep(1)

        while self.running:
            frame = cv2.resize(vs.read(), (450, 450))
            gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rects = self.landmarks.get_rects(gray_image)
            self.__analyze_frame(rects, gray_image)

        vs.stop()




    def start(self):
        self.running = True
        t = threading.Thread(target=self.__run)
        t.start()
        # self.database_writer.start()


    
    def stop(self):
        self.running = False
        # self.database_writer.join()


