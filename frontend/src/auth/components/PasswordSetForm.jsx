// src/auth/components/PasswordSetForm.jsx
import React, { useState } from 'react';
import { Box, TextField, Button } from '@mui/material';

/**
 * Simple form to set a new password (once, with confirmation).
 * Caller reicht onSubmit(newPassword), kümmert sich um redirect / API call.
 */
const PasswordSetForm = ({ onSubmit, submitting = false }) => {
  const [password1, setPassword1] = useState('');
  const [password2, setPassword2] = useState('');
  const [localError, setLocalError] = useState('');

  const handleSubmit = (event) => {
    event.preventDefault();
    setLocalError('');

    if (!password1 || !password2) {
      setLocalError('Please enter the new password twice.');
      return;
    }

    if (password1 !== password2) {
      setLocalError('The passwords do not match.');
      return;
    }

    if (onSubmit) {
      onSubmit(password1);
    }
  };

  return (
    <Box
      component="form"
      onSubmit={handleSubmit}
      sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}
    >
      {localError && (
        <Box sx={{ colour: 'error.main', fontSize: 14 }}>
          {localError}
        </Box>
      )}

      <TextField
        label="New password"
        type="password"
        fullWidth
        autoComplete="new-password"
        value={password1}
        onChange={(e) => setPassword1(e.target.value)}
        disabled={submitting}
      />

      <TextField
        label="Confirm new password"
        type="password"
        fullWidth
        autoComplete="new-password"
        value={password2}
        onChange={(e) => setPassword2(e.target.value)}
        disabled={submitting}
      />

      <Button
        type="submit"
        variant="contained"
        disabled={submitting}
      >
        Set password
      </Button>
    </Box>
  );
};

export default PasswordSetForm;
