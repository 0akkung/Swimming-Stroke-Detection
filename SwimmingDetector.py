import cv2
import mediapipe as mp
import numpy as np
import time
import matplotlib.pyplot as plt


class SwimmingDetector:
    def __init__(self):
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose

        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

        self.results = None
        self.landmarks = None

        # Swimming Style
        self.style = "Unknown"

        # Angles variables
        self.left_angles = []
        self.right_angles = []

        # Stroke counter variables
        self.ready = False
        self.left_stroke = 0
        self.right_stroke = 0
        self.l_stage = None
        self.r_stage = None

        # Timer variable
        self.start_time = None
        self.end_time = None
        self.elapsed_time = None

    def get_strokes(self):
        strokes = self.left_stroke + self.right_stroke

        if self.style == "Freestyle" or self.style == "Backstroke":
            return strokes

        return strokes // 2

    def get_result(self):
        return self.results

    def calculate_angle(self, image, a, b, c):
        a = np.array(a)  # First
        b = np.array(b)  # Mid
        c = np.array(c)  # End

        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)

        if angle > 180.0:
            angle = 360 - angle

        # Visualize angle
        cv2.putText(image, str(int(angle)),
                    tuple(np.multiply(b, [640, 480]).astype(int)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (191, 64, 191), 2, cv2.LINE_AA
                    )

        return angle

    def get_landmark_value(self, part):
        # Get landmark of specified body part
        landmark_index = self.mp_pose.PoseLandmark[part].value

        if self.landmarks is None:
            return None

        return self.landmarks[landmark_index]

    def get_orientation(self):
        left_shoulder = self.get_landmark_value("LEFT_SHOULDER")
        right_shoulder = self.get_landmark_value("RIGHT_SHOULDER")
        left_hip = self.get_landmark_value("LEFT_HIP")
        right_hip = self.get_landmark_value("RIGHT_HIP")

        # Calculate the vectors between shoulders and hips
        shoulder_vector_x = right_shoulder.x - left_shoulder.x
        shoulder_vector_y = right_shoulder.y - left_shoulder.y
        hip_vector_x = right_hip.x - left_hip.x
        hip_vector_y = right_hip.y - left_hip.y

        # Calculate the dot product of shoulder and hip vectors
        dot_product = shoulder_vector_x * hip_vector_x + shoulder_vector_y * hip_vector_y

        # TODO: Fixing dot product bugs since most swimming do not stand straight

        # Determine the facing direction based on the dot product sign
        if shoulder_vector_x < 0:
            return "Forward"
        else:
            return "Backward"

    def set_ready(self):
        self.ready = True
        self.start_time = time.time()

    def process_frame(self, frame):
        # Recolor image to RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False

        # Make detection
        self.results = self.pose.process(image)

        # Recolor back to BGR
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Extract landmarks
        try:
            self.landmarks = self.results.pose_landmarks.landmark

            # Get orientation (forward or backward)
            orientation = self.get_orientation()

            # Get left arm coordinates
            left_hip = [self.get_landmark_value("LEFT_HIP").x, self.get_landmark_value("LEFT_HIP").y]
            left_shoulder = [self.get_landmark_value("LEFT_SHOULDER").x, self.get_landmark_value("LEFT_SHOULDER").y]
            left_elbow = [self.get_landmark_value("LEFT_ELBOW").x, self.get_landmark_value("LEFT_ELBOW").y]
            left_wrist = [self.get_landmark_value("LEFT_WRIST").x, self.get_landmark_value("LEFT_WRIST").y]

            # Get right arm coordinates
            right_hip = [self.get_landmark_value("RIGHT_HIP").x, self.get_landmark_value("RIGHT_HIP").y]
            right_shoulder = [self.get_landmark_value("RIGHT_SHOULDER").x, self.get_landmark_value("RIGHT_SHOULDER").y]
            right_elbow = [self.get_landmark_value("RIGHT_ELBOW").x, self.get_landmark_value("RIGHT_ELBOW").y]
            right_wrist = [self.get_landmark_value("RIGHT_WRIST").x, self.get_landmark_value("RIGHT_WRIST").y]

            # Calculate angles
            left_shoulder_angle = self.calculate_angle(image, left_hip, left_shoulder, left_elbow)
            right_shoulder_angle = self.calculate_angle(image, right_hip, right_shoulder, right_elbow)

            left_elbow_angle = self.calculate_angle(image, left_shoulder, left_elbow, left_wrist)
            right_elbow_angle = self.calculate_angle(image, right_shoulder, right_elbow, right_wrist)

            # Store angles in a list for plotting
            self.left_angles.append(left_shoulder_angle)
            self.right_angles.append(right_shoulder_angle)

            # Percentage of success of stroke
            left_per = np.interp(left_shoulder_angle, (30, 160), (0, 100))
            right_per = np.interp(right_shoulder_angle, (30, 160), (0, 100))

            # Bar to show stroke progress
            left_bar = np.interp(left_shoulder_angle, (30, 160), (380, 50))
            right_bar = np.interp(right_shoulder_angle, (30, 160), (380, 50))

            # Check to ensure right form before starting the program
            if left_shoulder_angle > 160 and right_shoulder_angle > 160 and not self.ready:
                self.set_ready()

            if self.ready:
                # Stroke counter logic
                if left_shoulder_angle < 30:
                    # Swimming style logic
                    if self.style == "Unknown":
                        if right_shoulder_angle < 70 and left_elbow_angle > 160:
                            self.style = "Butterfly"
                        elif right_shoulder_angle < 70:
                            self.style = "Breaststroke"
                        elif orientation == "Backward":
                            self.style = "Freestyle"
                        else:
                            self.style = "Backstroke"

                    self.l_stage = "down"

                elif left_shoulder_angle > 160 and self.l_stage == 'down':
                    self.l_stage = "up"
                    self.left_stroke += 1
                    print(f'{self.left_stroke} (Left)')

                if right_shoulder_angle < 30:
                    # Swimming style logic
                    if self.style == "Unknown":
                        if left_shoulder_angle < 70 and right_elbow_angle > 160:
                            self.style = "Butterfly"
                        elif left_shoulder_angle < 70:
                            self.style = "Breaststroke"
                        elif orientation == "Backward":
                            self.style = "Freestyle"
                        else:
                            self.style = "Backstroke"

                    self.r_stage = "down"
                elif right_shoulder_angle > 160 and self.r_stage == 'down':
                    self.r_stage = "up"
                    self.right_stroke += 1
                    print(f'{self.right_stroke} (Right)')

                cv2.rectangle(image, (480, 50), (500, 380), (255, 0, 0), 3)
                cv2.rectangle(image, (480, int(left_bar)), (500, 380), (255, 0, 0), cv2.FILLED)
                cv2.putText(image, f'{int(left_per)}%', (465, 430), cv2.FONT_HERSHEY_PLAIN, 2,
                            (255, 0, 0), 2)

                cv2.rectangle(image, (580, 50), (600, 380), (0, 102, 255), 3)
                cv2.rectangle(image, (580, int(right_bar)), (600, 380), (0, 102, 255), cv2.FILLED)
                cv2.putText(image, f'{int(right_per)}%', (565, 430), cv2.FONT_HERSHEY_PLAIN, 2,
                            (255, 0, 0), 2)

        except Exception as e:
            print(f"Error: {e}")

        # Render detections
        self.mp_drawing.draw_landmarks(image, self.results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS,
                                       self.mp_drawing.DrawingSpec(color=(102, 255, 255), thickness=2,
                                                                   circle_radius=2),
                                       self.mp_drawing.DrawingSpec(color=(240, 207, 137), thickness=2,
                                                                   circle_radius=2)
                                       )

        if self.ready:
            # Render stroke counter
            # Setup status box
            cv2.rectangle(image, (0, 0), (225, 100), (45, 45, 45), -1)

            # Stroke data
            cv2.putText(image, f'Stroke: {self.get_strokes()}', (10, 30),
                        cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2, cv2.LINE_AA)

            # Style data
            cv2.putText(image, str(self.style), (10, 70),
                        cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2, cv2.LINE_AA)

            # Show Timer
            self.end_time = time.time()
            self.elapsed_time = self.end_time - self.start_time

            cv2.rectangle(image, (0, 420), (120, 480), (0, 255, 0), -1)
            cv2.putText(image, f'{self.elapsed_time:.2f}', (10, 460), cv2.FONT_HERSHEY_PLAIN,
                        2, (255, 0, 0), 3)

        cv2.imshow('Stroke Counter', image)

        return image

    def plot_angles(self):
        # Plot the angles
        plt.figure(figsize=(8, 6))
        plt.plot(self.left_angles, label='Left Arm Angles')
        plt.plot(self.right_angles, label='Right Arm Angles')
        plt.xlabel('Frame Number')
        plt.ylabel('Angle (degrees)')
        plt.title('Angles of Left and Right Arms')
        plt.legend()
        plt.grid(True)
        plt.show()

    def count_strokes(self, src=0, w_cam=640, h_cam=480):
        # VIDEO FEED
        print("???")
        cap = cv2.VideoCapture(src)
        cap.set(3, w_cam)
        cap.set(4, h_cam)

        while cap.isOpened():
            ret, frame = cap.read()

            frame = self.process_frame(frame)

            # Convert the processed frame back to JPEG format for streaming
            # try:
            #     ret, buffer = cv2.imencode('.jpg', frame)
            #     frame = buffer.tobytes()
            #     yield (b'--frame\r\n'
            #            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            # except Exception as e:
            #     pass

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    def get_strokes_per_minute(self):
        return (self.get_strokes() / self.elapsed_time) * 60
