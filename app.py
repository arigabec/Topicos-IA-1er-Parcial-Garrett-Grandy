import io
import time
import csv
import base64
from fastapi.responses import FileResponse, JSONResponse
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
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Pose classification API")

# Permitimos el uso de CORS para el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
pose_detector = PoseDetector()

# Colocamos en una lista los datos de cada request de /poses
execution_logs = []

def get_pose_detector():
    return pose_detector

def predict_uploadfile(predictor, file):
    start_time = time.time()
    
    img_stream = io.BytesIO(file.file.read())
    if file.content_type.split("/")[0] != "image":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, 
            detail="Not an image"
        )
    img_obj = Image.open(img_stream)
    img_array = np.array(img_obj)
    
    # Realizamos la predicción
    results, pose_labels = predictor.predict_image(img_array)
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    return results, img_array, execution_time, pose_labels

@app.get("/status")
def get_status():
    return {"status": "ok",
            "message": "Pose classification API is running",
            "model": "Pose Landmarker utiliza una serie de modelos para predecir puntos de referencia de pose. El primer modelo detecta la presencia de cuerpos humanos dentro de un marco de imagen y el segundo modelo localiza puntos de referencia en los cuerpos."
            "En este caso se utiliza el Pose landmarker model que agrega un mapeo completo de la pose. El modelo genera una estimación de 33 puntos de referencia de pose tridimensionales.",
            "service": "Pose classification API es un servicio que permite detectar poses en imágenes.",
            "version": "1.0.0",
            "author": "Camila Grandy Camacho y Ariane Garrett Becerra",
            }

@app.post("/poses")
def detect_poses(
    file: UploadFile = File(...), 
    predictor: PoseDetector = Depends(get_pose_detector)
) -> JSONResponse:
    results, img, execution_time, pose_labels = predict_uploadfile(predictor, file)

    pose_landmarks_list = results.pose_landmarks
    annotated_image = np.copy(img)

    pose_landmarks_proto = []

    # Iteramos las diferentes poses y reconocer
    for idx in range(len(pose_landmarks_list)):
        pose_landmarks = pose_landmarks_list[idx]

        # Dibujamos los landmarks de la pose
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
    img_base64 = base64.b64encode(image_stream.read()).decode('utf-8')

    # Guardamos los datos del request
    headers = {
        # Mostramos los landmarks predichas en la imagen
        "landmarks_found": str(pose_landmarks_proto.landmark),
        # Mostramos la predicción de la pose (si la mano derecha o izquierda está levantada)
        "pose_labels": pose_labels,
        # Mostramos el tiempo de ejecución de la solicitud
        "execution_time": str(execution_time),
        # Mostramos el tamaño de la imagen 
        "image_size": str(img.size),
        # Mostramos el formato de la imagen, que puede ser JPEG, PNG, etc
        "shape": str(img.shape),
        # Mostramos el tipo de datos de la imagen, que puede ser uint8, int32, etc
        "dtype": str(img.dtype),
        # Mostramos la fecha y hora en que se realizó la solicitud
        "date": str(time.ctime()),
        # Mostramos el nombre del archivo de imagen
        "filename": str(file.filename),
        # Mostramos el formato de la imagen, que puede ser JPEG, PNG, etc
        "content_type": str(file.content_type),  
    }
    execution_logs.append(headers)
        
    return JSONResponse(content={"image": img_base64, "headers": headers}, status_code=200)

@app.get("/reports")
def generate_report():
    if not execution_logs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Por el momento no existen reportes!"
        )

    csv_file_path = "poses_report.csv"

    with open(csv_file_path, mode="w", newline="") as csv_file:
        fieldnames = execution_logs[0].keys()
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(execution_logs)

    return FileResponse(csv_file_path, filename="poses_report.csv", media_type="text/csv")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", reload=True)