import React from 'react';
import { render, screen } from '@testing-library/react';

import App from './App';

jest.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (_key, fallback) => fallback || _key,
    i18n: {
      resolvedLanguage: 'de',
      changeLanguage: jest.fn(),
    },
  }),
}));

jest.mock('@micha.bigler/ui-core-micha', () => {
  const React = require('react');

  return {
    AuthContext: React.createContext({
      user: null,
      login: jest.fn(),
      logout: jest.fn(),
    }),
    AuthProvider: ({ children }) => <>{children}</>,
    LoginPage: () => <div>Login Page</div>,
    PasswordInvitePage: () => <div>Invite Page</div>,
    PasswordResetRequestPage: () => <div>Reset Request Page</div>,
    SignUpPage: () => <div>Signup Page</div>,
    AccountPage: () => <div>Account Page</div>,
    ProfileComponent: () => <div>Profile Component</div>,
    WidePage: ({ children, title }) => (
      <div>
        <h1>{title}</h1>
        {children}
      </div>
    ),
    updateUserProfile: jest.fn(),
    authTranslations: {},
  };
});

test('renders the updated template home page', () => {
  render(<App />);
  expect(screen.getByText(/current template on the modern stack/i)).toBeInTheDocument();
});
