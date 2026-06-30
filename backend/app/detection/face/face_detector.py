# """
# Person detection using YOLOv8m
# """

# from ultralytics import YOLO
# from app.config import DEVICE, PERSON_CONFIDENCE_THRESHOLD


# class FaceDetector:
#     def __init__(self):
#         # Load YOLOv8 medium model (better accuracy)
#         self.model = YOLO("yolov8m.pt")
#         self.model.to(DEVICE)

#     def detect(self, frame):
#         results = self.model(frame, device=DEVICE, verbose=False)

#         detections = []

#         for r in results:
#             for box in r.boxes:
#                 cls = int(box.cls[0])
#                 conf = float(box.conf[0])

#                 # COCO class 0 = person
#                 if cls == 0 and conf > PERSON_CONFIDENCE_THRESHOLD:
#                     x1, y1, x2, y2 = map(int, box.xyxy[0])
#                     width = x2 - x1
#                     height = y2 - y1

#                     detections.append(([x1, y1, width, height], conf, "person"))

#         return detections




# ## ----------------correct code----------------- ##


# """
# Robust Face Detection using YOLOv8-Face
# Handles:
# - Partial faces
# - Side faces
# - Masked faces
# - Corner faces
# """

from ultralytics import YOLO
import cv2


class FaceDetector:
    def __init__(self):
        # Use face-specific trained model
        self.model = YOLO("models/yolov8n-face.pt")
        self.model.to("cpu")   # change to "cuda" if GPU available

    def detect(self, frame):

        # Higher resolution improves partial detection
        resized = cv2.resize(frame, (960, 540))

        results = self.model(
            resized,
            conf=0.25,    # lower threshold for partial faces
            iou=0.5,
            imgsz=960,
            verbose=False
        )

        detections = []

        for r in results:
            for box in r.boxes:
                conf = float(box.conf[0])

                x1, y1, x2, y2 = map(int, box.xyxy[0])

                width = x2 - x1
                height = y2 - y1

                detections.append(([x1, y1, width, height], conf, "face"))

        return detections








#  ## ------------------------------------- ##

# from ultralytics import YOLO
# import cv2


# class FaceDetector:

#     def __init__(self):

#         # Face specialized model
#         self.model = YOLO("models/yolov8n-face.pt")

#         # Use CPU or CUDA automatically
#         try:
#             self.model.to("cuda")
#         except:
#             self.model.to("cpu")

#     def detect(self, frame):

#         h, w = frame.shape[:2]

#         # Resize but maintain better aspect detection
#         resized = cv2.resize(frame, (800, 600))

#         scale_x = w / 800
#         scale_y = h / 600

#         results = self.model(
#             resized,
#             conf=0.30,      # balanced threshold
#             iou=0.45,
#             imgsz=800,
#             verbose=False
#         )

#         detections = []

#         for r in results:
#             for box in r.boxes:

#                 conf = float(box.conf[0])

#                 x1, y1, x2, y2 = map(int, box.xyxy[0])

#                 # scale back to original frame
#                 x1 = int(x1 * scale_x)
#                 y1 = int(y1 * scale_y)
#                 x2 = int(x2 * scale_x)
#                 y2 = int(y2 * scale_y)

#                 width = x2 - x1
#                 height = y2 - y1

#                 # remove very small noise boxes
#                 if width * height < (w * h * 0.01):
#                     continue

#                 detections.append(([x1, y1, width, height], conf, "face"))

#         return detections