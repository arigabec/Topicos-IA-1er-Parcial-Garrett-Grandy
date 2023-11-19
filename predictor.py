from typing import Any
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import matplotlib.pyplot as plt

POSE_MODEL_PATH = "1erParcial/pose_landmarker_lite.task"

class PoseDetector:
    def __init__(self, model_path=POSE_MODEL_PATH):
        # Crear modelo
        base_options = python.BaseOptions(model_asset_path=POSE_MODEL_PATH)
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            output_segmentation_masks=True)
        self.model = vision.PoseLandmarker.create_from_options(options)

    def predict_image(self, image_array: np.ndarray):
        # Convertir array de numpy a formato compatible
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_array)
        detection = self.model.detect(mp_image)
        return detection

    def display_color_row(*imgs):
        for i, img in enumerate(imgs):
            print(type(img), img.dtype, img[0, 0])
            plt.subplot(1, len(imgs), i + 1)
            plt.imshow(img)
            plt.title(f"{i}")
            plt.xticks([])
            plt.yticks([])


if __name__ == "__main__":
    image = "1erParcial/person.jpg"
    img = cv2.cvtColor(cv2.imread(image), cv2.COLOR_BGR2RGB)
    predictor = PoseDetector()
    prediction = predictor.predict_image(img)
    print(predictor)
    # annotated_image = predictor.draw_landmarks_on_image(image.numpy_view(), prediction)
    # predictor.display_color_row(image.numpy_view(), annotated_image)
