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

// --- NEU: Importe aus der Bibliothek ---
import { 
  AuthProvider, 
  LoginPage, 
  AccountPage,
  PasswordResetRequestPage, 
  PasswordChangePage,
  PasswordInvitePage 
} from './webapp-management';

// --- Lokal verbliebene Seiten (Business Logic) ---
import Home from './pages/Home';
import UserManagementPage from './pages/UserManagementPage';
import WelcomePage from './pages/WelcomePage';

// Default Client-ID Header für axios
axios.defaults.headers.common['X-Client-ID'] = CLIENT_ID;

// --- AUTH KONFIGURATION ---
// Definiert die Basis-URL für die authApi in der Bibliothek
const AUTH_CONFIG = {
  // Im Development (Port 3000) müssen wir auf 8000 zeigen.
  // In Production (gleiche Domain) lassen wir es leer (= relativ).
  baseUrl: process.env.NODE_ENV === 'development' ? 'http://localhost:8000' : '',
};

function App() {
  return (
    // 1. AuthProvider umschließt alles und bekommt die Config
    <AuthProvider endpoints={AUTH_CONFIG}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Helmet>
          <title>PROJECT_NAME</title>
        </Helmet>
        
        <Router>
          <Header />
          <Routes>
            {/* --- App Pages --- */}
            <Route path="/" element={<Home />} />
            <Route path="/user-management" element={<UserManagementPage />} />
            <Route path="/welcome" element={<WelcomePage />} />

            {/* --- Auth Pages (aus der Lib) --- */}
            <Route 
              path="/login" 
              element={
                <LoginPage 
                  appName="PROJECT_NAME" 
                  redirectAfterLogin="/"
                  registerPath="/signup" // Falls du Registrierung hast
                />
              } 
            />
            
            <Route 
              path="/account" 
              element={<AccountPage />} 
            />

            <Route
              path="/reset-request-password"
              element={<PasswordResetRequestPage />}
            />
            
            <Route 
              path="/change-password" 
              element={<PasswordChangePage />} 
            />

            {/* Diese Page muss in der Lib so gebaut sein, dass sie 'mode' akzeptiert */}
            <Route 
              path="/invite/:uid/:token" 
              element={<PasswordInvitePage mode="invite" />} 
            />
            
            <Route 
              path="/reset/:uid/:token" 
              element={<PasswordInvitePage mode="reset" />} 
            />

          </Routes>
        </Router>
      </ThemeProvider>
    </AuthProvider>
  );
}

export default App;