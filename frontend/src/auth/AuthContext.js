// src/auth/AuthContext.jsx
import React, {
  createContext,
  useState,
  useEffect,
} from 'react';
import axios from 'axios';
import { CSRF_URL } from './authConfig';
import {
  fetchCurrentUser,
  logoutSession,
} from './authApi';

export const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Einmalige Axios-Basis-Konfiguration
  useEffect(() => {
    axios.defaults.withCredentials = true;
    axios.defaults.xsrfCookieName = 'csrftoken';
    axios.defaults.xsrfHeaderName = 'X-CSRFToken';
  }, []);

  useEffect(() => {
    let isMounted = true;

    const initAuth = async () => {
      try {
        // 1) CSRF-Cookie setzen (Django-View /api/csrf/)
        try {
          await axios.get(CSRF_URL, { withCredentials: true });
          // console.log('CSRF cookie set');
        } catch (err) {
          // eslint-disable-next-line no-console
          console.error('Error setting CSRF cookie:', err);
        }

        // 2) aktuellen User laden (falls Session vorhanden)
        try {
          const data = await fetchCurrentUser();
          if (!isMounted) return;
          setUser({
            id: data.id,
            username: data.username,
            email: data.email,
            first_name: data.first_name,
            last_name: data.last_name,
            role: data.role,
            is_superuser: data.is_superuser,
          });
        } catch (err) {
          // Kein eingeloggter User ist ein normaler Fall
          // eslint-disable-next-line no-console
          console.log('No logged-in user:', err?.message || err);
          if (!isMounted) return;
          setUser(null);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    initAuth();

    return () => {
      isMounted = false;
    };
  }, []);

  // Nach erfolgreichem Login das User-Objekt setzen
  // (z. B. aus loginWithPassword in authApi)
  const login = (userData) => {
    setUser((prev) => ({
      ...prev,
      ...userData,
    }));
  };

  // Logout im Backend + lokalen State leeren
  const logout = async () => {
    try {
      await logoutSession();
    } catch (error) {
      // eslint-disable-next-line no-console
      console.error('Error during logout:', error);
    } finally {
      setUser(null);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
