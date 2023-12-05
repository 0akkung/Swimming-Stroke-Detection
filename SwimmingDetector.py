import cv2
import mediapipe as mp
import numpy as np
import time


class SwimmingDetector:
    def __init__(self):
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose

        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

        self.results = None

        # Stroke counter variables
        self.stroke = 0
        self.l_stage = None
        self.r_stage = None

    def get_stroke(self):
        return self.stroke

    def get_result(self):
        return self.results

    def calculate_angle(self, a, b, c):
        a = np.array(a)  # First
        b = np.array(b)  # Mid
        c = np.array(c)  # End

        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)

        if angle > 180.0:
            angle = 360 - angle

        return angle

    def find_pose(self, img):
        # Recolor image to RGB
        image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False

        # Make detection
        self.results = self.pose.process(image)

        # Recolor back to BGR
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Render detections
        self.mp_drawing.draw_landmarks(image, self.results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS,
                                       self.mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                                       self.mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
                                       )

        return image

    def find_stroke(self, img):
        # Extract landmarks
        try:
            landmarks = self.results.pose_landmarks.landmark

            # Get left arm coordinates
            l_hip = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,
                     landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y]
            l_shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                          landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            l_elbow = [landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                       landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].y]

            # Get right arm coordinates
            r_hip = [landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                     landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].y]
            r_shoulder = [landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                          landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
            r_elbow = [landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                       landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]

            # Calculate angles
            l_angle = self.calculate_angle(l_hip, l_shoulder, l_elbow)
            r_angle = self.calculate_angle(r_hip, r_shoulder, r_elbow)

            # Visualize angle
            cv2.putText(img, str(int(l_angle)),
                        tuple(np.multiply(l_shoulder, [640, 480]).astype(int)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
                        )
            cv2.putText(img, str(int(r_angle)),
                        tuple(np.multiply(r_shoulder, [640, 480]).astype(int)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
                        )

            # Stroke counter logic
            if l_angle < 30:
                self.l_stage = "down"
            elif l_angle > 160 and self.l_stage == 'down':
                self.l_stage = "up"
                self.stroke += 1
                print(f'{self.stroke} (Left)')

            if r_angle < 30:
                self.r_stage = "down"
            elif r_angle > 160 and self.r_stage == 'down':
                self.r_stage = "up"
                self.stroke += 1
                print(f'{self.stroke} (Right)')

        except:
            pass