import cv2
import dlib
import numpy as np
import math
import csv


def eye_tracker(file):
    threshold, left_gaze, right_gaze, down_gaze = 0, 0, 0, 0
    gaze_direction = {}
    with open('eye_track_configuration.csv', 'r', encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        for row in reader:
            gaze_direction[row[0]] = gaze_direction.get(row[0], int(row[1]))

    cap = cv2.VideoCapture(file)
    font = cv2.FONT_HERSHEY_SIMPLEX

    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

    def midpoint(p1, p2):
        return int((p1.x + p2.x)/2), int((p1.y + p2.y)/2)

    def get_distance(points, face_landmark):
        point1 = midpoint(face_landmark.part(
            points[1]), face_landmark.part(points[2]))
        point2 = midpoint(face_landmark.part(
            points[4]), face_landmark.part(points[5]))
        dist = math.sqrt((point2[0] - point1[0]) **
                         2 + (point2[1] - point1[1])**2)
        return int(dist)

    def get_blinking_ratio(eye_points, facial_landmarks):
        left_point = (facial_landmarks.part(
            eye_points[0]).x, facial_landmarks.part(eye_points[0]).y)
        right_point = (facial_landmarks.part(
            eye_points[3]).x, facial_landmarks.part(eye_points[3]).y)
        center_top = midpoint(facial_landmarks.part(
            eye_points[1]), facial_landmarks.part(eye_points[2]))
        center_bottom = midpoint(facial_landmarks.part(
            eye_points[5]), facial_landmarks.part(eye_points[4]))
        hor_line_lenght = math.hypot(
            (left_point[0] - right_point[0]), (left_point[1] - right_point[1]))
        ver_line_lenght = math.hypot(
            (center_top[0] - center_bottom[0]), (center_top[1] - center_bottom[1]))
        ratio = hor_line_lenght / ver_line_lenght
        return ratio

    def get_gaze_ratio(eye_points, facial_landmarks):
        eye_region = np.array([(facial_landmarks.part(eye_points[0]).x, facial_landmarks.part(eye_points[0]).y),
                               (facial_landmarks.part(
                                eye_points[1]).x, facial_landmarks.part(eye_points[1]).y),
                               (facial_landmarks.part(
                                   eye_points[2]).x, facial_landmarks.part(eye_points[2]).y),
                               (facial_landmarks.part(
                                   eye_points[3]).x, facial_landmarks.part(eye_points[3]).y),
                               (facial_landmarks.part(
                                   eye_points[4]).x, facial_landmarks.part(eye_points[4]).y),
                               (facial_landmarks.part(eye_points[5]).x, facial_landmarks.part(eye_points[5]).y)], np.int32)

        height, width, _ = frame.shape
        mask = np.zeros((height, width), np.uint8)
        cv2.polylines(mask, [eye_region], True, 255, 2)
        cv2.fillPoly(mask, [eye_region], 255)
        eye = cv2.bitwise_and(gray, gray, mask=mask)

        min_x = np.min(eye_region[:, 0])
        max_x = np.max(eye_region[:, 0])
        min_y = np.min(eye_region[:, 1])
        max_y = np.max(eye_region[:, 1])

        gray_eye = eye[min_y: max_y, min_x: max_x]
        _, threshold_eye = cv2.threshold(gray_eye, 70, 255, cv2.THRESH_BINARY)
        height, width = threshold_eye.shape
        left_side_threshold = threshold_eye[0: height, 0: int(width / 2)]
        left_side_white = cv2.countNonZero(left_side_threshold)

        right_side_threshold = threshold_eye[0: height, int(width / 2): width]
        right_side_white = cv2.countNonZero(right_side_threshold)

        if left_side_white == 0:
            gaze_ratio = 1
        elif right_side_white == 0:
            gaze_ratio = 1.5
        else:
            gaze_ratio = left_side_white / right_side_white
        return gaze_ratio

    while True:
        ret, frame = cap.read()

        if ret == False:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)

        for face in faces:
            landmarks = predictor(gray, face)

            # eye blinking
            left_eye_ratio = get_blinking_ratio(
                [36, 37, 38, 39, 40, 41], landmarks)
            right_eye_ratio = get_blinking_ratio(
                [42, 43, 44, 45, 46, 47], landmarks)
            blinking_ratio = (left_eye_ratio + right_eye_ratio) / 2

            distance_left = get_distance([36, 37, 38, 39, 40, 41], landmarks)
            distance_right = get_distance([42, 43, 44, 45, 46, 47], landmarks)
            distance = int((distance_left + distance_right) / 2)

            if blinking_ratio > 5.5 or distance < 6:
                down_gaze += 1
                cv2.putText(frame, "BLINKING", (50, 150),
                            font, 1, (0, 0, 255), 3)

            # Gaze detection
            gaze_ratio_left_eye = get_gaze_ratio(
                [36, 37, 38, 39, 40, 41], landmarks)
            gaze_ratio_right_eye = get_gaze_ratio(
                [42, 43, 44, 45, 46, 47], landmarks)
            gaze_ratio = (gaze_ratio_right_eye + gaze_ratio_left_eye) / 2

            if gaze_ratio <= 0.5:
                right_gaze += 1
                cv2.putText(frame, "RIGHT", (50, 100), font, 2, (0, 0, 255), 3)
            elif 0.5 < gaze_ratio < 1.2:
                left_gaze += 1
                cv2.putText(frame, "LEFT", (50, 100), font, 2, (0, 0, 255), 3)
            else:
                cv2.putText(frame, "CENTER", (50, 100),
                            font, 2, (0, 0, 255), 3)

        cv2.imshow("Frame", frame)

        key = cv2.waitKey(1)
        if key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

    def classify_cheating():
        left_gaze_points = left_gaze * gaze_direction['left_gaze']
        right_gaze_points = right_gaze * gaze_direction['right_gaze']
        down_gaze_points = down_gaze * gaze_direction['down_gaze']
        cheat_points = left_gaze_points + right_gaze_points + down_gaze_points

        if cheat_points > gaze_direction['Threshold']:
            return True
        else:
            return False

    cheat = classify_cheating()
    print(cheat)
