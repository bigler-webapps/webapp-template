// src/components/UserInviteTab.jsx
import React, { useState } from 'react';
import axios from 'axios';
import {
  Box,
  TextField,
  Button,
  Typography,
} from '@mui/material';

const UserInviteTab = () => {
  const [inviteEmail, setInviteEmail] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const inviteUser = async () => {
    setMessage('');
    setError('');
    if (!inviteEmail) return;

    try {
      const { data } = await axios.post(
        '/api/users/invite/',
        { email: inviteEmail },
        { withCredentials: true },
      );
      setInviteEmail('');
      setMessage(
        data?.detail || 'Invitation sent.',
      );
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error('Error inviting user:', err);
      setError(
        err.response?.data?.detail || err.message || 'Error inviting user',
      );
    }
  };

  return (
    <Box sx={{ maxWidth: 600 }}>
      <Typography variant="h6" gutterBottom>
        Invite a new user
      </Typography>

      {message && (
        <Typography sx={{ mb: 1 }} color="primary">
          {message}
        </Typography>
      )}
      {error && (
        <Typography sx={{ mb: 1 }} color="error">
          {error}
        </Typography>
      )}

      <Box
        sx={{
          display: 'flex',
          gap: 2,
          alignItems: 'center',
        }}
      >
        <TextField
          label="Enter email"
          type="email"
          variant="outlined"
          fullWidth
          value={inviteEmail}
          onChange={(e) => setInviteEmail(e.target.value)}
        />
        <Button variant="contained" onClick={inviteUser}>
          Invite user
        </Button>
      </Box>
    </Box>
  );
};

export default UserInviteTab;
