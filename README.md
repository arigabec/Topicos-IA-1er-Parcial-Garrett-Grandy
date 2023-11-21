# Primer Parcial - Tópicos Selectos en IA

### Nombres: Ariane Garrett - Camila Grandy
### Código: 54617 - 56584

El proyecto en el que trabajamos es una Pose Detection API. Usando el modelo de detection de landmarks de MediaPipe (Pose Landmark Detection), 
desarrollamos una página web sencilla que permite hacer peticiones a nuestra API de reconocimiento.

## Primeras configuraciones
Para iniciar el proyecto, debemos clonar el repositorio con el siguiente comando:

```bash
git clone https://github.com/arigabec/Topicos-IA-1er-Parcial-Garrett-Grandy.git
```
Una vez obtenido el proyecto completo debemos ejecutar los siguientes comandos en la rama *master*, en la carpeta donde clonamos el proyecto,
para poder visualizar el proyecto funcionando con ambos servicios levantados (tanto frontend como backend):

- Frontend, levantamos el servicio e ingresamos al link que se devuelve como respuesta (localhost:3000):
```bash
cd Topicos-IA-1er-Parcial-Garrett-Grandy/pose-detection-app
npm install
npm start
```

- Backend, para poder ejecutar el código correctamente se debe tener un entorno vitual funcionando, y debe tener instaladas las dependencias de uvicorn, mediapipe y fastapi. En caso de que no funcione el 2do comando, se utiliza el 3er comando:
```bash
cd Topicos-IA-1er-Parcial-Garrett-Grandy
python.exe app.py
uvicorn app:app
```

## Explicacion del modelo de prediccion y la página web
La página web nos muestra 3 botones, y cada uno de estos realiza una peticion diferente a la API.

- Show API status: al hacer click en este botón, se hace un /get request a la API que simplemente nos devuelve el estado en el que se encuentra el servicio actualmente. Podemos visualizar estos datos en una tabla que se despliega bajo el botón.

- Predict Pose: al hacer click en este botón se despliega un botón de seleccionar archivo, en el que debemos seleccionar la imagen con la que queremos hacer una predicción. Una vez seleccionado el archivo hacemos click en "Submit", y se hace el /post request a la API, que devuelve los datos de la predicción incluyendo la imagen con los landmarks predichos,  la predicción de la pose (que en este caso, devuelve la predicción si la persona en la imagen se encuentra con la mano derecha o izquierda levantada), el tiempo de ejecución, el tamaño de la imagen, el tipo de imagen, la fecha exacta en la que se realizó la petición y otros datos que consideramos importantes.

- Get Report: al hacer click en este botón se descarga un archivo .csv que contiene los registros de las últimas prediccioens realizadas. De igual manera, registra los datos importantes ya mencionados anteriormente.