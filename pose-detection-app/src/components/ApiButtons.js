import React, { useState } from 'react';
import axios from 'axios';
import { Button, Grid, Container, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from '@mui/material';

const ApiButtons = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [prediction, setPrediction] = useState(false);
  const [resultImage, setResultImage] = useState(null);
  const [apiResponse, setApiResponse] = useState(null);
  const [showTable, setShowTable] = useState(false);
  const [apiResponsePost, setApiResponsePost] = useState(null);

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const openModal = () => {
    setPrediction(true);
    setShowTable(false); // Ocultar la tabla al hacer clic en "Predict Pose"
  };

  const handleStatusButtonClick = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:8000/status');
      setApiResponse(response.data);
      setShowTable(true); // Mostrar la tabla cuando se recibe una respuesta
      setResultImage(null); // Limpiar la imagen
    } catch (error) {
      console.error('Error calling /status:', error);
      setShowTable(false); // Ocultar la tabla en caso de error
    }
  };

  const handlePosesButtonClick = async () => {
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      // Limpiar los datos de la solicitud de estado y de la predicción
      setApiResponse(null);
      setApiResponsePost(null);

      const response = await axios.post('http://127.0.0.1:8000/poses', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        withCredentials: true,
        responseType: 'json'
      });

      setResultImage(`data:image/jpeg;base64,${response.data.image}`);
      setApiResponsePost(response.data.headers);
      setShowTable(true);
    } catch (error) {
      console.error('Error calling /poses:', error);
      setShowTable(false); // Ocultar la tabla en caso de error
    }
  };

  const handleReportsButtonClick = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:8000/reports', {
        responseType: 'blob',
      });

      // Creamos una url para poder almacenar el archivo csv
      const blobUrl = URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = blobUrl;
      link.download = 'pose_report.csv';

      // Creamos el trigger que nos permitirá descargar el documento
      document.body.appendChild(link);
      link.click();

      // Removemos los datos de modo que nos servirán para otra petición
      document.body.removeChild(link);
      URL.revokeObjectURL(blobUrl);
      setShowTable(false); // Ocultar la tabla cuando se realiza otra acción
    } catch (error) {
      console.error('Error fetching report:', error);
    }
  };

  return (
    <Container sx={{
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      marginTop: '5rem',
    }}>
      <Typography variant="h1" component="h1" gutterBottom>
        Pose Detection App
      </Typography>
      <Grid container spacing={30} direction="row" alignItems="center">
        <Grid item>
          <Button variant="contained" onClick={handleStatusButtonClick}>
            Show API status
          </Button>
        </Grid>
        <Grid item>
          <Button variant="contained" onClick={openModal}>
            Predict Pose
          </Button>
          {prediction && (
            <div>
              <input type="file" onChange={handleFileChange} />
              <Button variant="contained" onClick={handlePosesButtonClick}>
                Submit
              </Button>
            </div>
          )}
        </Grid>
        <Grid item>
          <Button variant="contained" onClick={handleReportsButtonClick}>
            Get report
          </Button>
        </Grid>
      </Grid>

      {resultImage && (
        <Grid container item justifyContent="center">
          <img src={resultImage} alt="Pose result" />
        </Grid>
      )}
      {showTable && (
        <div>
          {/* Tabla para /STATUS */}
          <TableContainer component={Paper} elevation={3} style={{ marginTop: '20px' }}>
            <Typography variant="h2" component="h2" gutterBottom sx={{ /* Estilos */ }}>
              API /STATUS
            </Typography>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Property</TableCell>
                  <TableCell>Value</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {apiResponse &&
                  Object.entries(apiResponse).map(([property, value]) => (
                    <TableRow key={property}>
                      <TableCell>{property}</TableCell>
                      <TableCell>{value}</TableCell>
                    </TableRow>
                  ))}
              </TableBody>
            </Table>
          </TableContainer>

          {/* Tabla para /POSES */}
          <TableContainer component={Paper} elevation={3} style={{ marginTop: '20px' }}>
            <Typography variant="h2" component="h2" gutterBottom sx={{ /* Estilos */ }}>
              API /POSES
            </Typography>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Property</TableCell>
                  <TableCell>Value</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {apiResponsePost &&
                  Object.entries(apiResponsePost).map(([property, value]) => (
                    <TableRow key={property}>
                      <TableCell>{property}</TableCell>
                      <TableCell>{value}</TableCell>
                    </TableRow>
                  ))}
              </TableBody>
            </Table>
          </TableContainer>
        </div>
      )}
    </Container>
  );
};

export default ApiButtons;