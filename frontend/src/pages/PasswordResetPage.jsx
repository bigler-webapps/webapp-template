// src/pages/PasswordResetPage.jsx
import React from 'react';
import { useParams } from 'react-router-dom';
import SetPasswordForm from '../components/SetPasswordForm';
import { Helmet } from 'react-helmet';
import { NarrowPage } from '../components/layout/PageLayout';

// Renders password reset page for non-authenticated users
const PasswordResetPage = () => {
  const { uidb64, token } = useParams();
  const endpoint = `/api/users/non_auth_reset/${uidb64}/${token}/`;

  return (
    <NarrowPage
      title="Change password"
      subtitle="Please choose a new password for your account."
    >
      <Helmet>
        <title>PROJECT_NAME – Change password</title>
      </Helmet>

      <SetPasswordForm
        endpoint={endpoint}
        title="Please insert your new password"
        onSuccessRedirect="/login"
        validateLink
      />
    </NarrowPage>
  );
};

export default PasswordResetPage;
