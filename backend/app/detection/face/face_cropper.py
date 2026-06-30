"""
Face detection + cropping before embedding
"""

from ultralytics import YOLO
import os
import cv2


class FaceCropper:
    def __init__(self):
        base_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../../")
        )
        model_path = os.path.join(base_dir, "models", "yolov8n-face.pt")

        self.model = YOLO(model_path)

    def crop_largest_face(self, frame):
        results = self.model(frame, verbose=False)

        boxes = []
        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                area = (x2 - x1) * (y2 - y1)
                boxes.append((area, x1, y1, x2, y2))

        if not boxes:
            return None

        # Pick largest face
        boxes.sort(reverse=True)
        _, x1, y1, x2, y2 = boxes[0]

        face_crop = frame[y1:y2, x1:x2]
        return face_crop