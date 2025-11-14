// src/pages/PasswordInvitePage.jsx
import React from 'react';
import { useParams } from 'react-router-dom';
import SetPasswordForm from '../components/SetPasswordForm';
import { Helmet } from 'react-helmet';
import { NarrowPage } from '../components/layout/PageLayout';

// Renders password setup page for invited users
const PasswordInvitePage = () => {
  const { uidb64, token } = useParams();
  const endpoint = `/api/users/non_auth_reset/${uidb64}/${token}/`;

  return (
    <NarrowPage
      title="Welcome to PROJECT_NAME"
      subtitle="Please set your password to access the application."
    >
      <Helmet>
        <title>PROJECT_NAME – Welcome</title>
      </Helmet>

      <SetPasswordForm
        endpoint={endpoint}
        title="Please set your password"
        onSuccessRedirect="/login"
        validateLink
      />
    </NarrowPage>
  );
};

export default PasswordInvitePage;
