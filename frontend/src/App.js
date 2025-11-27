// src/App.js
import React from 'react';
import axios from 'axios';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Helmet } from 'react-helmet';

import theme from './theme';
import { CLIENT_ID } from './utils/clientId';

import Header from './components/Header';

// Auth
import { AuthProvider } from './auth/AuthContext';
import LoginPage from './auth/pages/LoginPage';
import PasswordResetRequestPage from './auth/pages/PasswordResetRequestPage';
import PasswordChangePage from './auth/pages/PasswordChangePage';
import PasswordInvitePage from './auth/pages/PasswordInvitePage';

// Restliche Seiten
import Home from './pages/Home';
import UserManagementPage from './pages/UserManagementPage';
import AccountPage from './auth/pages/AccountPage';
import WelcomePage from './pages/WelcomePage';

// Default Client-ID Header für axios
axios.defaults.headers.common['X-Client-ID'] = CLIENT_ID;

function App() {
  return (
    <AuthProvider>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Helmet>
          <title>PROJECT_NAME</title>
        </Helmet>
        <Router>
          <Header />
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/user-management" element={<UserManagementPage />} />

            {/* Auth */}
            <Route path="/login" element={<LoginPage />} />
            <Route
              path="/reset-request-password"
              element={<PasswordResetRequestPage />}
            />
            <Route path="/change-password" element={<PasswordChangePage />} />

            <Route path="/invite/:uid/:token" element={<PasswordInvitePage mode="invite" />} />
            <Route path="/reset/:uid/:token" element={<PasswordInvitePage mode="reset" />} />

            {/* Profil / Onboarding */}
            <Route path="/account" element={<AccountPage />} />
            <Route path="/welcome" element={<WelcomePage />} />
          </Routes>
        </Router>
      </ThemeProvider>
    </AuthProvider>
  );
}

export default App;
