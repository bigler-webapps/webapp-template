// src/components/UserListTab.jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Box,
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
  Button,
} from '@mui/material';

const roles = ['none', 'collaborator', 'supervisor', 'admin'];

const UserListTab = () => {
  const [allUsers, setAllUsers] = useState([]);
  const [currentUser, setCurrentUser] = useState(null);

  const fetchCurrentUser = async () => {
    try {
      const { data } = await axios.get('/api/users/current/', {
        withCredentials: true,
      });
      setCurrentUser(data);
    } catch (error) {
      // eslint-disable-next-line no-console
      console.error('Error fetching current user:', error);
    }
  };

  const fetchAllUsers = async () => {
    try {
      const { data } = await axios.get('/api/users/', {
        withCredentials: true,
      });
      setAllUsers(data);
    } catch (error) {
      // eslint-disable-next-line no-console
      console.error('Error fetching all users:', error);
    }
  };

  useEffect(() => {
    fetchCurrentUser();
    fetchAllUsers();
  }, []);

  const deleteUser = async (userId) => {
    // eslint-disable-next-line no-alert
    if (!window.confirm('Are you sure you want to DELETE this user?')) return;
    try {
      await axios.delete(`/api/users/${userId}/`, {
        withCredentials: true,
      });
      fetchAllUsers();
    } catch (error) {
      // eslint-disable-next-line no-console
      console.error('Error deleting user:', error);
      // eslint-disable-next-line no-alert
      alert('Error deleting user');
    }
  };

  const handleChangeRole = async (userId, newRole) => {
    try {
      await axios.patch(
        `/api/users/${userId}/update-role/`,
        { role: newRole },
        { withCredentials: true },
      );
      fetchAllUsers();
    } catch (error) {
      // eslint-disable-next-line no-console
      console.error('Error updating role:', error);
      // eslint-disable-next-line no-alert
      alert(
        `Error updating role: ${
          error.response?.data?.detail || error.message
        }`,
      );
    }
  };

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

    if (currentRole === 'supervisor') {
      if (rowUser.id === currentUser.id) return false;
      if (['supervisor', 'admin'].includes(rowUserRole)) return false;
      return true;
    }

    return false;
  };

  if (!currentUser) {
    return (
      <Typography variant="body1">
        Loading…
      </Typography>
    );
  }

  return (
    <Box>
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
  );
};

export default UserListTab;
