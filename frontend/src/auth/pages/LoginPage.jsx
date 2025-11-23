// src/auth/pages/LoginPage.jsx
import React, { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { Helmet } from 'react-helmet';
import { Typography } from '@mui/material';
import { NarrowPage } from '../../components/layout/PageLayout';
import { AuthContext } from '../AuthContext';
import { authApi } from '../authApi';
import LoginForm from '../components/LoginForm';

const LoginPage = () => {
  const navigate = useNavigate();
  const { login } = useContext(AuthContext);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async ({ identifier, password }) => {
    setError('');
    setSubmitting(true);
    try {
      // FIX: Pass identifier and password as separate arguments, not as an object
      const data = await authApi.loginWithPassword(identifier, password);
      login(data.user);
      navigate('/');
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          err?.message ||
          'Login failed.',
      );
    } finally {
      setSubmitting(false);
    }
  };

  const handleForgotPassword = () => {
    navigate('/reset-request-password');
  };

  const handleSocialLogin = (providerKey) => {
    // Call the function that handles the redirect via window.location.href
    try {
      authApi.startSocialLogin(providerKey);
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error('Social login init failed', err);
      setError('Could not start social login.');
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

      <LoginForm
        onSubmit={handleSubmit}
        onForgotPassword={handleForgotPassword}
        onSocialLogin={handleSocialLogin}
        error={undefined}              // Error schon oben gerendert
        disabled={submitting}
      />
    </NarrowPage>
  );
};

export default LoginPage;
