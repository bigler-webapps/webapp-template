// src/pages/LoginPage.jsx
import React, { useState, useContext } from 'react';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';
import { AuthContext } from '../AuthContext';
import {
  Box,
  TextField,
  Button,
  Typography,
} from '@mui/material';
import { Helmet } from 'react-helmet';
import { NarrowPage } from '../components/layout/PageLayout';

// Renders login form and starts authenticated session on success
const LoginPage = () => {
  const navigate = useNavigate();
  const { login } = useContext(AuthContext);

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleLogin = async (event) => {
    event.preventDefault();
    setError('');

    try {
      const res = await axios.post('/api/users/login/', {
        username,
        password,
      });

      login(res.data);

      if (res.data.is_new_user) {
        navigate('/welcome');
      } else {
        navigate('/');
      }
    } catch (err) {
      setError('Login failed: ' + (err.response?.data?.detail || err.message));
    }
  };

  return (
    <NarrowPage title="Login">
      <Helmet>
        <title>PROJECT_NAME – Login</title>
      </Helmet>

      {error && (
        <Typography color="error" gutterBottom>
          {error}
        </Typography>
      )}

      <Box
        component="form"
        onSubmit={handleLogin}
        sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}
      >
        <TextField
          label="Email address"
          type="email"
          required
          fullWidth
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <TextField
          label="Password"
          type="password"
          required
          fullWidth
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            mt: 1,
          }}
        >
          <Button type="submit" variant="contained">
            Login
          </Button>
          <Button
            component={Link}
            to="/reset-request-password"
            variant="text"
          >
            Forgot password?
          </Button>
        </Box>
      </Box>
    </NarrowPage>
  );
};

export default LoginPage;
