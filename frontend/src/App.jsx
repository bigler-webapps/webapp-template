import React from "react";
import { BrowserRouter as Router, Navigate, Route, Routes } from "react-router-dom";

import {
  AuthProvider,
  LoginPage,
  PasswordInvitePage,
  PasswordResetRequestPage,
  PrivacyBanner,
  PrivacyProvider,
  createPrivacyApi,
  SignUpPage,
  SignupConfirmPage,
} from "@micha.bigler/ui-core-micha";

import Header from "./components/Header";
import RequireAuth from "./components/RequireAuth";
import AccountHubPage from "./pages/AccountHubPage";
import Home from "./pages/Home";
import WelcomePage from "./pages/WelcomePage";

const privacyApi = createPrivacyApi({}, { apiBase: "/api/privacy/", csrfUrl: "/api/csrf/" });

function App() {
  return (
    <AuthProvider>
      <PrivacyProvider api={privacyApi}>
        <Router>
          <PrivacyBanner />
          <Header />
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/signup" element={<SignUpPage />} />
            <Route path="/signup/confirm" element={<SignupConfirmPage />} />
            <Route path="/reset-request-password" element={<PasswordResetRequestPage />} />
            <Route path="/invite/:uid/:token" element={<PasswordInvitePage />} />
            <Route path="/reset/:uid/:token" element={<PasswordInvitePage />} />
            <Route
              path="/welcome"
              element={
                <RequireAuth>
                  <WelcomePage />
                </RequireAuth>
              }
            />
            <Route
              path="/account"
              element={
                <RequireAuth>
                  <AccountHubPage />
                </RequireAuth>
              }
            />
            <Route path="/user-management" element={<Navigate to="/account?tab=users" replace />} />
            <Route path="/profile" element={<Navigate to="/account" replace />} />
            <Route path="/change-password" element={<Navigate to="/account" replace />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Router>
      </PrivacyProvider>
    </AuthProvider>
  );
}

export default App;
