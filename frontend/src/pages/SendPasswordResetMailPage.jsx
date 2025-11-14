// src/pages/SendPasswordResetMailPage.jsx
import React, { useState } from 'react';
import axios from 'axios';
import {
  Box,
  TextField,
  Button,
  Typography,
} from '@mui/material';
import { Helmet } from 'react-helmet';
import { NarrowPage } from '../components/layout/PageLayout';

// Renders form to request a password reset email
const SendPasswordResetMailPage = () => {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault();
    setMessage('');
    setError('');
    try {
      const res = await axios.post(
        '/api/users/reset-request/',
        { email },
        { withCredentials: true },
      );
      setMessage(res.data.detail || 'Reset email sent.');
    } catch (err) {
      setError(err.response?.data?.detail || 'Error sending reset email.');
    }
  };

  return (
    <NarrowPage title="Reset password">
      <Helmet>
        <title>PROJECT_NAME – Reset password</title>
      </Helmet>

      {message && <Typography color="primary">{message}</Typography>}
      {error && <Typography color="error">{error}</Typography>}

      <Box
        component="form"
        onSubmit={handleSubmit}
        sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}
      >
        <TextField
          label="Email address"
          type="email"
          required
          fullWidth
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <Button type="submit" variant="contained">
          Send reset link
        </Button>
      </Box>
    </NarrowPage>
  );
};

export default SendPasswordResetMailPage;
