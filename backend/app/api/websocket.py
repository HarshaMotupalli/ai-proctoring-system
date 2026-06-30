# # # """
# # # Real-Time Proctoring WebSocket
# # # Advanced Production Version

# # # Features:
# # # - Face Detection (YOLO)
# # # - Head Turn Detection (MediaPipe normalized yaw)
# # # - Fast Partial Phone Detection
# # # - Temporal Verification
# # # - Multi-Level Warning System
# # # - Occurrence-Based Termination
# # # - Risk-Based Escalation
# # # """


# # ##------------------ OLDER CORRECT VERSION OF CODE ------------------


# from fastapi import APIRouter, WebSocket, WebSocketDisconnect
# import cv2
# import numpy as np
# import base64
# import os
# import time
# from collections import deque
# from uuid import uuid4
# from datetime import datetime

# from app.detection.face.face_embedding import FaceEmbedder
# from app.detection.face.face_cropper import FaceCropper
# from app.detection.headpose.headpose_estimator import HeadPoseEstimator
# from app.detection.object.object_detector import ObjectDetector

# from app.core.database import SessionLocal
# from app.models.session import ExamSession
# from app.models.violation import Violation

# router = APIRouter()

# # ---------------- MODELS ----------------
# cropper = FaceCropper()
# headpose = HeadPoseEstimator()
# object_detector = ObjectDetector()

# # ---------------- BUFFERS ----------------
# face_buffer = deque(maxlen=10)
# look_buffer = deque(maxlen=5)
# phone_buffer = deque(maxlen=5)

# TIME_THRESHOLD = 3  # seconds


# # ---------------- HELPER: LOG VIOLATION ----------------
# def log_violation(db, session_id, event_name, duration, evidence_path):
#     violation = Violation(
#         session_id=session_id,
#         type=event_name,
#         duration=duration,
#         timestamp=datetime.utcnow(),
#         evidence_path=evidence_path
#     )
#     db.add(violation)
#     db.commit()


# @router.websocket("/ws/proctor")
# async def websocket_proctor(websocket: WebSocket):

#     await websocket.accept()
#     print("WebSocket CONNECTED")

#     db = SessionLocal()

#     session_id = str(uuid4())

#     exam_session = ExamSession(
#         session_id=session_id,
#         user_id=1,
#         start_time=datetime.utcnow(),
#         final_status="ACTIVE",
#         termination_reason=None
#     )

#     db.add(exam_session)
#     db.commit()

#     # -------- SESSION-SPECIFIC EVIDENCE FOLDER --------
#     session_folder = None  # create only if needed

#     violation_memory = {
#         "looking_away": {"count": 0, "active": False, "start_time": None},
#         "no_face": {"count": 0, "active": False, "start_time": None},
#         "phone_detected": {"count": 0, "active": False, "start_time": None},
#         "multiple_faces": {"count": 0, "last_state": False},
#     }

#     combined_violation_count = 0

#     def update_event(event_name, is_active, frame):
#         nonlocal combined_violation_count, session_folder

#         now = time.time()
#         event = violation_memory[event_name]

#         if is_active:
#             if not event["active"]:
#                 event["active"] = True
#                 event["start_time"] = now
#         else:
#             if event["active"]:
#                 duration = now - event["start_time"]

#                 if duration >= TIME_THRESHOLD:
#                     event["count"] += 1
#                     combined_violation_count += 1

#                     # Create folder only when first violation confirmed
#                     if session_folder is None:
#                         session_folder = f"evidence/{session_id}"
#                         os.makedirs(session_folder, exist_ok=True)

#                     filename = f"{session_folder}/{event_name}_{datetime.utcnow().strftime('%H%M%S')}.jpg"
#                     cv2.imwrite(filename, frame)

#                     log_violation(
#                         db=db,
#                         session_id=session_id,
#                         event_name=event_name,
#                         duration=round(duration, 2),
#                         evidence_path=filename
#                     )

#                 event["active"] = False
#                 event["start_time"] = None

#     try:
#         while True:

#             data = await websocket.receive_text()

#             if "," in data:
#                 data = data.split(",")[1]

#             frame = cv2.imdecode(
#                 np.frombuffer(base64.b64decode(data), np.uint8),
#                 cv2.IMREAD_COLOR
#             )

#             if frame is None:
#                 continue

#             # -------- FACE DETECTION --------
#             results = cropper.model(frame, verbose=False)
#             face_count = sum(
#                 1 for r in results
#                 for box in r.boxes
#                 if float(box.conf[0]) > 0.6
#             )

#             face_buffer.append(face_count)
#             stable_face_count = max(set(face_buffer), key=face_buffer.count)

#             # -------- HEAD POSE --------
#             looking_direction = "CENTER"
#             looking_away = False

#             if stable_face_count == 1:
#                 yaw = headpose.estimate(frame)
#                 if yaw is not None:
#                     if yaw > 0.06:
#                         looking_away = True
#                         looking_direction = "RIGHT"
#                     elif yaw < -0.06:
#                         looking_away = True
#                         looking_direction = "LEFT"

#             look_buffer.append(looking_away)
#             stable_looking = sum(look_buffer) > 2

#             # -------- OBJECT DETECTION --------
#             detected_objects = object_detector.detect_objects(frame)
#             phone_detected = "cell phone" in detected_objects

#             phone_buffer.append(phone_detected)
#             stable_phone = sum(phone_buffer) > 2

#             # -------- MULTIPLE FACE OCCURRENCE --------
#             if stable_face_count > 1:
#                 if not violation_memory["multiple_faces"]["last_state"]:
#                     violation_memory["multiple_faces"]["count"] += 1
#                     violation_memory["multiple_faces"]["last_state"] = True

#                     log_violation(
#                         db=db,
#                         session_id=session_id,
#                         event_name="multiple_faces",
#                         duration=0,
#                         evidence_path=None
#                     )
#             else:
#                 violation_memory["multiple_faces"]["last_state"] = False

#             # -------- TIME EVENTS --------
#             update_event("looking_away", stable_looking, frame)
#             update_event("no_face", stable_face_count == 0, frame)
#             update_event("phone_detected", stable_phone, frame)

#             # -------- STATUS LOGIC --------
#             status = "SAFE"
#             reason = ""

#             if violation_memory["multiple_faces"]["count"] >= 3:
#                 status = "TERMINATE"
#                 reason = "Multiple Persons Detected"

#             elif combined_violation_count >= 4:
#                 status = "TERMINATE"
#                 reason = "Repeated Suspicious Behaviour"

#             elif combined_violation_count == 2:
#                 status = "SEVERE_WARNING"
#                 reason = "Repeated Suspicious Activity"

#             elif combined_violation_count == 1:
#                 status = "WARNING"
#                 reason = "Suspicious Activity Detected"

#             elif violation_memory["looking_away"]["active"]:
#                 status = "WARNING"
#                 reason = f"Looking {looking_direction}"

#             elif violation_memory["no_face"]["active"]:
#                 status = "WARNING"
#                 reason = "Face Not Detected"

#             elif violation_memory["phone_detected"]["active"]:
#                 status = "WARNING"
#                 reason = "Unauthorized Device Detected"

#             await websocket.send_json({
#                 "face_count": stable_face_count if stable_face_count > 0 else "No Face",
#                 "looking_direction": looking_direction,
#                 "multiple_person_occurrences": violation_memory["multiple_faces"]["count"],
#                 "detected_objects": detected_objects,
#                 "status": status,
#                 "reason": reason
#             })

#             # -------- TERMINATION --------
#             if status == "TERMINATE":

#                 exam_session.final_status = "TERMINATED"
#                 exam_session.termination_reason = reason
#                 exam_session.end_time = datetime.utcnow()
#                 db.commit()

#                 await websocket.close()
#                 break

#     except WebSocketDisconnect:

#         if exam_session.final_status == "ACTIVE":
#             if combined_violation_count == 0:
#                 exam_session.final_status = "COMPLETED_CLEAN"
#             else:
#                 exam_session.final_status = "COMPLETED_WITH_WARNINGS"

#             exam_session.end_time = datetime.utcnow()
#             db.commit()

#         db.close()
#         print("Client disconnected")












# --------------------------------CORRECT PREDICTION CODE ---------------------------------

# from fastapi import APIRouter, WebSocket, WebSocketDisconnect
# import cv2
# import numpy as np
# import base64
# import os
# import time
# from collections import deque
# from uuid import uuid4
# from datetime import datetime

# from app.detection.face.face_cropper import FaceCropper
# from app.detection.headpose.headpose_estimator import HeadPoseEstimator
# from app.detection.object.object_detector import ObjectDetector

# from app.core.database import SessionLocal
# from app.models.session import ExamSession
# from app.models.violation import Violation

# router = APIRouter()

# # ---------------- MODELS ----------------
# cropper = FaceCropper()
# headpose = HeadPoseEstimator()
# object_detector = ObjectDetector()

# # ---------------- BUFFERS ----------------
# face_buffer = deque(maxlen=10)
# look_buffer = deque(maxlen=5)
# phone_buffer = deque(maxlen=5)

# # 🔥 FRAME BUFFER (IMPORTANT)
# frame_buffer = deque(maxlen=50)

# TIME_THRESHOLD = 3  # seconds


# # ---------------- HELPER: LOG VIOLATION ----------------
# def log_violation(db, session_id, event_name, duration, evidence_path):
#     violation = Violation(
#         session_id=session_id,
#         type=event_name,
#         duration=duration,
#         timestamp=datetime.utcnow(),
#         evidence_path=evidence_path
#     )
#     db.add(violation)
#     db.commit()


# @router.websocket("/ws/proctor")
# async def websocket_proctor(websocket: WebSocket):

#     await websocket.accept()
#     print("WebSocket CONNECTED")

#     db = SessionLocal()

#     session_id = str(uuid4())

#     exam_session = ExamSession(
#         session_id=session_id,
#         user_id=1,
#         start_time=datetime.utcnow(),
#         final_status="ACTIVE",
#         termination_reason=None
#     )

#     db.add(exam_session)
#     db.commit()

#     session_folder = None

#     violation_memory = {
#         "looking_away": {"count": 0, "active": False, "start_time": None, "locked_frame": None},
#         "no_face": {"count": 0, "active": False, "start_time": None, "locked_frame": None},
#         "phone_detected": {"count": 0, "active": False, "start_time": None, "locked_frame": None},
#         "multiple_faces": {"count": 0, "last_state": False},
#     }

#     combined_violation_count = 0

#     # ---------------- UPDATED EVENT FUNCTION ----------------
#     def update_event(event_name, is_active):
#         nonlocal combined_violation_count, session_folder

#         now = time.time()
#         event = violation_memory[event_name]

#         if is_active:
#             if not event["active"]:
#                 # 🔥 EVENT START
#                 event["active"] = True
#                 event["start_time"] = now

#                 # 🔥 LOCK FRAME AT START
#                 event["locked_frame"] = frame_buffer[-1][1] if frame_buffer else None

#         else:
#             if event["active"]:
#                 duration = now - event["start_time"]

#                 if duration >= TIME_THRESHOLD:
#                     event["count"] += 1
#                     combined_violation_count += 1

#                     # Create folder
#                     if session_folder is None:
#                         session_folder = f"evidence/{session_id}"
#                         os.makedirs(session_folder, exist_ok=True)

#                     # 🔥 USE LOCKED FRAME
#                     frame_to_save = event.get("locked_frame") or frame

#                     filename = f"{session_folder}/{event_name}_{datetime.utcnow().strftime('%H%M%S')}.jpg"
#                     cv2.imwrite(filename, frame_to_save)

#                     log_violation(
#                         db=db,
#                         session_id=session_id,
#                         event_name=event_name,
#                         duration=round(duration, 2),
#                         evidence_path=filename
#                     )

#                 # RESET
#                 event["active"] = False
#                 event["start_time"] = None
#                 event["locked_frame"] = None

#     try:
#         while True:

#             data = await websocket.receive_text()

#             if "," in data:
#                 data = data.split(",")[1]

#             frame = cv2.imdecode(
#                 np.frombuffer(base64.b64decode(data), np.uint8),
#                 cv2.IMREAD_COLOR
#             )

#             if frame is None:
#                 continue

#             # 🔥 ADD FRAME TO BUFFER
#             frame_buffer.append((time.time(), frame.copy()))

#             # -------- FACE DETECTION --------
#             results = cropper.model(frame, verbose=False)
#             face_count = sum(
#                 1 for r in results
#                 for box in r.boxes
#                 if float(box.conf[0]) > 0.6
#             )

#             face_buffer.append(face_count)
#             stable_face_count = max(set(face_buffer), key=face_buffer.count)

#             # -------- HEAD POSE --------
#             looking_direction = "CENTER"
#             looking_away = False

#             if stable_face_count == 1:
#                 yaw = headpose.estimate(frame)
#                 if yaw is not None:
#                     if yaw > 0.06:
#                         looking_away = True
#                         looking_direction = "RIGHT"
#                     elif yaw < -0.06:
#                         looking_away = True
#                         looking_direction = "LEFT"

#             look_buffer.append(looking_away)
#             stable_looking = sum(look_buffer) > 2

#             # -------- OBJECT DETECTION --------
#             detected_objects = object_detector.detect_objects(frame)
#             phone_detected = "cell phone" in detected_objects

#             phone_buffer.append(phone_detected)
#             stable_phone = sum(phone_buffer) > 2

#             # -------- MULTIPLE FACE --------
#             if stable_face_count > 1:
#                 if not violation_memory["multiple_faces"]["last_state"]:
#                     violation_memory["multiple_faces"]["count"] += 1
#                     violation_memory["multiple_faces"]["last_state"] = True

#                     if session_folder is None:
#                         session_folder = f"evidence/{session_id}"
#                         os.makedirs(session_folder, exist_ok=True)

#                     frame_to_save = frame_buffer[-1][1] if frame_buffer else frame

#                     filename = f"{session_folder}/multiple_faces_{datetime.utcnow().strftime('%H%M%S')}.jpg"
#                     cv2.imwrite(filename, frame_to_save)

#                     log_violation(
#                         db=db,
#                         session_id=session_id,
#                         event_name="multiple_faces",
#                         duration=0,
#                         evidence_path=filename
#                     )
#             else:
#                 violation_memory["multiple_faces"]["last_state"] = False

#             # -------- TEMPORAL EVENTS --------
#             update_event("looking_away", stable_looking)
#             update_event("no_face", stable_face_count == 0)
#             update_event("phone_detected", stable_phone)

#             # -------- STATUS --------
#             status = "SAFE"
#             reason = ""

#             if violation_memory["multiple_faces"]["count"] >= 3:
#                 status = "TERMINATE"
#                 reason = "Multiple Persons Detected"

#             elif combined_violation_count >= 4:
#                 status = "TERMINATE"
#                 reason = "Repeated Suspicious Behaviour"

#             elif combined_violation_count == 2:
#                 status = "SEVERE_WARNING"
#                 reason = "Repeated Suspicious Activity"

#             elif combined_violation_count == 1:
#                 status = "WARNING"
#                 reason = "Suspicious Activity Detected"

#             elif violation_memory["looking_away"]["active"]:
#                 status = "WARNING"
#                 reason = f"Looking {looking_direction}"

#             elif violation_memory["no_face"]["active"]:
#                 status = "WARNING"
#                 reason = "Face Not Detected"

#             elif violation_memory["phone_detected"]["active"]:
#                 status = "WARNING"
#                 reason = "Unauthorized Device Detected"

#             await websocket.send_json({
#                 "face_count": stable_face_count if stable_face_count > 0 else "No Face",
#                 "looking_direction": looking_direction,
#                 "multiple_person_occurrences": violation_memory["multiple_faces"]["count"],
#                 "detected_objects": detected_objects,
#                 "status": status,
#                 "reason": reason
#             })

#             # -------- TERMINATE --------
#             if status == "TERMINATE":
#                 exam_session.final_status = "TERMINATED"
#                 exam_session.termination_reason = reason
#                 exam_session.end_time = datetime.utcnow()
#                 db.commit()

#                 await websocket.close()
#                 break

#     except WebSocketDisconnect:

#         if exam_session.final_status == "ACTIVE":
#             if combined_violation_count == 0:
#                 exam_session.final_status = "COMPLETED_CLEAN"
#             else:
#                 exam_session.final_status = "COMPLETED_WITH_WARNINGS"

#             exam_session.end_time = datetime.utcnow()
#             db.commit()

#         db.close()
#         print("Client disconnected")










# from fastapi import APIRouter, WebSocket, WebSocketDisconnect
# import cv2
# import numpy as np
# import base64
# import os
# import time
# from collections import deque
# from uuid import uuid4
# from datetime import datetime

# from app.detection.face.face_cropper import FaceCropper
# from app.detection.headpose.headpose_estimator import HeadPoseEstimator
# from app.detection.object.object_detector import ObjectDetector

# from app.core.database import SessionLocal
# from app.models.session import ExamSession
# from app.models.violation import Violation

# router = APIRouter()

# # ---------------- MODELS ----------------
# cropper = FaceCropper()
# headpose = HeadPoseEstimator()
# object_detector = ObjectDetector()

# # ---------------- BUFFERS ----------------
# face_buffer = deque(maxlen=10)
# look_buffer = deque(maxlen=5)
# phone_buffer = deque(maxlen=5)
# frame_buffer = deque(maxlen=50)

# TIME_THRESHOLD = 3


# # ---------------- LOG ----------------
# def log_violation(db, session_id, event_name, duration, evidence_path):
#     violation = Violation(
#         session_id=session_id,
#         type=event_name,
#         duration=duration,
#         timestamp=datetime.utcnow(),
#         evidence_path=evidence_path
#     )
#     db.add(violation)
#     db.commit()


# @router.websocket("/ws/proctor")
# async def websocket_proctor(websocket: WebSocket):

#     await websocket.accept()
#     print("✅ WebSocket CONNECTED")

#     db = SessionLocal()

#     session_id = str(uuid4())

#     exam_session = ExamSession(
#         session_id=session_id,
#         user_id=1,
#         start_time=datetime.utcnow(),
#         final_status="ACTIVE",
#         termination_reason=None
#     )

#     db.add(exam_session)
#     db.commit()

#     session_folder = None

#     violation_memory = {
#         "looking_away": {"count": 0, "active": False, "start_time": None, "locked_frame": None},
#         "no_face": {"count": 0, "active": False, "start_time": None, "locked_frame": None},
#         "phone_detected": {"count": 0, "active": False, "start_time": None, "locked_frame": None},
#         "multiple_faces": {"count": 0, "last_state": False},
#     }

#     combined_violation_count = 0

#     # ---------------- TEMPORAL LOGIC (UNCHANGED) ----------------
#     def update_event(event_name, is_active):
#         nonlocal combined_violation_count, session_folder

#         now = time.time()
#         event = violation_memory[event_name]

#         if is_active:
#             if not event["active"]:
#                 event["active"] = True
#                 event["start_time"] = now
#                 event["locked_frame"] = frame_buffer[-1][1] if frame_buffer else None

#         else:
#             if event["active"]:
#                 duration = now - event["start_time"]

#                 if duration >= TIME_THRESHOLD:
#                     event["count"] += 1
#                     combined_violation_count += 1

#                     if session_folder is None:
#                         session_folder = f"evidence/{session_id}"
#                         os.makedirs(session_folder, exist_ok=True)

#                     frame_to_save = event.get("locked_frame") or frame

#                     filename = f"{session_folder}/{event_name}_{datetime.utcnow().strftime('%H%M%S')}.jpg"
#                     cv2.imwrite(filename, frame_to_save)

#                     log_violation(
#                         db=db,
#                         session_id=session_id,
#                         event_name=event_name,
#                         duration=round(duration, 2),
#                         evidence_path=filename
#                     )

#                 event["active"] = False
#                 event["start_time"] = None
#                 event["locked_frame"] = None

#     try:
#         while True:

#             data = await websocket.receive_text()

#             if "," in data:
#                 data = data.split(",")[1]

#             frame = cv2.imdecode(
#                 np.frombuffer(base64.b64decode(data), np.uint8),
#                 cv2.IMREAD_COLOR
#             )

#             if frame is None:
#                 continue

#             frame_buffer.append((time.time(), frame.copy()))

#             # -------- FACE --------
#             results = cropper.model(frame, verbose=False)

#             face_count = sum(
#                 1 for r in results
#                 for box in r.boxes
#                 if float(box.conf[0]) > 0.6
#             )

#             face_buffer.append(face_count)
#             stable_face_count = max(set(face_buffer), key=face_buffer.count) if face_buffer else 0

#             # -------- HEADPOSE --------
#             looking_direction = "CENTER"
#             looking_away = False

#             if stable_face_count == 1:
#                 yaw = headpose.estimate(frame)
#                 if yaw is not None:
#                     if yaw > 0.06:
#                         looking_away = True
#                         looking_direction = "RIGHT"
#                     elif yaw < -0.06:
#                         looking_away = True
#                         looking_direction = "LEFT"

#             look_buffer.append(looking_away)
#             stable_looking = sum(look_buffer) > 2

#             # -------- OBJECT --------
#             detected_objects = object_detector.detect_objects(frame) or []
#             phone_detected = "cell phone" in detected_objects

#             phone_buffer.append(phone_detected)
#             stable_phone = sum(phone_buffer) > 2

#             # -------- MULTIPLE FACE --------
#             if stable_face_count > 1:
#                 if not violation_memory["multiple_faces"]["last_state"]:
#                     violation_memory["multiple_faces"]["count"] += 1
#                     violation_memory["multiple_faces"]["last_state"] = True

#                     if session_folder is None:
#                         session_folder = f"evidence/{session_id}"
#                         os.makedirs(session_folder, exist_ok=True)

#                     frame_to_save = frame_buffer[-1][1] if frame_buffer else frame

#                     filename = f"{session_folder}/multiple_faces_{datetime.utcnow().strftime('%H%M%S')}.jpg"
#                     cv2.imwrite(filename, frame_to_save)

#                     log_violation(
#                         db=db,
#                         session_id=session_id,
#                         event_name="multiple_faces",
#                         duration=0,
#                         evidence_path=filename
#                     )
#             else:
#                 violation_memory["multiple_faces"]["last_state"] = False

#             # -------- TEMPORAL EVENTS --------
#             update_event("looking_away", stable_looking)
#             update_event("no_face", stable_face_count == 0)
#             update_event("phone_detected", stable_phone)

#             # -------- STATUS (UNCHANGED LOGIC) --------
#             status = "SAFE"
#             reason = ""

#             if violation_memory["multiple_faces"]["count"] >= 3:
#                 status = "TERMINATE"
#                 reason = "Multiple Persons Detected"

#             elif combined_violation_count >= 4:
#                 status = "TERMINATE"
#                 reason = "Repeated Suspicious Behaviour"

#             elif combined_violation_count == 2:
#                 status = "SEVERE_WARNING"
#                 reason = "Repeated Suspicious Activity"

#             elif combined_violation_count == 1:
#                 status = "WARNING"
#                 reason = "Suspicious Activity Detected"

#             elif violation_memory["looking_away"]["active"]:
#                 status = "WARNING"
#                 reason = f"Looking {looking_direction}"

#             elif violation_memory["no_face"]["active"]:
#                 status = "WARNING"
#                 reason = "Face Not Detected"

#             elif violation_memory["phone_detected"]["active"]:
#                 status = "WARNING"
#                 reason = "Unauthorized Device Detected"

#             # 🔥 FIXED RESPONSE FORMAT
#             await websocket.send_json({
#                 "face_count": int(stable_face_count),
#                 "looking_direction": looking_direction,
#                 "multiple_person_occurrences": int(violation_memory["multiple_faces"]["count"]),
#                 "detected_objects": detected_objects,
#                 "status": status,
#                 "reason": reason
#             })

#             # -------- TERMINATE --------
#             if status == "TERMINATE":
#                 exam_session.final_status = "TERMINATED"
#                 exam_session.termination_reason = reason
#                 exam_session.end_time = datetime.utcnow()
#                 db.commit()

#                 await websocket.close()
#                 break

#     except WebSocketDisconnect:

#         if exam_session.final_status == "ACTIVE":
#             if combined_violation_count == 0:
#                 exam_session.final_status = "COMPLETED_CLEAN"
#             else:
#                 exam_session.final_status = "COMPLETED_WITH_WARNINGS"

#             exam_session.end_time = datetime.utcnow()
#             db.commit()

#         db.close()
#         print("Client disconnected")











from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import cv2
import numpy as np
import base64
import os
import time
from collections import deque
from uuid import uuid4
from datetime import datetime

from app.detection.face.face_cropper import FaceCropper
from app.detection.headpose.headpose_estimator import HeadPoseEstimator
from app.detection.object.object_detector import ObjectDetector

from app.core.database import SessionLocal
from app.models.session import ExamSession
from app.models.violation import Violation
from app.models.exam_log import ExamLog


router = APIRouter()

# ---------------- MODELS ----------------
cropper = FaceCropper()
headpose = HeadPoseEstimator()
object_detector = ObjectDetector()

# ---------------- BUFFERS ----------------
face_buffer = deque(maxlen=5)   # 🔥 reduced (faster)
look_buffer = deque(maxlen=5)
phone_buffer = deque(maxlen=5)
frame_buffer = deque(maxlen=30)

TIME_THRESHOLD = 3


# ---------------- LOG ----------------
# def log_violation(db, session_id, event_name, duration, evidence_path):
#     violation = Violation(
#         session_id=session_id,
#         type=event_name,
#         duration=duration,
#         timestamp=datetime.utcnow(),
#         evidence_path=evidence_path
#     )
#     db.add(violation)
#     db.commit()

from app.models.exam_log import ExamLog

def log_violation(db, session_id, event_name, duration, evidence_path):

    # EXISTING VIOLATION TABLE
    violation = Violation(
        session_id=session_id,
        type=event_name,
        duration=duration,
        timestamp=datetime.utcnow(),
        evidence_path=evidence_path
    )
    db.add(violation)

    # 🔥 NEW EXAM LOG ENTRY
    log = ExamLog(
        user_id=1,
        session_id=session_id,
        status="VIOLATION",
        violation_type=event_name
    )

    db.add(log)
    db.commit()



@router.websocket("/ws/proctor")
async def websocket_proctor(websocket: WebSocket):

    await websocket.accept()
    print("✅ WebSocket CONNECTED")

    db = SessionLocal()

    session_id = str(uuid4())

    exam_session = ExamSession(
        session_id=session_id,
        user_id=1,
        start_time=datetime.utcnow(),
        final_status="ACTIVE"
    )

    db.add(exam_session)
    db.commit()

    session_folder = None

    violation_memory = {
        "looking_away": {"count": 0, "active": False, "start_time": None, "locked_frame": None},
        "no_face": {"count": 0, "active": False, "start_time": None, "locked_frame": None},
        "phone_detected": {"count": 0, "active": False, "start_time": None, "locked_frame": None},
        "multiple_faces": {"count": 0, "last_state": False},
    }

    combined_violation_count = 0

    # ---------------- TEMPORAL LOGIC (UNCHANGED) ----------------
    def update_event(event_name, is_active):
        nonlocal combined_violation_count, session_folder

        now = time.time()
        event = violation_memory[event_name]

        if is_active:
            if not event["active"]:
                event["active"] = True
                event["start_time"] = now
                event["locked_frame"] = frame_buffer[-1][1] if frame_buffer else None

        else:
            if event["active"]:
                duration = now - event["start_time"]

                if duration >= TIME_THRESHOLD:
                    event["count"] += 1
                    combined_violation_count += 1

                    if session_folder is None:
                        session_folder = f"evidence/{session_id}"
                        os.makedirs(session_folder, exist_ok=True)

                    # frame_to_save = event.get("locked_frame") or frame
                    locked_frame = event.get("locked_frame")

                    if locked_frame is not None:
                        frame_to_save = locked_frame
                    else:
                        frame_to_save = frame

                    filename = f"{session_folder}/{event_name}_{datetime.utcnow().strftime('%H%M%S')}.jpg"
                    cv2.imwrite(filename, frame_to_save)

                    log_violation(db, session_id, event_name, round(duration, 2), filename)

                event["active"] = False
                event["start_time"] = None
                event["locked_frame"] = None

    try:
        while True:

            data = await websocket.receive_text()

            if "," in data:
                data = data.split(",")[1]

            frame = cv2.imdecode(
                np.frombuffer(base64.b64decode(data), np.uint8),
                cv2.IMREAD_COLOR
            )

            if frame is None:
                continue

            frame_buffer.append((time.time(), frame.copy()))

            # ---------------- FACE DETECTION (FIXED) ----------------
            results = cropper.model(frame, verbose=False)

            raw_face_count = sum(
                1 for r in results
                for box in r.boxes
                if float(box.conf[0]) > 0.5   # 🔥 relaxed threshold
            )

            face_buffer.append(raw_face_count)

            # 🔥 FAST RESPONSE (use latest if 0)
            if raw_face_count == 0:
                stable_face_count = 0
            else:
                stable_face_count = max(set(face_buffer), key=face_buffer.count)

            # ---------------- HEADPOSE ----------------
            looking_direction = "CENTER"
            looking_away = False

            if stable_face_count == 1:
                yaw = headpose.estimate(frame)
                if yaw is not None:
                    if yaw > 0.05:
                        looking_direction = "RIGHT"
                        looking_away = True
                    elif yaw < -0.05:
                        looking_direction = "LEFT"
                        looking_away = True

            look_buffer.append(looking_away)
            stable_looking = sum(look_buffer) > 2

            # ---------------- OBJECT DETECTION (FIXED) ----------------
            detected_objects = object_detector.detect_objects(frame) or []

            # 🔥 CLEAN LABELS
            detected_objects = [obj.lower() for obj in detected_objects]

            phone_detected = any(obj in ["cell phone", "phone", "mobile"] for obj in detected_objects)

            phone_buffer.append(phone_detected)
            stable_phone = sum(phone_buffer) > 2

            # ---------------- MULTIPLE FACE ----------------
            if stable_face_count > 1:
                if not violation_memory["multiple_faces"]["last_state"]:
                    violation_memory["multiple_faces"]["count"] += 1
                    violation_memory["multiple_faces"]["last_state"] = True

                    if session_folder is None:
                        session_folder = f"evidence/{session_id}"
                        os.makedirs(session_folder, exist_ok=True)

                    filename = f"{session_folder}/multiple_faces_{datetime.utcnow().strftime('%H%M%S')}.jpg"
                    cv2.imwrite(filename, frame)

                    log_violation(db, session_id, "multiple_faces", 0, filename)
            else:
                violation_memory["multiple_faces"]["last_state"] = False

            # ---------------- TEMPORAL EVENTS ----------------
            update_event("looking_away", stable_looking)
            update_event("no_face", stable_face_count == 0)
            update_event("phone_detected", stable_phone)

            # ---------------- STATUS ----------------
            status = "SAFE"
            reason = ""

            if violation_memory["multiple_faces"]["count"] >= 3:
                status = "TERMINATE"
                reason = "Multiple Persons Detected"

            elif combined_violation_count >= 4:
                status = "TERMINATE"
                reason = "Repeated Suspicious Behaviour"

            elif combined_violation_count == 2:
                status = "SEVERE_WARNING"
                reason = "Repeated Suspicious Activity"

            elif combined_violation_count == 1:
                status = "WARNING"
                reason = "Suspicious Activity Detected"

            elif stable_face_count == 0:
                status = "WARNING"
                reason = "Face Not Detected"

            elif stable_face_count > 1:
                status = "WARNING"
                reason = "Multiple Faces Detected"

            elif stable_phone:
                status = "WARNING"
                reason = "Phone Detected"

            elif stable_looking:
                status = "WARNING"
                reason = f"Looking {looking_direction}"

            # ---------------- RESPONSE ----------------
            await websocket.send_json({
                "face_count": int(stable_face_count),
                "looking_direction": looking_direction,
                "multiple_person_occurrences": int(stable_face_count),
                "detected_objects": detected_objects,
                "status": status,
                "reason": reason
            })

            # ---------------- TERMINATION ----------------
            if status == "TERMINATE":
                exam_session.final_status = "TERMINATED"
                exam_session.termination_reason = reason
                exam_session.end_time = datetime.utcnow()
                db.commit()

                await websocket.close()
                break

    except WebSocketDisconnect:

        if exam_session.final_status == "ACTIVE":
            if combined_violation_count == 0:
                exam_session.final_status = "COMPLETED_CLEAN"
            else:
                exam_session.final_status = "COMPLETED_WITH_WARNINGS"

            exam_session.end_time = datetime.utcnow()
            db.commit()

        db.close()
        print("Client disconnected")
