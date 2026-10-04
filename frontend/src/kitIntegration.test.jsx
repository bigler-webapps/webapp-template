import React from 'react';

import { ThemeProvider } from '@mui/material';
import { AuthProvider, checkKitIntegration } from '@micha.bigler/ui-core-micha';
import { describe, expect, it } from 'vitest';

import i18n from '../i18n/index.js';
import theme from './theme';

// The template's own providers, as mounted in src/index.jsx and src/App.jsx.
function AppProviders({ children }) {
  return (
    <ThemeProvider theme={theme}>
      <AuthProvider>{children}</AuthProvider>
    </ThemeProvider>
  );
}

describe('kit integration', () => {
  // Keep this check alone in its file: it stubs the kit's shared apiClient
  // transport for its duration.
  it('has no findings with the template i18n and providers', async () => {
    globalThis.IS_REACT_ACT_ENVIRONMENT = true;

    const { findings } = await checkKitIntegration({ i18n, wrapper: AppProviders });

    expect(findings).toEqual([]);
  });
});
