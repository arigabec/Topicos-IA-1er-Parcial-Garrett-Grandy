import io
import time
import csv
from fastapi.responses import FileResponse
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
    allow_origins=["http://localhost:3000"],  # Replace with the actual URL of your React app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
pose_detector = PoseDetector()

# Lista donde se almacenran los datos de cada request de /poses
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
    # convertir a una imagen de Pillow
    img_obj = Image.open(img_stream)
    # crear array de numpy
    img_array = np.array(img_obj)
    
    # Realizar la predicción
    results = predictor.predict_image(img_array)
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    return results, img_array, execution_time

@app.get("/status")
def get_status():
    return {"status": "ok",
            "message": "Pose classification API is running",
            "model": "Pose classification model",
            "version": "1.0.0",
            "author": "Camila Grandy Camacho y Ariane Garrett Becerra",
            }

@app.post("/poses")
def detect_poses(
    file: UploadFile = File(...), 
    predictor: PoseDetector = Depends(get_pose_detector)
) -> Response:
    results, img, execution_time = predict_uploadfile(predictor, file)

    pose_landmarks_list = results.pose_landmarks
    annotated_image = np.copy(img)

    # Iterar las diferentes poses y reconocer
    for idx in range(len(pose_landmarks_list)):
        pose_landmarks = pose_landmarks_list[idx]
        print(pose_landmarks)
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

    # Guardamos los datos del request
    execution_log = {
        "date": time.ctime(), # Fecha y hora en la que se realizo el request
        "filename": str(file.filename), # Nombre del archivo
        "execution_time": str(execution_time), # Tiempo de ejecucion
        "image_size": str(img.size), # Tamaño de la imagen
        "content_type": str(file.content_type), # Formato de la imagen
        "model": "pose_landmarker_lite.task" # Modelo utilizado
        # Añadir prediccion
    }
    execution_logs.append(execution_log)
    
    headers = {
        # Muestra las landmarks predichas en la imagen
        "pose_landmarks_list": str(pose_landmarks_list),
        # Muestra el tiempo de ejecución de la solicitud
        "execution_time": str(execution_time),
        # Muestra el tamaño de la imagen 
        "image_size": str(img.size),
        # Muestra el formato de la imagen, que puede ser JPEG, PNG, etc
        "shape": str(img.shape),
        # Muestra el tipo de datos de la imagen, que puede ser uint8, int32, etc
        "dtype": str(img.dtype),
        # Muestra la fecha y hora en que se realizó la solicitud
        "date": str(time.ctime()),
        # Muestra el nombre del archivo de imagen
        "filename": str(file.filename),
        # Muestra el formato de la imagen, que puede ser JPEG, PNG, etc
        "content_type": str(file.content_type),  
    }
        
    return Response(content=image_stream.read(), media_type="image/jpeg", status_code=200, headers=headers)


@app.get("/reports")
def generate_report():
    # Generar el reporte en formato CSV
    if not execution_logs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Por el momento no existen reportes!"
        )

    # Definimos el nombre del archivo CSV
    csv_file_path = "poses_report.csv"

    # Añadimos los execution_logs al archivo a generar
    with open(csv_file_path, mode="w", newline="") as csv_file:
        fieldnames = execution_logs[0].keys()
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(execution_logs)

    # Devolvemos el archivo generado
    return FileResponse(csv_file_path, filename="poses_report.csv", media_type="text/csv")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", reload=True)
