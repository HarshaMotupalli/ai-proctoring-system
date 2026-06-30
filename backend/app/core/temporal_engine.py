# """
# Temporal Verification Engine
# Implements duration-based suspicious behavior detection
# """

# import time


# class TemporalEngine:
#     def __init__(self):
#         # Store active events
#         self.events = {}

#         # Threshold durations (in seconds)
#         self.thresholds = {
#             "eyes_off_screen": 10,
#             "no_face": 8,
#             "multiple_faces": 5,
#             "head_turned": 7,
#             "looking_away": 7,
#             "phone_detected": 6
#         }

#     def update_event(self, event_type, is_active):
#         current_time = time.time()

#         if event_type not in self.events:
#             self.events[event_type] = {
#                 "start_time": None,
#                 "active": False
#             }

#         event = self.events[event_type]

#         if is_active:
#             if not event["active"]:
#                 event["start_time"] = current_time
#                 event["active"] = True
#         else:
#             event["start_time"] = None
#             event["active"] = False

#     def check_violation(self, event_type):
#         event = self.events.get(event_type)

#         if not event or not event["active"]:
#             return False, 0

#         duration = time.time() - event["start_time"]
#         threshold = self.thresholds.get(event_type, 10)

#         confidence = int((duration / threshold) * 100)

#         if duration >= threshold:
#             return True, min(confidence, 100)

#         return False, min(confidence, 100)


"""
Temporal Verification Engine
Enhanced with frame locking for accurate evidence capture
"""

import time


class TemporalEngine:
    def __init__(self):
        # Store active events
        self.events = {}

        # Threshold durations (in seconds)
        self.thresholds = {
            "eyes_off_screen": 10,
            "no_face": 8,
            "multiple_faces": 5,
            "head_turned": 7,
            "looking_away": 7,
            "phone_detected": 6
        }

    def update_event(self, event_type, is_active, frame_buffer=None):
        current_time = time.time()

        if event_type not in self.events:
            self.events[event_type] = {
                "start_time": None,
                "active": False,
                "locked_frame": None,
                "saved": False
            }

        event = self.events[event_type]

        if is_active:
            if not event["active"]:
                # Event starts
                event["start_time"] = current_time
                event["active"] = True
                event["saved"] = False

                # 🔥 LOCK FRAME at violation start
                if frame_buffer:
                    event["locked_frame"] = frame_buffer.get_latest_frame()
        else:
            # Reset event
            event["start_time"] = None
            event["active"] = False
            event["locked_frame"] = None
            event["saved"] = False

    def check_violation(self, event_type, frame_buffer=None):
        event = self.events.get(event_type)

        if not event or not event["active"]:
            return False, 0, None

        duration = time.time() - event["start_time"]
        threshold = self.thresholds.get(event_type, 10)

        confidence = int((duration / threshold) * 100)

        if duration >= threshold:
            # 🔥 Get correct frame
            frame_to_save = event["locked_frame"]

            # Fallback if needed
            if frame_to_save is None and frame_buffer:
                frame_to_save = frame_buffer.get_frame_before_seconds(1)

            # Prevent multiple saves
            if not event["saved"]:
                event["saved"] = True
                return True, min(confidence, 100), frame_to_save

        return False, min(confidence, 100), None