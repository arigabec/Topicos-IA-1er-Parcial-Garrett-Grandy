from typing import Any
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import matplotlib.pyplot as plt

POSE_MODEL_PATH = "pose_landmarker_lite.task"

class PoseDetector:
    def __init__(self, model_path=POSE_MODEL_PATH):
        base_options = python.BaseOptions(model_asset_path=POSE_MODEL_PATH)
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            output_segmentation_masks=True)
        self.model = vision.PoseLandmarker.create_from_options(options)

    def predict_image(self, image_array: np.ndarray):
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_array)
        detection = self.model.detect(mp_image)
        results = detection.pose_landmarks

        # Clasificamos la pose
        pose_labels = self.classify_pose(results)

        return detection, pose_labels

    def classify_pose(self, pose_landmarks_list):
        classifications = []

        for pose_landmarks in pose_landmarks_list:
            right_wrist_y = pose_landmarks[mp.solutions.pose.PoseLandmark.RIGHT_WRIST.value].y
            left_wrist_y = pose_landmarks[mp.solutions.pose.PoseLandmark.LEFT_WRIST.value].y

            if right_wrist_y > left_wrist_y:
                classifications.append("Derecha Levantada")
            else:
                classifications.append("Izquierda Levantada")

        return classifications

    def display_color_row(*imgs):
        for i, img in enumerate(imgs):
            print(type(img), img.dtype, img[0, 0])
            plt.subplot(1, len(imgs), i + 1)
            plt.imshow(img)
            plt.title(f"{i}")
            plt.xticks([])
            plt.yticks([])


if __name__ == "__main__":
    image = "person1.jpeg"
    img = cv2.cvtColor(cv2.imread(image), cv2.COLOR_BGR2RGB)
    predictor = PoseDetector()
    detection, pose_labels = predictor.predict_image(img)
    print (detection)
    print("Pose Labels:", pose_labels)

