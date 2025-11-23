// src/pages/AccountPage.jsx
import React, { useState } from 'react';
import { Helmet } from 'react-helmet';
import { Tabs, Tab, Box } from '@mui/material';
import { WidePage } from '../../components/layout/PageLayout';
import ProfileComponent from '../components/ProfileComponent';
import SecurityComponent from '../components/SecurityComponent'; // kommt gleich

const AccountPage = () => {
  const [tab, setTab] = useState('account');

  const handleTabChange = (_event, newValue) => {
    setTab(newValue);
  };

  return (
    <WidePage title="Account">
      <Helmet>
        <title>PROJECT_NAME – Account</title>
      </Helmet>

      <Tabs
        value={tab}
        onChange={handleTabChange}
        sx={{ mb: 3 }}
      >
        <Tab label="Account" value="account" />
        <Tab label="Security" value="security" />
      </Tabs>

      {tab === 'account' && (
        <Box sx={{ mt: 1 }}>
          <ProfileComponent
            onLoad={() => {}}
            onSubmit={(payload) =>
              // wie bisher: PATCH /api/users/current/
              // die Implementierung hast du schon
              // hier kannst du deine bisherige handleSave-Funktion verwenden
              Promise.resolve()
            }
            submitText="Save"
            showName
            showPrivacy
            showCookies
          />
        </Box>
      )}

      {tab === 'security' && (
        <Box sx={{ mt: 1 }}>
          <SecurityComponent />
        </Box>
      )}
    </WidePage>
  );
};

export default AccountPage;
