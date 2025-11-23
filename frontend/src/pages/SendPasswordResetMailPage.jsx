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
      // allauth-headless: Passwort-Reset anstossen
      const res = await axios.post(
        '/_allauth/auth/password/reset/',
        { email },
        { withCredentials: true },
      );

      // allauth liefert je nach Konfiguration kaum Details zurück,
      // daher lieber eine generische Erfolgsmeldung anzeigen.
      const detail =
        res.data?.detail ||
        'If an account with that email exists, a reset link has been sent.';

      setMessage(detail);
    } catch (err) {
      const detail =
        err.response?.data?.detail ||
        err.response?.data?.non_field_errors?.join(' ') ||
        'Error sending reset email.';
      setError(detail);
    }
  };

  return (
    <NarrowPage title="Reset password">
      <Helmet>
        <title>PROJECT_NAME – Reset password</title>
      </Helmet>

      {message && (
        <Typography color="primary" gutterBottom>
          {message}
        </Typography>
      )}
      {error && (
        <Typography color="error" gutterBottom>
          {error}
        </Typography>
      )}

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
