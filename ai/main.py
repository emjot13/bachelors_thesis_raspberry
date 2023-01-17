from imutils.video import VideoStream
import time
import cv2
import threading
from os.path import exists
from os import remove
# import final_project.database.client as database
import database.client as database
# from landmarks import Landmarks



from scipy.spatial import distance as dist
import cv2
import dlib
import numpy as np
from imutils import face_utils




class Landmarks:


    def __init__(self):
        self.DETECTOR = cv2.CascadeClassifier("/home/pi/final_project/ai/resources/haarcascade_frontalface_default.xml") 
        self.PREDICTOR = dlib.shape_predictor("/home/pi/final_project/ai/resources/shape_predictor_68_face_landmarks.dat") 



    def get_rects(self, gray_image):  
        return self.DETECTOR.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)



    @staticmethod
    def eye_aspect_ratio(eye):  # calculates openness of an eye
        eye_height_line_1 = dist.euclidean(eye[1], eye[5])
        eye_height_line_2 = dist.euclidean(eye[2], eye[4])
        eye_width = dist.euclidean(eye[0], eye[3])
        ear = (eye_height_line_1 + eye_height_line_2) / (2.0 * eye_width)
        return ear

    def final_ear(self, gray_image, rect):
        rect = dlib.rectangle(*rect)

        shape = face_utils.shape_to_np(self.PREDICTOR(gray_image, rect))
        (left_eye_start, left_eye_end) = face_utils.FACIAL_LANDMARKS_IDXS[
            "left_eye"]  # detects the eyes and applies above function
        (right_eye_start, right_eye_end) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
        left_eye = shape[left_eye_start:left_eye_end]
        right_eye = shape[right_eye_start:right_eye_end]
        left_ear =  Landmarks.eye_aspect_ratio(left_eye)
        right_ear = Landmarks.eye_aspect_ratio(right_eye)
        ear = (left_ear + right_ear) / 2.0
        return ear

    def lip_distance(self, gray_image, rect):  # calculates openness of a mouth
        rect = dlib.rectangle(*rect)
        shape = face_utils.shape_to_np(self.PREDICTOR(gray_image, rect))
        top_lip = np.concatenate((shape[50:53], shape[61:64]))
        low_lip = np.concatenate((shape[56:59], shape[65:68]))
        top_mean = np.mean(top_lip, axis=0)
        low_mean = np.mean(low_lip, axis=0)
        distance = abs(top_mean[1] - low_mean[1])
        return distance









class FatigueDetector:

    def __init__(self, closed_eyes_seconds_threshold, FPS, eye_aspect_ratio_threshold, yawn_threshold, database_writes_frequency_seconds):
        self.eye_aspect_ratio_threshold = eye_aspect_ratio_threshold 
        self.yawn_threshold = yawn_threshold
        self.database_writes_frequency_seconds = database_writes_frequency_seconds
        self.FPS = FPS
        
        self.closed_eyes_threshold_fps = FPS * closed_eyes_seconds_threshold
        self.landmarks = Landmarks()
        self.yawning_counter, self.sleeping_counter = 0, 0
        self.database_writer = threading.Thread(target=self.write_to_database_every_x_seconds)


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
                    print(self.sleeping_counter)
                    frame_counter = 0
                    sleep = False
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
