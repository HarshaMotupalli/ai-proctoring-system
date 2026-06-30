# #------------------CORRECT CODE------------------#
# """
# Cheating Object Detection using YOLOv8 
# """

from ultralytics import YOLO
import cv2

class ObjectDetector:
    def __init__(self):
        self.model = YOLO("yolov8m.pt")

        # Relevant cheating objects
        self.cheating_classes = {
            67: "phone",
            # 63: "laptop",
            # 62: "monitor",
            73: "book"
        }

    def detect_objects(self, frame):
        h, w, _ = frame.shape

        # Speed boost
        small_frame = cv2.resize(frame, (640, 360))
        results = self.model(small_frame, verbose=False)

        detected = []

        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])

                if cls_id in self.cheating_classes and conf > 0.30:

                    detected.append(self.cheating_classes[cls_id])

        return detected










# #------------------WITHOUT TRACKING------------------#
# from ultralytics import YOLO
# import cv2


# class ObjectDetector:

#     def __init__(self):

#         # YOLOv8 medium gives good balance of speed & accuracy
#         self.model = YOLO("yolov8m.pt")

#         # cheating related objects
#         self.cheating_classes = {
#             67: "cell phone",
#             73: "book"
#         }

#         # individual thresholds
#         self.thresholds = {
#             "cell phone": 0.35,
#             "book": 0.45
#         }

#     def detect_objects(self, frame):

#         h, w = frame.shape[:2]

#         # keep higher resolution to detect partial phones
#         resized = cv2.resize(frame, (960, 540))

#         results = self.model(
#             resized,
#             imgsz=960,
#             conf=0.25,
#             verbose=False
#         )

#         detected = []

#         for r in results:
#             for box in r.boxes:

#                 cls_id = int(box.cls[0])
#                 conf = float(box.conf[0])

#                 if cls_id not in self.cheating_classes:
#                     continue

#                 label = self.cheating_classes[cls_id]

#                 # apply class-specific threshold
#                 if conf < self.thresholds[label]:
#                     continue

#                 x1, y1, x2, y2 = map(int, box.xyxy[0])

#                 box_area = (x2 - x1) * (y2 - y1)

#                 # remove extremely tiny detections
#                 if box_area < (w * h * 0.005):
#                     continue

#                 detected.append(label)

#         # remove duplicates
#         return list(set(detected))



#------------------WITH TRACKING------------------#
# from ultralytics import YOLO
# from deep_sort_realtime.deepsort_tracker import DeepSort
# import cv2


# class ObjectDetector:

#     def __init__(self):

#         # YOLO model
#         self.model = YOLO("yolov8m.pt")

#         # Tracker
#         self.tracker = DeepSort(
#             max_age=10,
#             n_init=2,
#             max_iou_distance=0.7
#         )

#         # cheating objects
#         self.cheating_classes = {
#             67: "cell phone",
#             73: "book"
#         }

#         # thresholds
#         self.thresholds = {
#             "cell phone": 0.35,
#             "book": 0.45
#         }

#     def detect_objects(self, frame):

#         h, w = frame.shape[:2]

#         # resize for better detection
#         resized = cv2.resize(frame, (960, 540))

#         results = self.model(
#             resized,
#             imgsz=960,
#             conf=0.25,
#             verbose=False
#         )

#         detections = []

#         for r in results:
#             for box in r.boxes:

#                 cls_id = int(box.cls[0])
#                 conf = float(box.conf[0])

#                 if cls_id not in self.cheating_classes:
#                     continue

#                 label = self.cheating_classes[cls_id]

#                 if conf < self.thresholds[label]:
#                     continue

#                 x1, y1, x2, y2 = map(int, box.xyxy[0])

#                 detections.append(
#                     ([x1, y1, x2 - x1, y2 - y1], conf, label)
#                 )

#         # update tracker
#         tracks = self.tracker.update_tracks(detections, frame=resized)

#         detected = []

#         for track in tracks:

#             if not track.is_confirmed():
#                 continue

#             label = track.get_det_class()

#             if label in ["cell phone", "book"]:
#                 detected.append(label)

#         return list(set(detected))