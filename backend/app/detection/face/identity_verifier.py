"""
Identity Verification Logic
Compares stored embedding with live embedding.
"""

import numpy as np
from app.config import FACE_SIMILARITY_THRESHOLD


class IdentityVerifier:

    @staticmethod
    def cosine_similarity(emb1, emb2):
        emb1 = emb1 / np.linalg.norm(emb1)
        emb2 = emb2 / np.linalg.norm(emb2)
        return np.dot(emb1, emb2)

    def verify(self, stored_embedding, live_embedding):
        score = self.cosine_similarity(stored_embedding, live_embedding)
        is_match = score >= FACE_SIMILARITY_THRESHOLD
        # Convert NumPy types to Python native types
        return bool(is_match), float(score)