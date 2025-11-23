// src/auth/pages/PasswordInvitePage.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Helmet } from 'react-helmet';
import { Typography } from '@mui/material';
import { NarrowPage } from '../../components/layout/PageLayout';
import PasswordSetForm from '../components/PasswordSetForm';
import { resetPasswordWithKey } from '../authApi';

const PasswordInvitePage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const key = searchParams.get('key');

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    if (!key) {
      setError('This link is invalid or missing the key parameter.');
    }
  }, [key]);

  const handleSubmit = async (newPassword) => {
    if (!key) {
      setError('This link is invalid.');
      return;
    }

    setSubmitting(true);
    setError('');
    setSuccessMessage('');

    try {
      await resetPasswordWithKey(key, newPassword);
      setSuccessMessage('Password set successfully. You can now log in.');

      // Optional: direkt nach Login umleiten
      navigate('/login');
    } catch (err) {
      setError(err.message || 'Could not set password.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <NarrowPage
      title="Welcome"
      subtitle="Please choose a password to access your account."
    >
      <Helmet>
        <title>PROJECT_NAME – Set password</title>
      </Helmet>

      {error && (
        <Typography color="error" gutterBottom>
          {error}
        </Typography>
      )}

      {successMessage && (
        <Typography color="primary" gutterBottom>
          {successMessage}
        </Typography>
      )}

      <PasswordSetForm
        onSubmit={handleSubmit}
        submitting={submitting}
      />
    </NarrowPage>
  );
};

export default PasswordInvitePage;
