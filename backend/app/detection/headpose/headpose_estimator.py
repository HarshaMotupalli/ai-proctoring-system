# # """
# # Head Pose Estimator using MediaPipe Face Mesh
# # """
# ## --------------------- corrected version of headpose_estimator ---------------------- ##

import cv2
import numpy as np
import mediapipe as mp

class HeadPoseEstimator:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6
        )

    def estimate(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb)

        if not results.multi_face_landmarks:
            return None

        landmarks = results.multi_face_landmarks[0]
        h, w, _ = frame.shape

        nose = landmarks.landmark[1]
        left_eye = landmarks.landmark[33]
        right_eye = landmarks.landmark[263]

        nose_x = nose.x
        left_eye_x = left_eye.x
        right_eye_x = right_eye.x

        eye_center = (left_eye_x + right_eye_x) / 2

        # NORMALIZED YAW (-1 to +1)
        yaw_normalized = nose_x - eye_center

        return yaw_normalized





###-----------------------------------------------------------------###


# import cv2
# import numpy as np
# import mediapipe as mp


# class HeadPoseEstimator:

#     def __init__(self):

#         self.mp_face_mesh = mp.solutions.face_mesh

#         self.face_mesh = self.mp_face_mesh.FaceMesh(
#             static_image_mode=False,
#             max_num_faces=1,
#             refine_landmarks=True,
#             min_detection_confidence=0.6,
#             min_tracking_confidence=0.6
#         )

#     def estimate(self, frame):

#         img_h, img_w = frame.shape[:2]

#         rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         results = self.face_mesh.process(rgb)

#         if not results.multi_face_landmarks:
#             return None, None

#         face_landmarks = results.multi_face_landmarks[0]

#         # key landmarks for pose
#         points = []

#         ids = [1, 33, 263, 61, 291, 199]

#         for idx in ids:
#             lm = face_landmarks.landmark[idx]
#             x = int(lm.x * img_w)
#             y = int(lm.y * img_h)
#             points.append([x, y])

#         points = np.array(points, dtype=np.float64)

#         # 3D face model points
#         model_points = np.array([
#             (0.0, 0.0, 0.0),         # nose
#             (-30.0, -30.0, -30.0),   # left eye
#             (30.0, -30.0, -30.0),    # right eye
#             (-40.0, 30.0, -30.0),    # left mouth
#             (40.0, 30.0, -30.0),     # right mouth
#             (0.0, 70.0, -50.0)       # chin
#         ])

#         focal_length = img_w
#         cam_matrix = np.array(
#             [[focal_length, 0, img_w / 2],
#              [0, focal_length, img_h / 2],
#              [0, 0, 1]],
#             dtype="double"
#         )

#         dist_matrix = np.zeros((4, 1), dtype=np.float64)

#         success, rotation_vec, translation_vec = cv2.solvePnP(
#             model_points,
#             points,
#             cam_matrix,
#             dist_matrix
#         )

#         if not success:
#             return None, None

#         rmat, _ = cv2.Rodrigues(rotation_vec)

#         angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)

#         pitch = angles[0] * 360
#         yaw = angles[1] * 360

#         return yaw, pitch
    
    

# backend/app/detection/headpose/headpose_estimator.py

# import cv2
# import numpy as np
# import math


# class HeadPoseEstimator:
#     def __init__(self):
#         self.model_points = np.array([
#             (0.0, 0.0, 0.0),           # Nose tip
#             (0.0, -330.0, -65.0),      # Chin
#             (-225.0, 170.0, -135.0),   # Left eye left corner
#             (225.0, 170.0, -135.0),    # Right eye right corner
#             (-150.0, -150.0, -125.0),  # Left Mouth corner
#             (150.0, -150.0, -125.0)    # Right mouth corner
#         ], dtype=np.float64)

#     def estimate(self, frame, landmarks):
#         h, w, _ = frame.shape

#         def get_point(idx):
#             lm = landmarks[idx]
#             return (int(lm.x * w), int(lm.y * h))

#         image_points = np.array([
#             get_point(1),     # Nose tip
#             get_point(152),   # Chin
#             get_point(33),    # Left eye corner
#             get_point(263),   # Right eye corner
#             get_point(61),    # Left mouth
#             get_point(291)    # Right mouth
#         ], dtype=np.float64)

#         focal_length = w
#         center = (w / 2, h / 2)
#         camera_matrix = np.array([
#             [focal_length, 0, center[0]],
#             [0, focal_length, center[1]],
#             [0, 0, 1]
#         ], dtype="double")

#         dist_coeffs = np.zeros((4, 1))

#         success, rotation_vector, translation_vector = cv2.solvePnP(
#             self.model_points,
#             image_points,
#             camera_matrix,
#             dist_coeffs,
#             flags=cv2.SOLVEPNP_ITERATIVE
#         )

#         rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
#         pose_matrix = cv2.hconcat((rotation_matrix, translation_vector))
#         _, _, _, _, _, _, euler_angles = cv2.decomposeProjectionMatrix(pose_matrix)

#         pitch = float(euler_angles[0])
#         yaw = float(euler_angles[1])
#         roll = float(euler_angles[2])

#         direction = "CENTER"

#         if yaw > 30:
#             direction = "RIGHT"
#         elif yaw < -30:
#             direction = "LEFT"
#         elif pitch > 20:
#             direction = "DOWN"
#         elif pitch < -20:
#             direction = "UP"

#         return {
#             "yaw": round(yaw, 2),
#             "pitch": round(pitch, 2),
#             "roll": round(roll, 2),
#             "direction": direction
#         }