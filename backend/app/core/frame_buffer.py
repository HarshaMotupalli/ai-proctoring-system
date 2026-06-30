# """
# Stores recent frames in memory.
# Will be used later for evidence clip saving.
# """

# from collections import deque
# import time


# class FrameBuffer:
#     def __init__(self, max_seconds=20, fps=20):
#         self.buffer = deque(maxlen=max_seconds * fps)

#     def add_frame(self, frame):
#         self.buffer.append((time.time(), frame.copy()))

#     def get_recent_frames(self):
#         return list(self.buffer)

"""
Enhanced Frame Buffer for accurate evidence capture.
Stores timestamped frames and allows retrieval of correct violation frames.
"""

from collections import deque
import time


class FrameBuffer:
    def __init__(self, max_seconds=20, fps=20):
        self.buffer = deque(maxlen=max_seconds * fps)

    def add_frame(self, frame):
        """
        Store frame with timestamp
        """
        self.buffer.append((time.time(), frame.copy()))

    def get_recent_frames(self):
        """
        Return all frames (for debugging if needed)
        """
        return list(self.buffer)

    def get_latest_frame(self):
        """
        Get most recent frame
        """
        return self.buffer[-1][1] if self.buffer else None

    def get_frame_at_time(self, target_time):
        """
        Get frame closest to a given timestamp
        """
        if not self.buffer:
            return None

        closest_frame = None
        min_diff = float("inf")

        for t, frame in self.buffer:
            diff = abs(t - target_time)
            if diff < min_diff:
                min_diff = diff
                closest_frame = frame

        return closest_frame

    def get_frame_before_seconds(self, seconds_ago=2):
        """
        Get frame from a few seconds ago
        (helps capture correct violation moment)
        """
        target_time = time.time() - seconds_ago
        return self.get_frame_at_time(target_time)

    def get_delayed_frame(self, delay_frames=5):
        """
        Get frame from a few frames before (frame-based delay)
        """
        if len(self.buffer) > delay_frames:
            return list(self.buffer)[-delay_frames][1]
        return self.get_latest_frame()