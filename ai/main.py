from scipy.spatial import distance as dist
from imutils.video import VideoStream
from imutils import face_utils
import numpy as np
import argparse
import imutils
import time
import dlib
import cv2
import threading
from os.path import exists
from datetime import datetime
from os import remove
import database.client as database
import threading


class FatigueDetector:

    def __init__(self):
        self.DETECTOR = cv2.CascadeClassifier("/home/pi/final_project/ai/haarcascade_frontalface_default.xml") 
        self.PREDICTOR = dlib.shape_predictor("/home/pi/final_project/ai/shape_predictor_68_face_landmarks.dat") 
        self.yawning_counter, self.sleeping_counter = 0, 0


    def write_to_database_every_x_seconds(self, seconds):
        while True:
            time.sleep(seconds)
            database.insert_data(self.yawning_counter, self.sleeping_counter)


    @staticmethod
    def eye_aspect_ratio(eye):  # calculates openness of an eye
        eye_height_line_1 = dist.euclidean(eye[1], eye[5])
        eye_height_line_2 = dist.euclidean(eye[2], eye[4])
        eye_width = dist.euclidean(eye[0], eye[3])
        ear = (eye_height_line_1 + eye_height_line_2) / (2.0 * eye_width)
        return ear

    @staticmethod
    def final_ear(shape):
        (left_eye_start, left_eye_end) = face_utils.FACIAL_LANDMARKS_IDXS[
            "left_eye"]  # detects the eyes and applies above function
        (right_eye_start, right_eye_end) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
        left_eye = shape[left_eye_start:left_eye_end]
        right_eye = shape[right_eye_start:right_eye_end]
        left_ear =  FatigueDetector.eye_aspect_ratio(left_eye)
        right_ear = FatigueDetector.eye_aspect_ratio(right_eye)
        ear = (left_ear + right_ear) / 2.0
        return ear, left_eye, right_eye

    @staticmethod
    def lip_distance(shape):  # calculates openness of a mouth
        top_lip = np.concatenate((shape[50:53], shape[61:64]))
        low_lip = np.concatenate((shape[56:59], shape[65:68]))
        top_mean = np.mean(top_lip, axis=0)
        low_mean = np.mean(low_lip, axis=0)
        distance = abs(top_mean[1] - low_mean[1])
        return distance


    def camera(self, frame, eye, gray, rect, ear):  # enables real-time view from camera
        shape = self.PREDICTOR(gray, rect)
        shape = face_utils.shape_to_np(shape)
        distance = lip_distance(shape)
        left_eye = eye[1]
        right_eye = eye[2]
        left_eye_convex_hull = cv2.convexHull(left_eye)
        right_eye_convex_hull = cv2.convexHull(right_eye)
        cv2.drawContours(frame, [left_eye_convex_hull], -1, (0, 255, 0), 1)
        cv2.drawContours(frame, [right_eye_convex_hull], -1, (0, 255, 0), 1)
        lip = shape[48:60]
        cv2.drawContours(frame, [lip], -1, (0, 255, 0), 1)
        cv2.putText(frame, "EAR: {:.2f}".format(ear), (300, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(frame, "YAWN: {:.2f}".format(distance), (300, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 100, 255), 2)
        cv2.imshow("Fatigue detector", frame)



    @staticmethod
    def save_to_file(filepath, data):
        if not filepath.endswith('.csv'):
            raise ValueError("File should be a csv file")
        file_exists = exists(filepath)
        with open(filepath, 'a+') as f:
            if not file_exists:
                f.write("date, from, to, yawns, eyes closed \n")
            f.write(data + "\n")



    def fatigue_detector(self, seconds, verbose, audio, closed_eyes_seconds_threshold, FPS, e_a_r, yawn_threshold, time_limit,
                        filepath):  # main detecting function

        print("started fatique analysis")
        default_thread_number = threading.active_count()
        closed_eyes_threshold_fps = closed_eyes_seconds_threshold * FPS
        frame_counter = 0
        vs = VideoStream(framerate=FPS).start()  # starts video
        time.sleep(1)
        yawn, sleep, multiple_threads = False, False, False
        starting_time = time.time()
        date = datetime.now().replace(microsecond=0)
        timeout = starting_time + seconds
        database_writer = threading.Thread(target=self.write_to_database_every_x_seconds, args=(10,))
        database_writer.start()
        # database_writer = RepeatedTimer(10, database.insert_one, {"yawning": yawn, "sleeping": sleep})

        while True:
            if FatigueDetector.check_logical_files():
                vs.stop()
                database_writer.join()

                break
            frame = imutils.resize(vs.read(), width=450)
            to_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rects = self.DETECTOR.detectMultiScale(to_gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)
            for (x, y, w, h) in rects:
                rect = dlib.rectangle(int(x), int(y), int(x + w), int(y + h))
                shape = face_utils.shape_to_np(self.PREDICTOR(to_gray, rect))
                eye = FatigueDetector.final_ear(shape)
                ear = eye[0]
                distance = FatigueDetector.lip_distance(shape)
                if sleep and ear > e_a_r:
                    self.sleeping_counter += 1
                    print(self.sleeping_counter)
                    frame_counter = 0
                    sleep = False
                elif ear < e_a_r:
                    print("closed eyes")
                    frame_counter += 1
                    if frame_counter >= closed_eyes_threshold_fps:
                        sleep = True
                if not sleep and distance > yawn_threshold:
                    yawn = True
                    print("Yawning")
                elif yawn and distance < yawn_threshold:
                    yawn = False
                    self.yawning_counter += 1
                    print(self.yawning_counter)
                if verbose:
                    self.camera(frame, eye, to_gray, rect, self.PREDICTOR, ear)
                if filepath is not None:
                    to_write = f' {date.strftime("%m/%d/%Y")}, {date.strftime("%H:%M:%S")},' \
                            f' {datetime.now().replace(microsecond=0).strftime("%H:%M:%S")},' \
                            f' {yawning_counter}, {sleeping_counter} '
                    FatigueDetector.save_to_file(filepath, to_write)
                # print(f"In the last {round(time.time() - starting_time)} seconds you've yawned: {yawning_counter} "
                #       f"times and had your eyes closed for longer than "
                #       f"{closed_eyes_seconds_threshold} seconds {sleeping_counter} times")


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


    def run(args):
        fatigue_detector(args['seconds'], args['verbose'], args['audio'], args['closed_eyes_seconds_threshold'],
                            args['FPS'], args['e_a_r'], args['yawn_threshold'], args['time_limit'], args['filepath'])


    def run_no_cmd(self):
        self.fatigue_detector(30, False, False, 3, 24, 0.2, 10, False, None)


    def start(self):
        self.run_no_cmd()




def main():
    detector = FatigueDetector()
    detector.start()



if __name__ == '__main__':
    main()
