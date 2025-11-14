// src/App.js
import React from 'react';
import axios from 'axios';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './AuthContext';
import Header from './components/Header';

import Home from './pages/Home';
import UserManagementPage from './pages/UserManagementPage';
import LoginPage from './pages/LoginPage';
import ProfilePage from './pages/ProfilePage';
import PasswordInvitePage from './pages/PasswordInvitePage';
import PasswordResetPage from './pages/PasswordResetPage';
import PasswordChangePage from './pages/PasswordChangePage';
import WelcomePage from './pages/WelcomePage';
import SendPasswordResetMailPage from './pages/SendPasswordResetMailPage';

import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import theme from './theme';
import { CLIENT_ID } from './utils/clientId';
import { Helmet } from 'react-helmet';

// Sets default client id header for axios
axios.defaults.headers.common['X-Client-ID'] = CLIENT_ID;

function App() {
  return (
    <AuthProvider>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Router>
          <Header />
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/user-management" element={<UserManagementPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route
              path="/reset-request-password"
              element={<SendPasswordResetMailPage />}
            />
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="/invite/:uidb64/:token" element={<PasswordInvitePage />} />
            <Route path="/reset/:uidb64/:token" element={<PasswordResetPage />} />
            <Route path="/change-password" element={<PasswordChangePage />} />
            <Route path="/welcome" element={<WelcomePage />} />
          </Routes>
        </Router>
      </ThemeProvider>
    </AuthProvider>
  );
}

export default App;
