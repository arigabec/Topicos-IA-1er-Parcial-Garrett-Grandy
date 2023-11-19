import io
from fastapi import (
    FastAPI, 
    UploadFile, 
    File, 
    HTTPException, 
    status,
    Depends
)
from fastapi.responses import Response
import numpy as np
from PIL import Image
from predictor import PoseDetector
from mediapipe.framework.formats import landmark_pb2
from mediapipe import solutions

app = FastAPI(title="Pose classification API")

pose_detector = PoseDetector()

def get_pose_detector():
    return pose_detector

def predict_uploadfile(predictor, file):
    img_stream = io.BytesIO(file.file.read())
    if file.content_type.split("/")[0] != "image":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, 
            detail="Not an image"
        )
    # convertir a una imagen de Pillow
    img_obj = Image.open(img_stream)
    # crear array de numpy
    img_array = np.array(img_obj)
    return predictor.predict_image(img_array), img_array

@app.post("/poses")
def detect_poses(
    file: UploadFile = File(...), 
    predictor: PoseDetector = Depends(get_pose_detector)
) -> Response:
    results, img = predict_uploadfile(predictor, file)

    pose_landmarks_list = results.pose_landmarks
    annotated_image = np.copy(img)

    # Iterar las diferentes poses y reconocer
    for idx in range(len(pose_landmarks_list)):
        pose_landmarks = pose_landmarks_list[idx]

        # Dibujar los landmarks de la pose
        pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        pose_landmarks_proto.landmark.extend([
            landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in pose_landmarks
        ])
        solutions.drawing_utils.draw_landmarks(
            annotated_image,
            pose_landmarks_proto,
            solutions.pose.POSE_CONNECTIONS,
            solutions.drawing_styles.get_default_pose_landmarks_style())
    
    img_pil = Image.fromarray(annotated_image)
    image_stream = io.BytesIO()
    img_pil.save(image_stream, format="JPEG")
    image_stream.seek(0)
    return Response(content=image_stream.read(), media_type="image/jpeg")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", reload=True)