// src/auth/pages/PasswordInvitePage.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import { Helmet } from 'react-helmet';
import { Typography } from '@mui/material';
import { NarrowPage } from '../../components/layout/PageLayout';
import PasswordSetForm from '../components/PasswordSetForm';
import { authApi } from '../authApi';

const PasswordInvitePage = () => {
  const { uid, token } = useParams();
  const location = useLocation();
  const navigate = useNavigate();

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [checked, setChecked] = useState(false);

  // Optional: andere Texte je nach „invite“ vs „reset“
  const isInvite = location.pathname.startsWith('/invite/');

  useEffect(() => {
    if (!uid || !token) {
      setError('This link is invalid.');
      setChecked(true);
      return;
    }

    const check = async () => {
      try {
        await authApi.verifyResetToken(uid, token);
        setChecked(true);
      } catch (err) {
        setError('This link is invalid or has expired.');
        setChecked(true);
      }
    };

    check();
  }, [uid, token]);

  const handleSubmit = async (newPassword) => {
    if (!uid || !token) {
      setError('This link is invalid.');
      return;
    }

    setSubmitting(true);
    setError('');
    setSuccessMessage('');

    try {
      await authApi.setNewPassword(uid, token, newPassword);
      setSuccessMessage(
        isInvite
          ? 'Password set successfully. You can now log in.'
          : 'Password changed successfully. You can now log in.',
      );
      navigate('/login');
    } catch (err) {
      setError(err.message || 'Could not set password.');
    } finally {
      setSubmitting(false);
    }
  };

  if (!checked && !error) {
    return (
      <NarrowPage title="Checking link…">
        <Typography>Validating your link…</Typography>
      </NarrowPage>
    );
  }

  return (
    <NarrowPage
      title={isInvite ? 'Welcome' : 'Reset password'}
      subtitle={
        isInvite
          ? 'Please choose a password to access your account.'
          : 'Please choose a new password.'
      }
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

      {!successMessage && !error && (
        <PasswordSetForm onSubmit={handleSubmit} submitting={submitting} />
      )}
    </NarrowPage>
  );
};

export default PasswordInvitePage;
