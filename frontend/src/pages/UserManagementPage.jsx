// src/pages/UserManagementPage.jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Box,
  Button,
  TextField,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import { Helmet } from 'react-helmet';
import { WidePage } from '../components/layout/PageLayout';

// Available user roles
const roles = ['none', 'student', 'teacher', 'admin'];

// Renders user management page with invite, role change and delete
const UserManagementPage = () => {
  const [inviteEmail, setInviteEmail] = useState('');
  const [allUsers, setAllUsers] = useState([]);
  const [currentUser, setCurrentUser] = useState(null);

  // Loads current user to determine permissions
  const fetchCurrentUser = async () => {
    try {
      const { data } = await axios.get('/api/users/current/', {
        withCredentials: true,
      });
      setCurrentUser(data);
    } catch (error) {
      console.error('Error fetching current user:', error);
    }
  };

  // Loads all users from backend
  const fetchAllUsers = async () => {
    try {
      const response = await axios.get('/api/users/', {
        withCredentials: true,
      });
      setAllUsers(response.data);
    } catch (error) {
      console.error('Error fetching all users:', error);
    }
  };

  useEffect(() => {
    fetchCurrentUser();
    fetchAllUsers();
  }, []);

  // Invites a new user by email
  const inviteUser = async () => {
    if (!inviteEmail) return;
    try {
      await axios.post(
        '/api/users/invite/',
        { email: inviteEmail },
        { withCredentials: true },
      );
      setInviteEmail('');
      fetchAllUsers();
    } catch (error) {
      console.error('Error inviting user:', error);
      alert('Error inviting user');
    }
  };

  // Deletes a user by id
  const deleteUser = async (userId) => {
    if (!window.confirm('Are you sure you want to DELETE this user?')) return;
    try {
      await axios.delete(`/api/users/${userId}/`, { withCredentials: true });
      fetchAllUsers();
    } catch (error) {
      console.error('Error deleting user:', error);
      alert('Error deleting user');
    }
  };

  // Updates user role with permission checks enforced on backend
  const handleChangeRole = async (userId, newRole) => {
    try {
      await axios.patch(
        `/api/users/${userId}/update-role/`,
        { role: newRole },
        { withCredentials: true },
      );
      fetchAllUsers();
    } catch (error) {
      console.error('Error updating role:', error);
      alert(
        `Error updating role: ${
          error.response?.data?.detail || error.message
        }`,
      );
    }
  };

  // Checks whether current user may edit the target user's role
  const isRoleEditable = (rowUser) => {
    if (!currentUser) return false;

    if (currentUser.is_superuser) {
      return true;
    }

    const currentRole = currentUser.role || 'none';
    const rowUserRole = rowUser.role || 'none';

    if (currentRole === 'admin') {
      return true;
    }

    if (currentRole === 'teacher') {
      if (rowUser.id === currentUser.id) return false;
      if (['teacher', 'admin'].includes(rowUserRole)) return false;
      return true;
    }

    return false;
  };

  if (!currentUser) {
    return (
      <WidePage title="User Management">
        <Typography variant="h5">Loading...</Typography>
      </WidePage>
    );
  }

  return (
    <WidePage title="User Management">
      <Helmet>
        <title>PROJECT_NAME – User Management</title>
      </Helmet>

      {/* --- Invite New User --- */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          Invite a new user
        </Typography>
        <Box
          sx={{
            display: 'flex',
            gap: 2,
            alignItems: 'center',
            maxWidth: 600,
          }}
        >
          <TextField
            label="Enter email"
            type="email"
            variant="outlined"
            fullWidth
            value={inviteEmail}
            onChange={(e) => setInviteEmail(e.target.value)}
          />
          <Button variant="contained" onClick={inviteUser}>
            Invite user
          </Button>
        </Box>
      </Box>

      {/* --- All Users Table --- */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          All users
        </Typography>
        {allUsers.length > 0 ? (
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>ID</TableCell>
                  <TableCell>Name</TableCell>
                  <TableCell>Email</TableCell>
                  <TableCell>Role</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {allUsers.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell>{user.id}</TableCell>
                    <TableCell>
                      {user.first_name || user.last_name
                        ? `${user.first_name} ${user.last_name}`.trim()
                        : user.username}
                    </TableCell>
                    <TableCell>{user.email}</TableCell>
                    <TableCell>
                      <FormControl
                        fullWidth
                        size="small"
                        disabled={!isRoleEditable(user)}
                      >
                        <InputLabel id={`role-label-${user.id}`}>
                          Role
                        </InputLabel>
                        <Select
                          labelId={`role-label-${user.id}`}
                          id={`role-select-${user.id}`}
                          value={user.role || 'none'}
                          label="Role"
                          onChange={(e) =>
                            handleChangeRole(user.id, e.target.value)
                          }
                        >
                          {roles.map((r) => (
                            <MenuItem key={r} value={r}>
                              {r}
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                    </TableCell>
                    <TableCell>
                      <Button
                        variant="contained"
                        size="small"
                        color="error"
                        onClick={() => deleteUser(user.id)}
                      >
                        Delete
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        ) : (
          <Typography variant="body1">No users found.</Typography>
        )}
      </Box>
    </WidePage>
  );
};

export default UserManagementPage;
