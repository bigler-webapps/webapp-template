// src/auth/components/PasswordChangeForm.jsx
import React, { useState } from 'react';
import { Box, TextField, Button } from '@mui/material';

const PasswordChangeForm = ({ onSubmit, submitting = false }) => {
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword1, setNewPassword1] = useState('');
  const [newPassword2, setNewPassword2] = useState('');
  const [localError, setLocalError] = useState('');

  const handleSubmit = (event) => {
    event.preventDefault();
    setLocalError('');

    if (!newPassword1 || !newPassword2) {
      setLocalError('Please enter the new password twice.');
      return;
    }

    if (newPassword1 !== newPassword2) {
      setLocalError('The new passwords do not match.');
      return;
    }

    if (onSubmit) {
      onSubmit(oldPassword, newPassword1);
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
        label="Current password"
        type="password"
        fullWidth
        autoComplete="current-password"
        value={oldPassword}
        onChange={(e) => setOldPassword(e.target.value)}
        disabled={submitting}
      />

      <TextField
        label="New password"
        type="password"
        fullWidth
        autoComplete="new-password"
        value={newPassword1}
        onChange={(e) => setNewPassword1(e.target.value)}
        disabled={submitting}
      />

      <TextField
        label="Confirm new password"
        type="password"
        fullWidth
        autoComplete="new-password"
        value={newPassword2}
        onChange={(e) => setNewPassword2(e.target.value)}
        disabled={submitting}
      />

      <Button
        type="submit"
        variant="contained"
        disabled={submitting}
      >
        Change password
      </Button>
    </Box>
  );
};

export default PasswordChangeForm;
