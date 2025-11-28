// src/components/Header.jsx
import React, { useContext } from 'react';
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { AuthContext } from 'webapp-management';

// Renders the main app header with navigation and auth actions
const Header = () => {
  const { user, logout } = useContext(AuthContext);
  

  const navigate = useNavigate();

  
  async function handleLogout() {
    await logout();       // uses the logout from AuthContext (calls logoutSession + setUser(null))
    navigate('/login');   // then redirect to login
  }

  return (
    <AppBar position="static">
      <Toolbar>
        <Typography
          variant="h6"
          component={RouterLink}
          to="/"
          sx={{ flexGrow: 1, textDecoration: 'none', color: 'inherit' }}
        >
          PROJECT_NAME
        </Typography>

        {user ? (
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button color="inherit" component={RouterLink} to="/account">
              Profile
            </Button>
            <Button color="inherit" component={RouterLink} to="/user-management">
              Users
            </Button>
            <Button color="inherit" onClick={handleLogout}>
              Logout
            </Button>
          </Box>
        ) : (
          <Button color="inherit" component={RouterLink} to="/login">
            Login
          </Button>
        )}
      </Toolbar>
    </AppBar>
  );
};

export default Header;
