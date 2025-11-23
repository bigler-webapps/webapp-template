import React, { useState } from 'react';
import {
  Box,
  Typography,
  Divider,
  Button,
  Stack,
  Alert,
} from '@mui/material';
import PasswordChangeForm from './PasswordChangeForm';
import SocialLoginButtons from './SocialLoginButtons';
import { authApi } from '../authApi'; 

const SecurityComponent = () => {
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleSocialClick = async (provider) => {
    setMessage('');
    setError('');
    try {
      // FIX: Await the async function to catch network errors
      await authApi.startSocialLogin(provider);
    } catch (e) {
      setError(e.message || 'Social login could not be started.');
    }
  };

  const handlePasswordChange = async (currentPassword, newPassword) => {
    setMessage('');
    setError('');
    try {
      await authApi.changePassword(currentPassword, newPassword);
      setMessage('Password changed successfully.');
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 
                       err.message || 
                       'Could not change password.';
      setError(errorMsg);
    }
  };

  return (
    <Box>
      {message && (
        <Alert severity="success" sx={{ mb: 2 }}>
          {message}
        </Alert>
      )}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Password Change Section */}
      <Typography variant="h6" gutterBottom>
        Password
      </Typography>
      
      <PasswordChangeForm onSubmit={handlePasswordChange} />
      
      <Divider sx={{ my: 3 }} />

      {/* Social Logins Section */}
      <Typography variant="h6" gutterBottom>
        Social logins
      </Typography>
      <Typography variant="body2" sx={{ mb: 1 }}>
        Sign in using a connected Google or Microsoft account.
      </Typography>
      <SocialLoginButtons onProviderClick={handleSocialClick} />

      <Divider sx={{ my: 3 }} />

      {/* Passkeys Section (Placeholder) */}
      <Typography variant="h6" gutterBottom>
        Passkeys (coming soon)
      </Typography>
      <Typography variant="body2" sx={{ mb: 1 }}>
        Use passkeys for passwordless sign-in. This section will be active once
        WebAuthn endpoints are wired in the backend.
      </Typography>
      <Stack direction="row" spacing={2}>
        <Button
          variant="outlined"
          disabled
        >
          Add passkey
        </Button>
      </Stack>
    </Box>
  );
};

export default SecurityComponent;