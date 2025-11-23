// src/components/ProfileComponent.jsx
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import {
  Box,
  Stack,
  TextField,
  FormControlLabel,
  Checkbox,
  Button,
  CircularProgress,
  Alert,
  Typography,
} from '@mui/material';
import { USERS_BASE } from '../authConfig';

/**
 * ProfileComponent
 *
 * - Lädt das aktuelle User-Objekt von `${USERS_BASE}/current/`
 * - Zeigt Basisfelder (Name, E-Mail, etc.)
 * - Optional Privacy/Cookie-Checkboxen
 * - Ruft onSubmit(payload) auf, um Änderungen zu speichern
 */
const ProfileComponent = ({
  onLoad,
  onSubmit,
  submitText = 'Save',
  showName = true,
  showPrivacy = true,
  showCookies = true,
}) => {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [userId, setUserId] = useState(null);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');

  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');

  const [acceptedPrivacy, setAcceptedPrivacy] = useState(false);
  const [acceptedCookies, setAcceptedCookies] = useState(false);

  // Load current user on mount
  useEffect(() => {
    let mounted = true;

    const loadUser = async () => {
      setLoading(true);
      setError('');
      try {
        const res = await axios.get(`${USERS_BASE}/current/`, {
          withCredentials: true,
        });
        if (!mounted) return;

        const data = res.data;
        setUserId(data.id ?? null);
        setUsername(data.username ?? '');
        setEmail(data.email ?? '');
        setFirstName(data.first_name ?? '');
        setLastName(data.last_name ?? '');
        setAcceptedPrivacy(Boolean(data.accepted_privacy_statement));
        setAcceptedCookies(Boolean(data.accepted_convenience_cookies));

        if (onLoad) {
          onLoad(data);
        }
      } catch (err) {
        if (!mounted) return;
        setError(
          err.response?.data?.detail ||
            err.message ||
            'Unable to load profile.',
        );
      } finally {
        if (mounted) setLoading(false);
      }
    };

    loadUser();
    return () => {
      mounted = false;
    };
  }, [onLoad]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!onSubmit) return;

    setSaving(true);
    setError('');
    setSuccess('');

    const payload = {
      first_name: firstName,
      last_name: lastName,
      // Die Serializer-Felder sind flach, werden aber über `source="profile.*"`
      // ins Profil gemappt.
      accepted_privacy_statement: acceptedPrivacy,
      accepted_convenience_cookies: acceptedCookies,
    };

    try {
      await onSubmit(payload);
      setSuccess('Profile updated successfully.');
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          err.message ||
          'Error while saving profile.',
      );
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box
      component="form"
      onSubmit={handleSubmit}
      sx={{ maxWidth: 600, display: 'flex', flexDirection: 'column', gap: 2 }}
    >
      {error && (
        <Alert severity="error">
          {error}
        </Alert>
      )}
      {success && (
        <Alert severity="success">
          {success}
        </Alert>
      )}

      {/* Basisdaten (immer sichtbar, E-Mail / Username meist read-only) */}
      <Stack spacing={2}>
        <TextField
          label="Username"
          value={username}
          fullWidth
          disabled
        />
        <TextField
          label="Email"
          type="email"
          value={email}
          fullWidth
          disabled
        />
      </Stack>

      {/* Name nur, wenn showName == true */}
      {showName && (
        <Stack spacing={2} direction={{ xs: 'column', sm: 'row' }}>
          <TextField
            label="First name"
            value={firstName}
            onChange={(e) => setFirstName(e.target.value)}
            fullWidth
          />
          <TextField
            label="Last name"
            value={lastName}
            onChange={(e) => setLastName(e.target.value)}
            fullWidth
          />
        </Stack>
      )}

      {/* Privacy/Cookies */}
      {(showPrivacy || showCookies) && (
        <Box sx={{ mt: 1 }}>
          <Typography variant="subtitle1" gutterBottom>
            Privacy and cookies
          </Typography>

          <Stack spacing={1}>
            {showPrivacy && (
              <FormControlLabel
                control={
                  <Checkbox
                    checked={acceptedPrivacy}
                    onChange={(e) => setAcceptedPrivacy(e.target.checked)}
                  />
                }
                label="I agree with the privacy statement."
              />
            )}

            {showCookies && (
              <FormControlLabel
                control={
                  <Checkbox
                    checked={acceptedCookies}
                    onChange={(e) => setAcceptedCookies(e.target.checked)}
                  />
                }
                label="I allow convenience cookies."
              />
            )}
          </Stack>
        </Box>
      )}

      <Box sx={{ mt: 2 }}>
        <Button
          type="submit"
          variant="contained"
          disabled={saving}
        >
          {saving ? 'Saving…' : submitText}
        </Button>
      </Box>
    </Box>
  );
};

export default ProfileComponent;
