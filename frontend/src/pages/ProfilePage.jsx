// src/pages/ProfilePage.jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import ProfileComponent from '../components/ProfileComponent';
import { Helmet } from 'react-helmet';
import {
  Button,
  Stack,
  Alert,
  Divider,
} from '@mui/material';
import { WidePage } from '../components/layout/PageLayout';

// Renders the profile page with user data and actions
const ProfilePage = () => {
  const [userData, setUserData] = useState(null);
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  const handleLoad = (data) => setUserData(data);

  const handleSave = (payload) =>
    axios.patch('/api/users/current/', payload, { withCredentials: true });

  const handlePasswordChange = () => navigate('/reset-request-password');

  const handleDelete = () => {
    if (!window.confirm('Are you sure you want to delete your profile?')) return;
    if (!userData) return;

    axios
      .delete(`/api/users/${userData.id}/`, { withCredentials: true })
      .then(() => navigate('/login'))
      .catch((err) => {
        console.error('Error deleting profile:', err);
        setMessage('Error deleting profile.');
      });
  };

  const handleDownload = () => {
    if (!userData) return;
    const blob = new Blob([JSON.stringify(userData, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'profile.json';
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  };

  return (
    <WidePage title="Profile">
      <Helmet>
        <title>PROJECT_NAME – Profile</title>
      </Helmet>

      {message && (
        <Alert severity="info" sx={{ mb: 2 }}>
          {message}
        </Alert>
      )}

      <ProfileComponent
        onLoad={handleLoad}
        onSubmit={handleSave}
        submitText="Save"
        showName
        showPrivacy
        showCookies
      />

      <Divider sx={{ my: 3 }} />

      <Stack direction="row" spacing={2}>
        <Button variant="contained" onClick={handlePasswordChange}>
          Change password
        </Button>
        <Button variant="contained" onClick={handleDownload}>
          Download user data
        </Button>
        <Button
          variant="contained"
          color="error"
          onClick={handleDelete}
        >
          Delete profile
        </Button>
      </Stack>
    </WidePage>
  );
};

export default ProfilePage;
