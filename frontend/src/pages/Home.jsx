// src/pages/Home.jsx
import React from 'react';
import { Helmet } from 'react-helmet';
import { Typography, Box } from '@mui/material';
import { WidePage } from '@michabigler/ui-core';

// Renders the main landing page of the application
const Home = () => {
  return (
    <WidePage title="PROJECT_NAME">
      <Helmet>
        <title>PROJECT_NAME – Home</title>
      </Helmet>

      <Typography paragraph>
        This is the home page of the application.
      </Typography>

      <Box
        mt={4}
        sx={{
          display: 'flex',
          justifyContent: 'center',
        }}
      >
        <Box
          component="img"
          // gerne erstmal absolut, um Base-URL-Probleme auszuschliessen
          src="http://127.0.0.1:8125/media/Activity_Line.png"
          alt="Activity line test"
          sx={{
            width: 300,        // feste Breite, damit es nicht „wegschrumpft“
            height: 'auto',
            borderRadius: 1,
            border: '1px solid #ccc',
          }}
        />
      </Box>
    </WidePage>
  );
};

export default Home;
