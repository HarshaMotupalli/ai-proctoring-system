# -------------- corrected and optimized version with better error handling, margin, and debug logs --------------

# from fastapi import APIRouter, UploadFile, File, Form
# import cv2
# import numpy as np
# import mediapipe as mp

# from app.core.database import SessionLocal
# from app.models.user import User
# from app.detection.face.face_embedding import FaceEmbedder

# router = APIRouter()

# # 🔹 Face Detector
# mp_face = mp.solutions.face_detection
# face_detector = mp_face.FaceDetection(
#     model_selection=1,
#     min_detection_confidence=0.6  # 🔥 slightly higher for stability
# )

# embedder = FaceEmbedder()

# @router.post("/verify")
# async def verify_face(
#     image: UploadFile = File(...),
#     user_id: int = Form(...)
# ):
#     db = SessionLocal()

#     try:
#         # ---------------- READ IMAGE ---------------- #
#         contents = await image.read()
#         if not contents:
#             return {"face_detected": False, "identity": False}

#         npimg = np.frombuffer(contents, np.uint8)
#         frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

#         if frame is None:
#             return {"face_detected": False, "identity": False}

#         h, w, _ = frame.shape

#         # ---------------- FACE DETECTION ---------------- #
#         rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         results = face_detector.process(rgb)

#         if not results.detections:
#             return {"face_detected": False, "identity": False}

#         # 🔥 MULTIPLE FACE CHECK (important for cheating detection)
#         if len(results.detections) > 1:
#             print("Multiple faces detected!")
#             return {"face_detected": True, "identity": False}

#         # ---------------- FACE CROP ---------------- #
#         bbox = results.detections[0].location_data.relative_bounding_box

#         # 🔥 ADD MARGIN (VERY IMPORTANT FOR ACCURACY)
#         margin = 0.2

#         x1 = int((bbox.xmin - margin) * w)
#         y1 = int((bbox.ymin - margin) * h)
#         x2 = int((bbox.xmin + bbox.width + margin) * w)
#         y2 = int((bbox.ymin + bbox.height + margin) * h)

#         # Clamp values
#         x1 = max(0, x1)
#         y1 = max(0, y1)
#         x2 = min(w, x2)
#         y2 = min(h, y2)

#         face_crop = frame[y1:y2, x1:x2]

#         if face_crop.size == 0:
#             return {"face_detected": False, "identity": False}

#         # 🔥 RESIZE (ArcFace standard)
#         face_crop = cv2.resize(face_crop, (112, 112))

#         # ---------------- USER FETCH ---------------- #
#         user = db.query(User).filter(User.id == user_id).first()

#         if user is None:
#             print("User not found!")
#             return {"face_detected": True, "identity": False}

#         # ---------------- EMBEDDINGS ---------------- #
#         embedding_live = embedder.get_embedding(face_crop)

#         if embedding_live is None:
#             return {"face_detected": True, "identity": False}

#         stored_embedding = np.frombuffer(user.embedding, dtype=np.float32)

#         # 🔥 SAFE NORMALIZATION
#         def normalize(v):
#             norm = np.linalg.norm(v)
#             return v if norm == 0 else v / norm

#         embedding_live = normalize(embedding_live)
#         stored_embedding = normalize(stored_embedding)

#         # ---------------- SIMILARITY ---------------- #
#         similarity = float(np.dot(embedding_live, stored_embedding))

#         print("----------- VERIFY DEBUG -----------")
#         print("User ID:", user_id)
#         print("Similarity:", similarity)
#         print("Frame shape:", frame.shape)

#         # 🔥 FINAL THRESHOLD (TUNED)
#         THRESHOLD = 0.6
#         identity_match = similarity > THRESHOLD

#         return {
#             "face_detected": True,
#             "identity": bool(identity_match),
#             "similarity": similarity
#         }

#     except Exception as e:
#         print("VERIFY ERROR:", str(e))
#         return {"face_detected": False, "identity": False}

#     finally:
#         db.close()






import csv
import os
from fastapi import APIRouter, UploadFile, File, Form
import cv2
import numpy as np
import mediapipe as mp

from app.core.database import SessionLocal
from app.models.user import User
from app.detection.face.face_embedding import FaceEmbedder


#----------------csv logging setup----------------#
CSV_FILE = "evaluation_results.csv"

# Create file with header if not exists
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["user_id", "similarity", "prediction", "actual"])

# 🔥 GLOBAL MATCH MEMORY (for stability)
match_history = []

router = APIRouter()

# 🔹 Face Detector
mp_face = mp.solutions.face_detection
face_detector = mp_face.FaceDetection(
    model_selection=1,
    min_detection_confidence=0.6
)

embedder = FaceEmbedder()


@router.post("/verify")
async def verify_face(
    image: UploadFile = File(...),
    user_id: int = Form(...)
):
    db = SessionLocal()

    try:
        # ---------------- READ IMAGE ---------------- #
        contents = await image.read()
        if not contents:
            return {"face_detected": False, "identity": False}

        npimg = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

        if frame is None:
            return {"face_detected": False, "identity": False}

        h, w, _ = frame.shape

        # ---------------- FACE DETECTION ---------------- #
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_detector.process(rgb)

        if not results.detections:
            return {"face_detected": False, "identity": False}

        # 🔥 MULTIPLE FACE CHECK
        if len(results.detections) > 1:
            return {"face_detected": True, "identity": False}

        # ---------------- FACE CROP ---------------- #
        bbox = results.detections[0].location_data.relative_bounding_box
        margin = 0.2

        x1 = max(0, int((bbox.xmin - margin) * w))
        y1 = max(0, int((bbox.ymin - margin) * h))
        x2 = min(w, int((bbox.xmin + bbox.width + margin) * w))
        y2 = min(h, int((bbox.ymin + bbox.height + margin) * h))

        face_crop = frame[y1:y2, x1:x2]

        if face_crop.size == 0:
            return {"face_detected": False, "identity": False}

        # 🔥 Resize (ArcFace standard)
        face_crop = cv2.resize(face_crop, (112, 112))

        # ---------------- USER ---------------- #
        user = db.query(User).filter(User.id == user_id).first()

        if user is None:
            return {"face_detected": True, "identity": False}

        # ---------------- EMBEDDINGS ---------------- #
        embedding_live = embedder.get_embedding(face_crop)

        if embedding_live is None:
            return {"face_detected": True, "identity": False}

        stored_embedding = np.frombuffer(user.embedding, dtype=np.float32)

        # 🔥 SAFE NORMALIZATION
        def normalize(v):
            norm = np.linalg.norm(v)
            if norm == 0:
                return v
            return v / norm

        embedding_live = normalize(embedding_live)
        stored_embedding = normalize(stored_embedding)

        # ---------------- METRICS ---------------- #
        cosine_sim = float(np.dot(embedding_live, stored_embedding))
        euclidean_dist = float(np.linalg.norm(embedding_live - stored_embedding))

        print("----------- VERIFY DEBUG -----------")
        print("Cosine:", cosine_sim)
        print("Distance:", euclidean_dist)

        # FINAL STRICT DECISION (UPDATED)
        identity_match = False

        if cosine_sim > 0.80 and euclidean_dist < 0.65:
            identity_match = True
        
        # TEMPORAL STABILITY CHECK
        match_history.append(identity_match)

        if len(match_history) > 5:
            match_history.pop(0)

        final_match = match_history.count(True) >= 4 # At least 4 out of last 5 should match

        # Prediction from model
        prediction = int(final_match)

        # Ground truth (manual for now)
        actual = -1   # later change manually (1 = same, 0 = different)

        # Save data (⚡ limit logging to avoid huge file)
        if cosine_sim > 0.3:
            with open(CSV_FILE, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    user_id,
                    float(cosine_sim),
                    prediction,
                    actual
                ])

        # ---------------- RETURN RESPONSE ---------------- #
        return {
            "face_detected": True,
            "identity": bool(final_match),
            "similarity": cosine_sim,
            "distance": euclidean_dist
        }

    except Exception as e:
        print("VERIFY ERROR:", str(e))
        return {"face_detected": False, "identity": False}

    finally:
        db.close()





# from fastapi import APIRouter, UploadFile, File
# import cv2
# import numpy as np
# import mediapipe as mp
# from fastapi import Form

# from app.core.database import SessionLocal
# from app.models.user import User
# from app.detection.face.face_embedding import FaceEmbedder
# from app.models.user import User

# router = APIRouter()

# mp_face = mp.solutions.face_detection
# face_detector = mp_face.FaceDetection(
#     model_selection=1,
#     min_detection_confidence=0.3
# )

# embedder = FaceEmbedder()


# @router.post("/verify")
# async def verify_face(
#     image: UploadFile = File(...),
#     user_id: int = Form(...)
# ):
#     db = SessionLocal()

#     try:
#         # 🔹 Read image
#         contents = await image.read()
#         if not contents:
#             return {"face_detected": False, "identity": False}

#         npimg = np.frombuffer(contents, np.uint8)
#         frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

#         if frame is None:
#             return {"face_detected": False, "identity": False}

#         # 🔹 Detect face
#         rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         results = face_detector.process(rgb)

#         if not results.detections:
#             return {"face_detected": False, "identity": False}

#         # 🔹 Get user safely
#         user = db.query(User).filter(User.id == user_id).first()

#         if user is None:
#             print("User not found!")
#             return {"face_detected": True, "identity": False}

#         # 🔹 Generate embedding
#         embedding_live = embedder.get_embedding(frame)

#         if embedding_live is None:
#             return {"face_detected": True, "identity": False}

#         # 🔹 Load stored embedding
#         stored_embedding = np.frombuffer(user.embedding, dtype=np.float32)

#         # 🔹 Cosine similarity
#         similarity = np.dot(embedding_live, stored_embedding) / (
#             np.linalg.norm(embedding_live) * np.linalg.norm(stored_embedding)
#         )

#         print("User ID:", user_id)
#         print("User exists:", user is not None)
#         print("Embedding live:", embedding_live is not None)
#         print("Stored embedding shape:", stored_embedding.shape)
#         print("Similarity:", similarity)
#         print("Frame shape:", frame.shape)

#         # 🔥 TEMP LOW THRESHOLD (FOR TESTING)
#         identity_match = similarity > 0.3

#         return {
#             "face_detected": bool(True),
#             "identity": bool(identity_match),   
#             "similarity": float(similarity)
#         }

#     except Exception as e:
#         print("VERIFY ERROR:", str(e))
#         return {"face_detected": False, "identity": False}

#     finally:
#         db.close()




