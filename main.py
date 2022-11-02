from scipy.spatial import distance as dist
from imutils.video import VideoStream
from imutils import face_utils
from threading import Thread
import numpy as np
import argparse
import imutils
import time
import dlib
import cv2
import threading
from playsound import playsound
from pynput import keyboard
from os.path import exists
from datetime import datetime


def eye_aspect_ratio(eye):  # calculates openness of an eye
    eye_height_line_1 = dist.euclidean(eye[1], eye[5])
    eye_height_line_2 = dist.euclidean(eye[2], eye[4])
    eye_width = dist.euclidean(eye[0], eye[3])
    ear = (eye_height_line_1 + eye_height_line_2) / (2.0 * eye_width)
    return ear


def final_ear(shape):
    (left_eye_start, left_eye_end) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]  # detects the eyes and applies above function
    (right_eye_start, right_eye_end) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
    left_eye = shape[left_eye_start:left_eye_end]
    right_eye = shape[right_eye_start:right_eye_end]
    left_ear = eye_aspect_ratio(left_eye)
    right_ear = eye_aspect_ratio(right_eye)
    ear = (left_ear + right_ear) / 2.0
    return ear, left_eye, right_eye


def lip_distance(shape):  # calculates openness of a mouth
    top_lip = np.concatenate((shape[50:53], shape[61:64]))
    low_lip = np.concatenate((shape[56:59], shape[65:68]))
    top_mean = np.mean(top_lip, axis=0)
    low_mean = np.mean(low_lip, axis=0)
    distance = abs(top_mean[1] - low_mean[1])
    return distance


def camera(frame, eye, gray, rect, predictor, ear):  # enables real-time view from camera
    shape = predictor(gray, rect)
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


def alarm(filepath):  # plays sound alarm
    playsound(filepath)


def on_press(key, abort_key='esc'):
    try:
        key = key.char
    except AttributeError:
        key = key.name
    if key == abort_key:
        return False


def save_to_file(filepath, data):
    if not filepath.endswith('.csv'):
        raise ValueError("File should be a csv file")
    file_exists = exists(filepath)
    with open(filepath, 'a+') as f:
        if not file_exists:
            f.write("date, from, to, yawns, eyes closed \n")
        f.write(data + "\n")


def get_args():  # gets arguments from command line flags
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--rounds", help="number of times program will run", type=int, default=3)
    parser.add_argument("-s", "--seconds", help="seconds for one cycle", type=int, default=30)
    parser.add_argument("-v", "--verbose", help="Verbose output", action="store_true")
    parser.add_argument("-a", "--audio", help="Audio output", action="store_true")
    parser.add_argument("-c", "--closed_eyes_seconds_threshold",
                        help="Time after which closed eyes are counted as sleeping", type=int, default=3)
    parser.add_argument("-f", "--FPS", help="Frames per second", type=int, default=24)
    parser.add_argument("-e", "--e_a_r", help="eye aspect ratio", type=float, default=0.2)
    parser.add_argument("-y", "--yawn_threshold", help="yawn threshold", type=float, default=20.0)
    parser.add_argument("-t", "--time_limit", help="if time limit is to be applied", action="store_false")
    parser.add_argument("-file", '--filepath', help="path to the file to write to")
    arguments = parser.parse_args()
    return arguments.__dict__


def fatigue_detector(seconds, verbose, audio, closed_eyes_seconds_threshold, FPS, e_a_r, yawn_threshold, time_limit,
                     filepath):  # main detecting function
    default_thread_number = threading.active_count()
    closed_eyes_threshold_fps = closed_eyes_seconds_threshold * FPS
    sleeping_counter, yawning_counter, frame_counter = 0, 0, 0
    detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
    vs = VideoStream(framerate=FPS).start()  # starts video
    time.sleep(1)
    yawn, sleep, multiple_threads = False, False, False
    starting_time = time.time()
    date = datetime.now().replace(microsecond=0)
    timeout = starting_time + seconds
    while True:
        frame = imutils.resize(vs.read(), width=450)
        to_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rects = detector.detectMultiScale(to_gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30),
                                          flags=cv2.CASCADE_SCALE_IMAGE)
        for (x, y, w, h) in rects:
            rect = dlib.rectangle(int(x), int(y), int(x + w), int(y + h))
            shape = face_utils.shape_to_np(predictor(to_gray, rect))
            eye = final_ear(shape)
            ear = eye[0]
            distance = lip_distance(shape)
            if sleep and ear > e_a_r:
                sleeping_counter += 1
                frame_counter = 0
                sleep = False
            elif ear < e_a_r:
                frame_counter += 1
                if frame_counter >= closed_eyes_threshold_fps:
                    if audio and threading.active_count() < default_thread_number + 2:
                        multiple_threads = True
                        new_thread = Thread(target=playsound, args=('hello_there.mp3',))
                        new_thread.start()
                    cv2.putText(frame, "WAKE UP!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    sleep = True
            if not sleep and distance > yawn_threshold:
                cv2.putText(frame, "FATIGUE ALERT", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                yawn = True
            elif yawn and distance < yawn_threshold:
                yawn = False
                yawning_counter += 1
            if verbose:
                camera(frame, eye, to_gray, rect, predictor, ear)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('z'):
            if multiple_threads:
                new_thread.join()
            cv2.destroyAllWindows()
            vs.stop()
            exit(0)
        if key == ord("q") or (time_limit and time.time() > timeout):
            if multiple_threads:
                new_thread.join()
            cv2.destroyAllWindows()
            vs.stop()
            if filepath is not None:
                to_write = f' {date.strftime("%m/%d/%Y")}, {date.strftime("%H:%M:%S")},' \
                           f' {datetime.now().replace(microsecond=0).strftime("%H:%M:%S")},' \
                           f' {yawning_counter}, {sleeping_counter} '
                save_to_file(filepath, to_write)
            print(f"In the last {round(time.time() - starting_time)} seconds you've yawned: {yawning_counter} "
                  f"times and had your eyes closed for longer than "
                  f"{closed_eyes_seconds_threshold} seconds {sleeping_counter} times")
            exit(0)


def main(args):
    for _ in range(args['rounds']):
        fatigue_detector(args['seconds'], args['verbose'], args['audio'], args['closed_eyes_seconds_threshold'],
                         args['FPS'], args['e_a_r'], args['yawn_threshold'], args['time_limit'], args['filepath'])


if __name__ == '__main__':
    cmd_args = get_args()
    if not cmd_args['verbose']:
        listener = keyboard.Listener(on_press=lambda event: on_press(event, abort_key='esc'))
        listener.start()
        Thread(target=main, args=(cmd_args,), name='main', daemon=True).start()
        listener.join()
    else:
        main(cmd_args)
