# import os
# import onnxruntime as ort
# import numpy as np
# import cv2


# class FaceEmbedding:
#     def __init__(self):
#         # Get backend directory properly
#         base_dir = os.path.abspath(
#             os.path.join(os.path.dirname(__file__), "../../../")
#         )

#         model_path = os.path.join(base_dir, "models", "arcface.onnx")

#         if not os.path.exists(model_path):
#             raise Exception(f"Model not found at: {model_path}")

#         print("Loading ArcFace model from:", model_path)

#         self.session = ort.InferenceSession(
#             model_path,
#             providers=['CUDAExecutionProvider']  #, 'CPUExecutionProvider'
#         )

#     def preprocess(self, img):
#         # Resize to required size
#         img = cv2.resize(img, (112, 112))

#         # Convert BGR to RGB
#         img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

#         # Normalize
#         img = img.astype(np.float32)
#         img = (img - 127.5) / 128.0

#         # IMPORTANT: Do NOT transpose
#         # Keep NHWC format for this ONNX model

#         # Add batch dimension → (1,112,112,3)
#         img = np.expand_dims(img, axis=0)

#         return img

#     def get_embedding(self, frame):
#         input_tensor = self.preprocess(frame)

#         input_name = self.session.get_inputs()[0].name
#         outputs = self.session.run(None, {input_name: input_tensor})

#         embedding = outputs[0][0]

#         # Normalize embedding
#         embedding = embedding / np.linalg.norm(embedding)

#         return embedding



import os
import onnxruntime as ort
import numpy as np
import cv2


class FaceEmbedder:

    def __init__(self):

        base_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../../")
        )

        model_path = os.path.join(base_dir, "models", "arcface.onnx")

        if not os.path.exists(model_path):
            raise Exception(f"Model not found at: {model_path}")

        print("Loading ArcFace model from:", model_path)

        # Try GPU first, fallback to CPU
        providers = [
            "CUDAExecutionProvider",
            "CPUExecutionProvider"
        ]

        self.session = ort.InferenceSession(
            model_path,
            providers=providers
        )

        self.input_name = self.session.get_inputs()[0].name

    def preprocess(self, img):

        img = cv2.resize(img, (112, 112))

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        img = img.astype(np.float32)

        img = (img - 127.5) / 128.0

        img = np.expand_dims(img, axis=0)

        return img

    def get_embedding(self, frame):

        input_tensor = self.preprocess(frame)

        outputs = self.session.run(
            None,
            {self.input_name: input_tensor}
        )

        embedding = outputs[0][0]

        embedding = embedding / np.linalg.norm(embedding)

        return embedding