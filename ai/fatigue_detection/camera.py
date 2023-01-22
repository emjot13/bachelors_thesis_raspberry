class Camera:

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