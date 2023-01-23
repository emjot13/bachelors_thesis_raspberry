from imutils.video import VideoStream
import time
import cv2
import threading
from os.path import exists
from os import remove
import database.client as database
# from hardware.buzzer import beep
from . import landmarks

class FatigueDetector:

    def __init__(self, closed_eyes_seconds_threshold, FPS, eye_aspect_ratio_threshold, yawn_threshold, database_writes_frequency_seconds):
        self.eye_aspect_ratio_threshold = eye_aspect_ratio_threshold 
        self.yawn_threshold = yawn_threshold
        self.database_writes_frequency_seconds = database_writes_frequency_seconds
        self.FPS = FPS
        
        self.closed_eyes_threshold_fps = FPS * closed_eyes_seconds_threshold
        self.landmarks = landmarks.Landmarks()
        self.yawning_counter, self.sleeping_counter = 0, 0
        # self.database_writer = threading.Thread(target=self.write_to_database_every_x_seconds)
        # self.buzzer = threading.Thread(target=beep)



    def write_to_database_every_x_seconds(self):
        while True:
            time.sleep(self.database_writes_frequency_seconds)
            database.insert_data(self.yawning_counter, self.sleeping_counter)


    @staticmethod
    def check_logical_files():
        pause = "logical_files/pause"
        end = "logical_files/end"
        if exists(pause):
            remove(pause)
            return "pause"
        if exists(end):
            remove(end)
            return "end"



    def run(self):  # main detecting function
        print("started fatique analysis")
        frame_counter = 0
        yawn, sleep = False, False

        vs = VideoStream(framerate = self.FPS).start()  # starts video
        time.sleep(1)
        
        # self.database_writer.start()

        while True:
            if FatigueDetector.check_logical_files():
                vs.stop()
                # self.database_writer.join()
                break

            frame = cv2.resize(vs.read(), (450, 450))
            gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rects = self.landmarks.get_rects(gray_image)
            for (x, y, w, h) in rects:
                rect = (x, y, x + w, y + h)                
                eye_aspect_ratio = self.landmarks.final_ear(gray_image, rect)
                lips_distance = self.landmarks.lip_distance(gray_image, rect)
                print(eye_aspect_ratio, lips_distance)

                if sleep and eye_aspect_ratio > self.eye_aspect_ratio_threshold:
                    self.sleeping_counter += 1
                    frame_counter = 0
                    sleep = False
                    # buzzer = threading.Thread(target=beep)
                    # buzzer.start()

                
                elif eye_aspect_ratio < self.eye_aspect_ratio_threshold:
                    print("closed eyes")
                    frame_counter += 1
                    if frame_counter >= self.closed_eyes_threshold_fps:
                        sleep = True


                if not sleep and lips_distance > self.yawn_threshold:
                    yawn = True
                    print("Yawning")
                elif yawn and lips_distance < self.yawn_threshold:
                    yawn = False
                    self.yawning_counter += 1
                    print(self.yawning_counter)











# def main(closed_eyes_seconds_threshold, FPS, eye_aspect_ratio_threshold, yawn_threshold, database_writes_frequency_seconds):
#     detector = FatigueDetector(closed_eyes_seconds_threshold, FPS, eye_aspect_ratio_threshold, yawn_threshold, database_writes_frequency_seconds)
#     detector.run()



# if __name__ == '__main__':
#     main(3, 24, 0.25, 10, 10)
