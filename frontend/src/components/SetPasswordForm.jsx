// src/components/SetPasswordForm.jsx
import React, { useEffect, useState } from 'react';
import { Box, TextField, Button, Typography } from '@mui/material';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

// Renders form to set a new password, optionally validating link before use
const SetPasswordForm = ({
  endpoint,
  title,
  onSuccessRedirect = '/login',
  validateLink = true,
}) => {
  const navigate = useNavigate();
  const [password, setPassword] = useState('');
  const [linkValid, setLinkValid] = useState(!validateLink);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');

  // Optionally validates the reset link by sending GET to backend
  useEffect(() => {
    if (!validateLink) return;
    axios
      .get(endpoint)
      .then(() => setLinkValid(true))
      .catch(() => {
        setError('Reset link is invalid or has expired.');
        setLinkValid(false);
      });
  }, [endpoint, validateLink]);

  // Sends new password to backend
  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setMessage('');

    try {
      await axios.post(endpoint, { new_password: password });
      setMessage('Password updated successfully.');
      navigate(onSuccessRedirect);
    } catch (err) {
      setError(
        err.response?.data?.detail || 'Could not update password. Please try again.',
      );
    }
  };

  if (!linkValid) {
    return <Typography color="error">{error}</Typography>;
  }

  return (
    <Box
      component="form"
      onSubmit={handleSubmit}
      sx={{ display: 'flex', flexDirection: 'column', gap: 2, maxWidth: 400 }}
    >
      <Typography variant="h6">{title}</Typography>
      {error && <Typography color="error">{error}</Typography>}
      {message && <Typography color="primary">{message}</Typography>}

      <TextField
        label="New password"
        type="password"
        required
        fullWidth
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />

      <Button type="submit" variant="contained">
        Save password
      </Button>
    </Box>
  );
};

export default SetPasswordForm;
