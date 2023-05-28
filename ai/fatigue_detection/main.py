import time
from typing import Tuple
import cv2
from . import landmarks
from hardware.buzzer import intermittent_beep
import database.client as database
import threading
from imutils.video import VideoStream




class FatigueDetector:
    def __init__(
        self,
        closed_eyes_seconds_threshold: int = 3,
        FPS: int = 24,
        eye_aspect_ratio_threshold: float = 0.40,
        yawn_threshold: float = 10,
        database_writes_frequency_seconds: int = 30) -> None:
        
        self.eye_aspect_ratio_threshold = eye_aspect_ratio_threshold
        self.yawn_threshold = yawn_threshold
        self.database_writes_frequency_seconds = database_writes_frequency_seconds
        self.FPS = FPS
        self.closed_eyes_threshold_fps = int(FPS * closed_eyes_seconds_threshold / 4)
        self.landmarks = landmarks.Landmarks()
        self.yawning_counter = 0
        self.sleeping_counter = 0
        self.running = False
        self.database_writer = threading.Thread(target = self.__write_to_database_every_x_seconds)
        self.buzzer_thread = None
        self.buzzer_lock = threading.Lock()
        print("closed_eyes_threshold_fps: ", self.closed_eyes_threshold_fps)        

    def __write_to_database_every_x_seconds(self) -> None:
        while True:
            time.sleep(self.database_writes_frequency_seconds)
            database.insert_data(self.yawning_counter, self.sleeping_counter)


    def __analyze_frame(self, rects: Tuple[int, int, int, int], gray_image: any) -> None:
        for (bottom_left_corner_x, bottom_left_corner_y, width, height) in rects:
            bottom_left_corner = (bottom_left_corner_x, bottom_left_corner_y)
            top_right_corner = (bottom_left_corner_x + width, bottom_left_corner_y + height)
            rect_coordinates = (*bottom_left_corner, *top_right_corner)
            eyes_aspect_ratio = self.landmarks.eyes_aspect_ratio(gray_image, rect_coordinates)
            lips_distance = self.landmarks.lip_distance(gray_image, rect_coordinates)

            print("frame_counter: ", self.frame_counter)

            print("----------- EAR --------------")
            print(eyes_aspect_ratio)
            print("----------- EAR --------------")

            was_sleeping = self.is_sleeping and eyes_aspect_ratio > self.eye_aspect_ratio_threshold
            if was_sleeping:
                print("BEEEEP BEEEEP!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                self.sleeping_counter += 1
                self.frame_counter = 0
                self.is_sleeping = False
                continue

            has_closed_eyes = eyes_aspect_ratio < self.eye_aspect_ratio_threshold
            if has_closed_eyes:
                print("HAS CLOSED EYES")
                self.frame_counter += 1
            
            if self.frame_counter >= self.closed_eyes_threshold_fps:
                self.is_sleeping = True
                with self.buzzer_lock:
                    if self.buzzer_thread is None or not self.buzzer_thread.is_alive():
                        self.buzzer_thread = threading.Thread(target = intermittent_beep)
                        self.buzzer_thread.start()
                        print("started beep thread")               


            is_just_yawning = not self.is_sleeping and lips_distance > self.yawn_threshold
            if is_just_yawning:
                self.is_yawning = True
                continue
            
            was_yawning = self.is_yawning and lips_distance < self.yawn_threshold
            if was_yawning:
                self.is_yawning = False
                self.yawning_counter += 1
                


    def __run(self) -> None:
        print("started fatigue analysis")
        self.is_yawning, self.is_sleeping = False, False
        self.frame_counter = 0

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
        self.database_writer.start()


    
    def stop(self):
        self.running = False
        self.database_writer.join()


