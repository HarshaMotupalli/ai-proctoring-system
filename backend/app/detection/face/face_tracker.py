"""
DeepSORT tracking to prevent flickering
"""

from deep_sort_realtime.deepsort_tracker import DeepSort


class FaceTracker:
    def __init__(self):
        self.tracker = DeepSort(
            max_age=30,
            n_init=3,
            max_cosine_distance=0.3
        )

    def update(self, detections, frame):
        tracks = self.tracker.update_tracks(detections, frame=frame)

        tracked = []

        for track in tracks:
            if not track.is_confirmed():
                continue

            l, t, r, b = track.to_ltrb()
            track_id = track.track_id

            tracked.append([int(l), int(t), int(r), int(b), track_id])

        return tracked