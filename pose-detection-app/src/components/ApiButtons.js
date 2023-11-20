import React, { useState } from 'react';
import axios from 'axios';
import { Button, Grid, Container, Typography } from '@mui/material';

const ApiButtons = ({ setApiResponse }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [prediction, setPrediction] = useState(false);
  const [resultImage, setResultImage] = useState(null);

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const openModal = () => {
    setPrediction(true);
  };

  const handleStatusButtonClick = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:8000/status');

      setApiResponse(response.data);
    } catch (error) {
      console.error('Error calling /status:', error);
    }
  };

  const handlePosesButtonClick = async () => {
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await axios.post('http://127.0.0.1:8000/poses', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        withCredentials: true,
        responseType: 'blob'
      });

      // Creamos una url para poder visualizar la imagen
      const imageUrl = URL.createObjectURL(new Blob([response.data]));

      setResultImage(imageUrl);
      setApiResponse(response.headers);
      console.log(response);

    } catch (error) {
      console.error('Error calling /poses:', error);
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
    </Container>
  );  
};

export default ApiButtons;