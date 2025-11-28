// src/pages/WelcomePage.jsx
import React from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { ProfileComponent } from '@michabigler/ui-core';
import { Helmet } from 'react-helmet';
import { Typography, Box } from '@mui/material';
import { WidePage } from '@michabigler/ui-core';

// Renders onboarding page for new users to complete their profile
const WelcomePage = () => {
  const navigate = useNavigate();

  const handleWelcomeSubmit = (payload) =>
    axios
      .patch('/api/users/current/', payload, { withCredentials: true })
      .then(() => {
        if (payload.accepted_convenience_cookies) {
          document.cookie =
            'convenience_cookies=true;path=/;max-age=31536000';
        }
        navigate('/');
      });

  return (
    <WidePage title="Welcome to PROJECT_NAME">
      <Helmet>
        <title>Welcome to PROJECT_NAME</title>
      </Helmet>

      <Typography paragraph>
        Please complete your profile and accept the policies.
      </Typography>

      <Box mt={2}>
        <ProfileComponent
          submitText="Continue"
          onSubmit={handleWelcomeSubmit}
          showName
          showPrivacy
          showCookies
        />
      </Box>
    </WidePage>
  );
};

export default WelcomePage;
