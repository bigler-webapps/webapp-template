// src/auth/components/PasswordResetRequestForm.jsx
import React, { useState } from 'react';
import { Box, TextField, Button } from '@mui/material';

const PasswordResetRequestForm = ({ onSubmit, submitting = false }) => {
  const [email, setEmail] = useState('');

  const handleSubmit = (event) => {
    event.preventDefault();
    if (onSubmit) {
      onSubmit(email);
    }
  };

  return (
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
        disabled={submitting}
      />
      <Button
        type="submit"
        variant="contained"
        disabled={submitting}
      >
        Send reset link
      </Button>
    </Box>
  );
};

export default PasswordResetRequestForm;
