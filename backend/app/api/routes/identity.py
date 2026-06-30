"""
Identity Verification API
Handles ID upload and live verification.
"""

from fastapi import APIRouter, UploadFile, File
import cv2
import numpy as np

from app.detection.face.face_embedding import FaceEmbedder
from app.detection.face.identity_verifier import IdentityVerifier
from app.detection.face.face_cropper import FaceCropper

router = APIRouter()

embedding_model = FaceEmbedder()
verifier = IdentityVerifier()
cropper = FaceCropper()

# Temporary storage (later move to DB)
stored_embedding = None


@router.post("/upload-id")
async def upload_id(file: UploadFile = File(...)):
    global stored_embedding

    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Basic safety check
    if frame is None:
        return {"success": False, "message": "Invalid image"}

    try:
        face = cropper.crop_largest_face(frame)

        if face is None:
            return {"success": False, "message": "No face detected"}

        emb = embedding_model.get_embedding(face)
    except Exception as e:
        print("Embedding error:", e)
        return {"success": False, "message": "Embedding failed"}

    stored_embedding = emb

    return {"success": True, "message": "ID stored successfully"}


@router.post("/verify-live")
async def verify_live(file: UploadFile = File(...)):
    global stored_embedding

    if stored_embedding is None:
        return {"success": False, "message": "No ID uploaded"}

    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if frame is None:
        return {"success": False, "message": "Invalid image"}

    try:
        face = cropper.crop_largest_face(frame)

        if face is None:
            return {"success": False, "message": "No face detected"}

        live_emb = embedding_model.get_embedding(face)
    except Exception as e:
        print("Live embedding error:", e)
        return {"success": False, "message": "Embedding failed"}

    is_match, score = verifier.verify(stored_embedding, live_emb)

    return {
        "success": is_match,
        "similarity_score": score
    }