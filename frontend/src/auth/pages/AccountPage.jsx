import React, { useState, useContext } from 'react';
import { Helmet } from 'react-helmet';
import { Tabs, Tab, Box } from '@mui/material';
import { WidePage } from '../../components/layout/PageLayout';
import ProfileComponent from '../components/ProfileComponent';
import SecurityComponent from '../components/SecurityComponent'; // Kommentiere ich ein, bis die Datei existiert, um Build-Fehler zu vermeiden
import { authApi } from '../authApi';
import { AuthContext } from '../AuthContext';

const AccountPage = () => {
  const [tab, setTab] = useState('account');
  const { login } = useContext(AuthContext);

  const handleTabChange = (_event, newValue) => {
    setTab(newValue);
  };

  // Diese Funktion übernimmt das tatsächliche Speichern
  const handleProfileSubmit = async (payload) => {
    // 1. Send update to backend via PATCH
    const updatedUser = await authApi.updateUserProfile(payload);
    
    // 2. Update local global context with fresh data (so header/sidebar update immediately)
    login(updatedUser);
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
            onLoad={() => {}} // Optional: Falls du beim Laden noch etwas tun willst
            onSubmit={handleProfileSubmit} // Hier wird jetzt die echte API aufgerufen
            submitText="Save"
            showName
            showPrivacy
            showCookies
          />
        </Box>
      )}

      {tab === 'security' && (
        <Box sx={{ mt: 1 }}>
           {<SecurityComponent/> }
           
        </Box>
      )}
    </WidePage>
  );
};

export default AccountPage;