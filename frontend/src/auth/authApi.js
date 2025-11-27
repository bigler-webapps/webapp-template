import axios from 'axios';
import { HEADLESS_BASE, USERS_BASE } from './authConfig'; 

// Helper to normalise error messages from API responses
function extractErrorMessage(error) {
  const data = error.response?.data;
  if (!data) {
    return error.message || 'Unknown error';
  }
  if (typeof data.detail === 'string') {
    return data.detail;
  }
  if (Array.isArray(data.non_field_errors) && data.non_field_errors.length > 0) {
    return data.non_field_errors[0];
  }
  return JSON.stringify(data);
}

// Helper to get CSRF token from cookies manually
function getCsrfToken() {
  if (!document.cookie) return null;
  const match = document.cookie.match(/csrftoken=([^;]+)/);
  return match ? match[1] : null;
}

/**
 * Fetches the current authenticated user from your own User API.
 */
export async function fetchCurrentUser() {
  const res = await axios.get(`${USERS_BASE}/current/`, {
    withCredentials: true,
  });
  return res.data;
}

/**
 * Updates the user profile fields.
 */
export async function updateUserProfile(data) {
  const res = await axios.patch(`${USERS_BASE}/current/`, data, {
    withCredentials: true,
  });
  return res.data;
}

/**
 * Logs a user in using email/password via allauth headless.
 */
export async function loginWithPassword(email, password) {
  try {
    await axios.post(
      `${HEADLESS_BASE}/auth/login`,
      {
        email, 
        password,
      },
      { withCredentials: true },
    );
  } catch (error) {
    if (error.response && error.response.status === 409) {
       // Proceed normally if already logged in
    } else {
      throw new Error(extractErrorMessage(error));
    }
  }

  const user = await fetchCurrentUser();
  return user;
}

/**
 * Requests a password reset email via allauth headless.
 */
export async function requestPasswordReset(email) {
  try {
    await axios.post(
      `${USERS_BASE}/reset-request/`,
      { email },
      { withCredentials: true },
    );
  } catch (error) {
    throw new Error(extractErrorMessage(error));
  }
}

/**
 * Sets a new password using a reset key (from email link).
 */
export async function resetPasswordWithKey(key, newPassword) {
  try {
    await axios.post(
      `${HEADLESS_BASE}/auth/password/reset/key`,
      {
        key,
        password: newPassword,
      },
      { withCredentials: true },
    );
  } catch (error) {
    throw new Error(extractErrorMessage(error));
  }
}

/**
 * Changes the password for an authenticated user.
 */
export async function changePassword(currentPassword, newPassword) {
  try {
    await axios.post(
      `${HEADLESS_BASE}/account/password/change`,
      {
        current_password: currentPassword,
        new_password: newPassword,
      },
      { withCredentials: true },
    );
  } catch (error) {
    throw new Error(extractErrorMessage(error));
  }
}

/**
 * Logs the user out via allauth headless.
 */
export async function logoutSession() {
  try {
    const headers = {};
    const csrfToken = getCsrfToken();
    if (csrfToken) {
      headers['X-CSRFToken'] = csrfToken;
    }

    await axios.delete(
      `${HEADLESS_BASE}/auth/session`,
      { 
        withCredentials: true,
        headers, 
      },
    );
  } catch (error) {
    if (error.response && [401, 404, 410].includes(error.response.status)) {
      return;
    }
    // eslint-disable-next-line no-console
    console.error('Logout error:', error);
  }
}

/**
 * Starts an OAuth social login flow for the given provider.
 * Provider examples: "google", "microsoft".
 * * FIX:
 * 1. Uses POST instead of GET (standard for headless init flows).
 * 2. Uses the correct path '/providers/{provider}/login'.
 */
export function startSocialLogin(provider) {
  window.location.href = `/accounts/${provider}/login/?process=login`;
}



/**
 * Loads the current session information directly from allauth headless.
 */
export async function fetchHeadlessSession() {
  const res = await axios.get(`${HEADLESS_BASE}/auth/session`, {
    withCredentials: true,
  });
  return res.data;
}

export async function loginWithPasskey() {
  throw new Error('Passkey login is not implemented yet.');
}

export async function registerPasskey() {
  throw new Error('Passkey registration is not implemented yet.');
}

export async function verifyResetToken(uid, token) {
  const res = await axios.get(
    `${USERS_BASE}/password-reset/${uid}/${token}/`,
    { withCredentials: true },
  );
  return res.data;
}

export async function setNewPassword(uid, token, newPassword) {
  const res = await axios.post(
    `${USERS_BASE}/password-reset/${uid}/${token}/`,
    { new_password: newPassword },
    { withCredentials: true },
  );
  return res.data;
}


export const authApi = {
  fetchCurrentUser,
  updateUserProfile,
  loginWithPassword,
  requestPasswordReset,
  changePassword,
  logoutSession,
  startSocialLogin,
  fetchHeadlessSession,
  verifyResetToken,
  setNewPassword,
  loginWithPasskey,
  registerPasskey,
};