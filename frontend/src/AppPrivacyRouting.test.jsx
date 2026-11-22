import React from 'react';
import { cleanup, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';

const wiring = vi.hoisted(() => ({ api: {}, options: null }));
vi.mock('@micha.bigler/ui-core-micha', () => ({
  createPrivacyApi: (_config, options) => { wiring.options = options; return wiring.api; },
  AuthProvider: ({ children }) => <>{children}</>,
  PrivacyProvider: ({ api, children }) => <div data-testid="privacy-provider" data-api={api === wiring.api}>{children}</div>,
  PrivacyBanner: () => <div>Privacy banner</div>,
  LoginPage: () => <div>Login</div>,
  SignUpPage: () => <div>Signup</div>,
  SignupConfirmPage: () => <div>Confirm signup</div>,
  PasswordResetRequestPage: () => <div>Request password reset</div>,
  PasswordInvitePage: () => <div>Password invite or reset</div>,
}));
vi.mock('./components/Header', () => ({ default: () => null }));
vi.mock('./components/RequireAuth', () => ({ default: ({ children }) => children }));
vi.mock('./pages/AccountHubPage', () => ({ default: () => null }));
vi.mock('./pages/Home', () => ({ default: () => <div>Home</div> }));
vi.mock('./pages/WelcomePage', () => ({ default: () => null }));
import App from './App';

afterEach(cleanup);
describe('privacy and password routes', () => {
  it.each([
    ['/reset-request-password', 'Request password reset'],
    ['/reset/synthetic/token', 'Password invite or reset'],
    ['/invite/synthetic/token', 'Password invite or reset'],
  ])('renders the banner and %s in the configured privacy provider', (path, page) => {
    window.history.pushState({}, '', path);
    render(<App />);
    expect(wiring.options).toEqual({ apiBase: '/api/privacy/', csrfUrl: '/api/csrf/' });
    expect(screen.getByTestId('privacy-provider').getAttribute('data-api')).toBe('true');
    expect(screen.getByTestId('privacy-provider').contains(screen.getByText('Privacy banner'))).toBe(true);
    expect(screen.getByText(page)).toBeTruthy();
    expect(window.location.pathname).toBe(path);
  });
});
