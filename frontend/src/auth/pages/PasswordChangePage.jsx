// src/auth/pages/PasswordChangePage.jsx
import React, { useState } from 'react';
import { Helmet } from 'react-helmet';
import { Typography } from '@mui/material';
import { NarrowPage } from '../../components/layout/PageLayout';
import PasswordChangeForm from '../components/PasswordChangeForm';
import { changePassword } from '../authApi';

const PasswordChangePage = () => {
  const [submitting, setSubmitting] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (oldPassword, newPassword) => {
    setSuccessMessage('');
    setError('');
    setSubmitting(true);

    try {
      await changePassword(oldPassword, newPassword);
      setSuccessMessage('Password changed successfully.');
    } catch (err) {
      setError(err.message || 'Could not change password.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <NarrowPage
      title="Change password"
      subtitle="Enter your current password and a new password."
    >
      <Helmet>
        <title>PROJECT_NAME – Change password</title>
      </Helmet>

      {successMessage && (
        <Typography color="primary" gutterBottom>
          {successMessage}
        </Typography>
      )}

      {error && (
        <Typography color="error" gutterBottom>
          {error}
        </Typography>
      )}

      <PasswordChangeForm
        onSubmit={handleSubmit}
        submitting={submitting}
      />
    </NarrowPage>
  );
};

export default PasswordChangePage;
