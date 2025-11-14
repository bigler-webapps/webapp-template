// src/pages/PasswordChangePage.jsx
import React from 'react';
import SetPasswordForm from '../components/SetPasswordForm';
import { Helmet } from 'react-helmet';
import { NarrowPage } from '../components/layout/PageLayout';

// Renders password change page for authenticated users
const PasswordChangePage = () => {
  const endpoint = `/api/users/auth_reset/`; // needs matching backend endpoint

  return (
    <NarrowPage
      title="Change password"
      subtitle="Enter a new password for your account."
    >
      <Helmet>
        <title>PROJECT_NAME – Change password</title>
      </Helmet>

      <SetPasswordForm
        endpoint={endpoint}
        title="Please insert your new password"
        onSuccessRedirect="/login"
        validateLink={false}
      />
    </NarrowPage>
  );
};

export default PasswordChangePage;
