
from scipy.spatial import distance as dist
import cv2
import dlib
import numpy as np
from imutils import face_utils


CASCADE_CLASIFIER_PATH = "/home/pi/final_project/ai/resources/haarcascade_frontalface_default.xml"
SHAPE_PREDICTOR_PATH = "/home/pi/final_project/ai/resources/shape_predictor_68_face_landmarks.dat"


class Landmarks:

    def __init__(self):
        self.DETECTOR = cv2.CascadeClassifier(CASCADE_CLASIFIER_PATH) 
        self.PREDICTOR = dlib.shape_predictor(SHAPE_PREDICTOR_PATH) 


    def get_rects(self, gray_image):  
        return self.DETECTOR.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)


    @staticmethod
    def one_eye_aspect_ratio(eye):  # calculates openness of an eye
        eye_height_line_1 = dist.euclidean(eye[1], eye[5])
        eye_height_line_2 = dist.euclidean(eye[2], eye[4])
        eye_width = dist.euclidean(eye[0], eye[3])
        one_eye_aspect_ratio = (eye_height_line_1 + eye_height_line_2) / (2.0 * eye_width)
        return one_eye_aspect_ratio

    def eyes_aspect_ratio(self, gray_image, rect):
        rect = dlib.rectangle(*rect)

        shape = face_utils.shape_to_np(self.PREDICTOR(gray_image, rect))

        (left_eye_start, left_eye_end) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]  # detects the eyes and applies above function
        (right_eye_start, right_eye_end) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

        left_eye = shape[left_eye_start:left_eye_end]
        right_eye = shape[right_eye_start:right_eye_end]
        left_eye_aspect_ratio =  Landmarks.one_eye_aspect_ratio(left_eye)
        right_eye_aspect_ratio = Landmarks.one_eye_aspect_ratio(right_eye)
        total_eye_aspect_ratio = (left_eye_aspect_ratio + right_eye_aspect_ratio) / 2.0
        return total_eye_aspect_ratio

    def lip_distance(self, gray_image, rect):  # calculates openness of a mouth
        rect = dlib.rectangle(*rect)
        shape = face_utils.shape_to_np(self.PREDICTOR(gray_image, rect))
        top_lip = np.concatenate((shape[50:53], shape[61:64]))
        low_lip = np.concatenate((shape[56:59], shape[65:68]))
        top_lip_mean = np.mean(top_lip, axis=0)
        low_lip_mean = np.mean(low_lip, axis=0)
        distance = abs(top_lip_mean[1] - low_lip_mean[1])
        return distance