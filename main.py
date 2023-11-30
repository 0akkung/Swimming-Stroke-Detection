import cv2
import mediapipe as mp
import numpy as np
import time

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


def calculate_angle(a, b, c):
    a = np.array(a)  # First
    b = np.array(b)  # Mid
    c = np.array(c)  # End

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle


w_cam, h_cam = 640, 480

# VIDEO FEED
cap = cv2.VideoCapture(0)
# cap = cv2.VideoCapture('videos/freestyle.mp4')
cap.set(3, w_cam)
cap.set(4, h_cam)

# Stroke counter variables
counter = 0
l_stage = None
r_stage = None

# FPS variable
prev_time = 0

# Timer variable
start_time = time.time()

# Setup mediapipe instance
with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        ret, frame = cap.read()

        # Recolor image to RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False

        # Make detection
        results = pose.process(image)

        # Recolor back to BGR
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Extract landmarks
        try:
            landmarks = results.pose_landmarks.landmark

            # Get left arm coordinates
            l_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                     landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
            l_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                          landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            l_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                       landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]

            # Get right arm coordinates
            r_hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                     landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
            r_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                          landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
            r_elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                       landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]

            # Calculate angles
            l_angle = calculate_angle(l_hip, l_shoulder, l_elbow)
            r_angle = calculate_angle(r_hip, r_shoulder, r_elbow)

            # Visualize angle
            cv2.putText(image, str(int(l_angle)),
                        tuple(np.multiply(l_shoulder, [640, 480]).astype(int)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
                        )
            cv2.putText(image, str(int(r_angle)),
                        tuple(np.multiply(r_shoulder, [640, 480]).astype(int)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
                        )

            # Stroke counter logic
            if l_angle < 30:
                l_stage = "down"
            elif l_angle > 160 and l_stage == 'down':
                l_stage = "up"
                counter += 1
                print(f'{counter} (Left)')

            if r_angle < 30:
                r_stage = "down"
            elif r_angle > 160 and r_stage == 'down':
                r_stage = "up"
                counter += 1
                print(f'{counter} (Right)')

        except:
            pass

        # Render curl counter
        # Setup status box
        cv2.rectangle(image, (0, 0), (225, 73), (45, 45, 45), -1)

        # Stroke data
        cv2.putText(image, f'Stroke: {counter}', (10, 60),
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2, cv2.LINE_AA)

        # Render detections
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                  mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                                  mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
                                  )
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
