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
    setError('');
    try {
      authApi.startSocialLogin(providerKey);
    } catch (err) {
      // This will only fire on immediate client-side errors
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
        error={undefined}
        disabled={submitting}
      />
    </NarrowPage>
  );
};

export default LoginPage;