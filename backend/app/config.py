"""
Global configuration settings
"""

import torch

# Detect GPU automatically
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print("=================================")
print("AI PROCTORING SYSTEM STARTING...")
print("Using Device:", DEVICE)
print("=================================")

# Detection threshold
PERSON_CONFIDENCE_THRESHOLD = 0.6

# Frame settings
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FPS = 20
FACE_SIMILARITY_THRESHOLD = 0.85