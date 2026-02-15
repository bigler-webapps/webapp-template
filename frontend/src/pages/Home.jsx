// src/pages/Home.jsx
import React from 'react';
import { Helmet } from 'react-helmet';
import { Typography, Box } from '@mui/material';
import { WidePage } from '@micha.bigler/ui-core-micha';

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
    </WidePage>
  );
};

export default Home;
