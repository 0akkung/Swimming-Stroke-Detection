import cv2
import mediapipe as mp
import numpy as np
import time
from SwimmingDetector import SwimmingDetector

w_cam, h_cam = 640, 480

# VIDEO FEED
cap = cv2.VideoCapture(0)
# cap = cv2.VideoCapture('videos/freestyle.mp4')
cap.set(3, w_cam)
cap.set(4, h_cam)

# FPS variable
prev_time = 0

# Timer variable
start_time = time.time()

# Swimming Detector
detector = SwimmingDetector()

while cap.isOpened():
    ret, frame = cap.read()

    image = detector.find_pose(frame)

    results = detector.get_result()

    detector.find_stroke(image)

    # Render curl counter
    # Setup status box
    cv2.rectangle(image, (0, 0), (225, 73), (45, 45, 45), -1)

    # Stroke data
    cv2.putText(image, f'Stroke: {detector.get_stroke()}', (10, 60),
                cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2, cv2.LINE_AA)

    # Show FPS
    cur_time = time.time()  # current time
    fps = 1 / (cur_time - prev_time)
    cv2.putText(image, f'FPS: {int(fps)}', (400, 70), cv2.FONT_HERSHEY_PLAIN,
                3, (255, 0, 0), 3)
    prev_time = cur_time  # previous time

    # Show Timer
    elapsed_time = cur_time - start_time
    cv2.putText(image, f'Time Elapsed: {elapsed_time:.2f}', (10, 430), cv2.FONT_HERSHEY_PLAIN,
                2, (255, 128, 0), 3)

    cv2.imshow('Mediapipe Feed', image)

    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
