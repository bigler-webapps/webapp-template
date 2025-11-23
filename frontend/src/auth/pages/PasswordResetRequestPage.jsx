// src/auth/pages/PasswordResetRequestPage.jsx
import React, { useState } from 'react';
import { Helmet } from 'react-helmet';
import { Typography } from '@mui/material';
import { NarrowPage } from '../../components/layout/PageLayout';
import { requestPasswordReset } from '../authApi';
import PasswordResetRequestForm from '../components/PasswordResetRequestForm';

const PasswordResetRequestPage = () => {
  const [submitting, setSubmitting] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (email) => {
    setSuccessMessage('');
    setError('');
    if (!email) {
      setError('Please enter an email address.');
      return;
    }

    setSubmitting(true);
    try {
      await requestPasswordReset(email);
      setSuccessMessage(
        'If an account exists for this address, a reset email has been sent.'
      );
    } catch (err) {
      setError(err.message || 'Could not send reset email.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <NarrowPage title="Reset password">
      <Helmet>
        <title>PROJECT_NAME – Reset password</title>
      </Helmet>

      {successMessage && (
        <Typography colour="primary" gutterBottom>
          {successMessage}
        </Typography>
      )}

      {error && (
        <Typography colour="error" gutterBottom>
          {error}
        </Typography>
      )}

      <PasswordResetRequestForm
        onSubmit={handleSubmit}
        submitting={submitting}
      />
    </NarrowPage>
  );
};

export default PasswordResetRequestPage;
