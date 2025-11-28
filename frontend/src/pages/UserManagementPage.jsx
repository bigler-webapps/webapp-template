// src/pages/UserManagementPage.jsx
import React, { useState } from 'react';
import { Box, Tabs, Tab, Typography } from '@mui/material';
import { Helmet } from 'react-helmet';
import { WidePage, AccessCodeManager } from '@micha.bigler/ui-core-micha';

// Diese beiden Komponenten bleiben in deiner App
import UserListTab from '../components/Users/UserListTab';
import InviteUserTab from '../components/Users/UserInviteTab';

const UserManagementPage = () => {
  const [tab, setTab] = useState('list');

  const handleTabChange = (_event, value) => {
    setTab(value);
  };

  return (
    <WidePage title="User Management">
      <Helmet>
        <title>PROJECT_NAME – User Management</title>
      </Helmet>

      <Tabs
        value={tab}
        onChange={handleTabChange}
        sx={{ mb: 3 }}
      >
        <Tab label="Users" value="list" />
        <Tab label="Invite" value="invite" />
        <Tab label="Access codes" value="access" />
      </Tabs>

      {tab === 'list' && (
        <Box>
          <UserListTab />
        </Box>
      )}

      {tab === 'invite' && (
        <Box>
          <UserInviteTab />
        </Box>
      )}

      {tab === 'access' && (
        <Box>
          <Typography variant="body2" sx={{ mb: 2 }}>
            Access codes control who can self-register when access-code registration is enabled.
          </Typography>
          <AccessCodeManager />
        </Box>
      )}
    </WidePage>
  );
};

export default UserManagementPage;
