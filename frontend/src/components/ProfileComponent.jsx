// src/components/ProfileComponent.jsx
import React, { useEffect, useState } from 'react';
import {
  Box,
  TextField,
  FormControlLabel,
  Checkbox,
  Button,
} from '@mui/material';
import axios from 'axios';

// Renders profile form that can load and update current user data
const ProfileComponent = ({
  onLoad,
  onSubmit,
  submitText = 'Save',
  showName = false,
  showPrivacy = false,
  showCookies = false,
}) => {
  const [formData, setFormData] = useState({
    email: '',
    first_name: '',
    last_name: '',
    role: 'none',
    accepted_privacy_statement: false,
    accepted_convenience_cookies: false,
  });

  const [loading, setLoading] = useState(true);

  // Loads current user profile once on mount
  useEffect(() => {
    axios
      .get('/api/users/current/')
      .then((res) => {
        setFormData((prev) => ({
          ...prev,
          ...res.data,
        }));
        if (onLoad) {
          onLoad(res.data);
        }
      })
      .catch(() => {
        // optional error handling
      })
      .finally(() => setLoading(false));
  }, []); // no dependency on onLoad to avoid loops

  // Updates local form state on field change
  const handleChange = (field) => (event) => {
    const value =
      event.target.type === 'checkbox'
        ? event.target.checked
        : event.target.value;
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  // Submits form data to parent handler
  const handleSubmit = (event) => {
    event.preventDefault();
    if (onSubmit) {
      const payload = {
        email: formData.email,
        first_name: formData.first_name,
        last_name: formData.last_name,
        role: formData.role,
        accepted_privacy_statement: formData.accepted_privacy_statement,
        accepted_convenience_cookies: formData.accepted_convenience_cookies,
        is_new: false,
      };
      onSubmit(payload);
    }
  };

  if (loading) {
    return <div>Loading profile...</div>;
  }

  return (
    <Box
      component="form"
      onSubmit={handleSubmit}
      sx={{ display: 'flex', flexDirection: 'column', gap: 2, maxWidth: 500 }}
    >
      <TextField
        label="Email"
        type="email"
        fullWidth
        value={formData.email || ''}
        onChange={handleChange('email')}
      />

      {showName && (
        <>
          <TextField
            label="First name"
            fullWidth
            value={formData.first_name || ''}
            onChange={handleChange('first_name')}
          />
          <TextField
            label="Last name"
            fullWidth
            value={formData.last_name || ''}
            onChange={handleChange('last_name')}
          />
        </>
      )}

      {showPrivacy && (
        <FormControlLabel
          control={
            <Checkbox
              checked={!!formData.accepted_privacy_statement}
              onChange={handleChange('accepted_privacy_statement')}
            />
          }
          label="I accept the privacy statement"
        />
      )}

      {showCookies && (
        <FormControlLabel
          control={
            <Checkbox
              checked={!!formData.accepted_convenience_cookies}
              onChange={handleChange('accepted_convenience_cookies')}
            />
          }
          label="I accept convenience cookies"
        />
      )}

      <Button type="submit" variant="contained">
        {submitText}
      </Button>
    </Box>
  );
};

export default ProfileComponent;
