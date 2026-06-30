# from fastapi import APIRouter, UploadFile, File, Form, HTTPException
# import cv2
# import numpy as np
# import traceback

# from app.detection.face.face_embedding import FaceEmbedder
# from app.core.database import SessionLocal
# from app.models.user import User

# router = APIRouter()
# embedder = FaceEmbedder()

# @router.post("/register")
# async def register_user(
#     name: str = Form(...),
#     reg_no: str = Form(...),
#     college: str = Form(...),
#     image: UploadFile = File(...)
# ):
#     db = SessionLocal()

#     try:
#         # VALIDATION
#         if not name.strip() or not reg_no.strip() or not college.strip():
#             raise HTTPException(status_code=400, detail="All fields required")

#         existing_user = db.query(User).filter(User.reg_no == reg_no).first()
#         if existing_user:
#             raise HTTPException(status_code=400, detail="User already registered")

#         contents = await image.read()
#         if not contents:
#             raise HTTPException(status_code=400, detail="Image missing")

#         npimg = np.frombuffer(contents, np.uint8)
#         frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

#         if frame is None:
#             raise HTTPException(status_code=400, detail="Invalid image")

#         embedding = embedder.get_embedding(frame)
#         if embedding is None:
#             raise HTTPException(status_code=400, detail="Face not detected")

#         # 🔥 USER CREATION (INSIDE TRY)
#         user = User(
#             name=name.strip(),
#             reg_no=reg_no.strip(),
#             college=college.strip(),
#             embedding=embedding.tobytes()
#         )

#         db.add(user)
#         db.commit()
#         db.refresh(user)

#         # 🔥 RETURN MUST BE INSIDE TRY
#         return {
#             "message": "User registered successfully",
#             "user_id": user.id
#         }

#     except HTTPException as e:
#         db.rollback()
#         raise e

#     except Exception as e:
#         db.rollback()
#         print("REGISTER ERROR:", str(e))
#         raise HTTPException(status_code=500, detail=str(e))

#     finally:
#         db.close()


# # ---------------- GET ALL USERS (DEBUG / DASHBOARD) ---------------- #
# @router.get("/users")
# def get_users():
#     db = SessionLocal()

#     try:
#         users = db.query(User).all()

#         return [
#             {
#                 "id": u.id,
#                 "name": u.name,
#                 "reg_no": u.reg_no,
#                 "college": u.college
#             }
#             for u in users
#         ]

#     except Exception as e:
#         print("FETCH USERS ERROR:", str(e))
#         return []

#     finally:
#         db.close()





from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import cv2
import numpy as np
import mediapipe as mp
import time

from app.detection.face.face_embedding import FaceEmbedder
from app.core.database import SessionLocal
from app.models.user import User

router = APIRouter()
embedder = FaceEmbedder()

# 🔹 Face Detector
mp_face = mp.solutions.face_detection
face_detector = mp_face.FaceDetection(
    model_selection=1,
    min_detection_confidence=0.6
)


@router.post("/register")
async def register_user(
    name: str = Form(...),
    reg_no: str = Form(...),
    college: str = Form(...),
    image: UploadFile = File(...)
):
    db = SessionLocal()

    try:
        # ---------------- VALIDATION ---------------- #
        name = name.strip()
        reg_no = reg_no.strip()
        college = college.strip()

        if not name or not reg_no or not college:
            raise HTTPException(status_code=400, detail="All fields required")

        existing_user = db.query(User).filter(User.reg_no == reg_no).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="User already registered")

        # ---------------- READ IMAGE ---------------- #
        contents = await image.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Image missing")

        npimg = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image")

        h, w, _ = frame.shape

        # ---------------- FACE DETECTION ---------------- #
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_detector.process(rgb)

        if not results.detections:
            raise HTTPException(status_code=400, detail="Face not detected")

        # 🔥 FIRST FACE
        bbox = results.detections[0].location_data.relative_bounding_box

        margin = 0.2

        x1 = max(0, int((bbox.xmin - margin) * w))
        y1 = max(0, int((bbox.ymin - margin) * h))
        x2 = min(w, int((bbox.xmin + bbox.width + margin) * w))
        y2 = min(h, int((bbox.ymin + bbox.height + margin) * h))

        face_crop = frame[y1:y2, x1:x2]

        if face_crop.size == 0:
            raise HTTPException(status_code=400, detail="Invalid face crop")

        # 🔥 Resize (ArcFace standard)
        face_crop = cv2.resize(face_crop, (112, 112))

        # ---------------- EMBEDDING ---------------- #
        embedding = embedder.get_embedding(face_crop)

        if embedding is None:
            raise HTTPException(status_code=400, detail="Face embedding failed")

        # 🔥 Normalize
        norm = np.linalg.norm(embedding)
        if norm == 0:
            raise HTTPException(status_code=400, detail="Invalid embedding")

        embedding = embedding / norm

        # ---------------- SAVE USER ---------------- #
        user = User(
            name=name,
            reg_no=reg_no,
            college=college,
            embedding=embedding.astype(np.float32).tobytes()
        )

        # 🔥 RETRY FIX FOR SQLITE LOCK
        for _ in range(3):
            try:
                db.add(user)
                db.commit()
                db.refresh(user)
                break
            except:
                db.rollback()
                time.sleep(0.5)
        else:
            raise HTTPException(status_code=500, detail="Database busy, try again")

        return {
            "message": "User registered successfully",
            "user_id": user.id
        }

    except HTTPException as e:
        db.rollback()
        raise e

    except Exception as e:
        db.rollback()
        print("REGISTER ERROR:", str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")

    finally:
        db.close()


# ---------------- GET ALL USERS ---------------- #
@router.get("/users")
def get_users():
    db = SessionLocal()

    try:
        users = db.query(User).all()

        return [
            {
                "id": u.id,
                "name": u.name,
                "reg_no": u.reg_no,
                "college": u.college
            }
            for u in users
        ]

    finally:
        db.close()