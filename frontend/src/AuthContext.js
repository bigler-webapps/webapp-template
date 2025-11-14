// src/AuthContext.jsx
import React, { createContext, useState, useEffect } from 'react';
import axios from 'axios';

export const AuthContext = createContext(null);

// Provides authentication state and helpers for login/logout
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Configure axios to handle CSRF cookies and headers
  axios.defaults.withCredentials = true;
  axios.defaults.xsrfCookieName = 'csrftoken';
  axios.defaults.xsrfHeaderName = 'X-CSRFToken';

  useEffect(() => {
    // Ensures CSRF cookie is set on the client
    axios
      .get('/api/csrf/', { withCredentials: true })
      .then(() => {
        console.log('CSRF cookie should be set now.');
      })
      .catch((err) => {
        console.error('Error setting CSRF cookie:', err);
      });

    // Loads current user profile if session exists
    axios
      .get('/api/users/current/', { withCredentials: true })
      .then((response) => {
        const data = response.data;
        setUser({
          id: data.id,
          username: data.username,
          email: data.email,
          first_name: data.first_name,
          last_name: data.last_name,
          role: data.role,
          is_superuser: data.is_superuser,
        });
      })
      .catch((error) => {
        console.log('No logged in user:', error);
        setUser(null);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  // Stores user data after successful login
  const login = (userData) => {
    setUser((prev) => ({
      ...prev,
      ...userData,
    }));
  };

  // Logs user out via backend and clears local state
  const logout = async () => {
    try {
      await axios.post('/api/users/logout/', {}, { withCredentials: true });
    } catch (error) {
      console.error('Error during logout:', error);
    } finally {
      setUser(null);
    }
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
