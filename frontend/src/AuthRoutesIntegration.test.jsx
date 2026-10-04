import React from 'react';

import { ThemeProvider } from '@mui/material';
import { render, waitFor } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

import App from './App';
import './i18n';
import theme from './theme';

const { axiosInstance } = vi.hoisted(() => ({
  axiosInstance: {
    delete: vi.fn().mockResolvedValue({ data: {} }),
    get: vi.fn().mockResolvedValue({ data: {} }),
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() },
    },
    patch: vi.fn().mockResolvedValue({ data: {} }),
    post: vi.fn().mockResolvedValue({ data: {} }),
    put: vi.fn().mockResolvedValue({ data: {} }),
  },
}));

// Only the network is mocked; the kit pages themselves are real.
vi.mock('axios', () => ({
  default: {
    create: vi.fn(() => axiosInstance),
  },
}));

vi.mock('./components/Header', () => ({ default: () => null }));

describe('auth route integration with ui-core-micha', () => {
  // A bare "does not throw" would also pass with the pages stubbed to null;
  // a mounted <form> proves the real kit page rendered.
  it.each([
    ['/signup', 'self-registration'],
    ['/invite/some-uid/some-token', 'password invite'],
  ])('renders the %s route real kit form (%s)', async (path) => {
    window.history.pushState({}, '', path);

    const { container } = render(
      <ThemeProvider theme={theme}>
        <App />
      </ThemeProvider>,
    );

    await waitFor(() => expect(container.querySelector('form')).not.toBeNull());
    // LoginPage also renders a form: staying on the requested path proves the
    // route was not redirected to /login.
    expect(window.location.pathname).toBe(path);
  });
});
