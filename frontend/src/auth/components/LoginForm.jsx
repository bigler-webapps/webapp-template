// src/auth/components/LoginForm.jsx
import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  Divider,
} from '@mui/material';
import SocialLoginButtons from './SocialLoginButtons';

const LoginForm = ({
  onSubmit,
  onForgotPassword,
  onSocialLogin,
  error,
  disabled = false,
}) => {
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (event) => {
    event.preventDefault();
    if (!onSubmit) return;
    onSubmit({ identifier, password });
  };

  return (
    <Box
      component="form"
      onSubmit={handleSubmit}
      sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}
    >
      {error && (
        <Typography color="error" gutterBottom>
          {error}
        </Typography>
      )}

      <TextField
        label="Email address"
        type="email"
        required
        fullWidth
        value={identifier}
        onChange={(e) => setIdentifier(e.target.value)}
        disabled={disabled}
      />

      <TextField
        label="Password"
        type="password"
        required
        fullWidth
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        disabled={disabled}
      />

      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          mt: 1,
        }}
      >
        <Button
          type="submit"
          variant="contained"
          disabled={disabled}
        >
          Login
        </Button>

        <Button
          type="button"
          variant="text"
          onClick={onForgotPassword}
          disabled={disabled}
        >
          Forgot password?
        </Button>
      </Box>

      <Divider sx={{ my: 2 }}>or</Divider>

      <SocialLoginButtons onProviderClick={onSocialLogin} />
    </Box>
  );
};

export default LoginForm;
