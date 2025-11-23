// src/auth/components/SocialLoginButtons.jsx
import React from 'react';
import { Stack, Button, Box } from '@mui/material';
import { SOCIAL_PROVIDERS } from '../authConfig';

/**
 * Renders buttons for social login providers.
 * The caller passes a handler that receives the provider key.
 */
const SocialLoginButtons = ({ onProviderClick }) => {
  const handleClick = (provider) => {
    if (onProviderClick) {
      onProviderClick(provider);
    }
  };

  return (
    <Stack spacing={1.5} sx={{ mt: 1 }}>
      <Button
        variant="outlined"
        fullWidth
        onClick={() => handleClick(SOCIAL_PROVIDERS.google)}
        startIcon={
          <Box
            sx={{
              width: 24,
              height: 24,
              borderRadius: '50%',
              border: '1px solid rgba(0,0,0,0.2)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 700,
              fontSize: 14,
            }}
          >
            G
          </Box>
        }
      >
        Continue with Google
      </Button>

      <Button
        variant="outlined"
        fullWidth
        onClick={() => handleClick(SOCIAL_PROVIDERS.microsoft)}
        startIcon={
          <Box
            sx={{
              width: 24,
              height: 24,
              display: 'grid',
              gridTemplateColumns: '1fr 1fr',
              gridTemplateRows: '1fr 1fr',
              gap: '1px',
            }}
          >
            <Box sx={{ bgcolor: 'primary.main', opacity: 0.9 }} />
            <Box sx={{ bgcolor: 'primary.main', opacity: 0.7 }} />
            <Box sx={{ bgcolor: 'primary.main', opacity: 0.7 }} />
            <Box sx={{ bgcolor: 'primary.main', opacity: 0.9 }} />
          </Box>
        }
      >
        Continue with Microsoft
      </Button>
    </Stack>
  );
};

export default SocialLoginButtons;
