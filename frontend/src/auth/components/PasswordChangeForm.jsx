import React, { useState } from 'react';
import { Box, TextField, Button, Stack } from '@mui/material';

/**
 * A simplified form to handle password changes.
 * Does not require password confirmation.
 */
const PasswordChangeForm = ({ onSubmit }) => {
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!onSubmit) return;

    setSubmitting(true);
    try {
      // Send the current and new password to the parent component
      await onSubmit(currentPassword, newPassword);
      // Reset form fields on success
      setCurrentPassword('');
      setNewPassword('');
    } catch (err) {
      // Errors are generally handled by the parent
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ maxWidth: 500 }}>
      <Stack spacing={2}>
        <TextField
          label="Current Password"
          type="password"
          value={currentPassword}
          onChange={(e) => setCurrentPassword(e.target.value)}
          required
          fullWidth
          disabled={submitting}
        />
        <TextField
          label="New Password"
          type="password"
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
          required
          fullWidth
          disabled={submitting}
        />
        <Box>
          <Button 
            type="submit" 
            variant="contained" 
            disabled={submitting}
          >
            {submitting ? 'Changing...' : 'Change Password'}
          </Button>
        </Box>
      </Stack>
    </Box>
  );
};

export default PasswordChangeForm;