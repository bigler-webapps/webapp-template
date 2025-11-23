// src/auth/authApi.js
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

/**
 * Fetches the current authenticated user from your own User API.
 * Expected to return the same shape as before (/api/users/current/).
 */
export async function fetchCurrentUser() {
  const res = await axios.get(`${USERS_BASE}/current/`, {
    withCredentials: true,
  });
  return res.data;
}

/**
 * Logs a user in using email/password via allauth headless.
 * Afterwards fetches current user from /api/users/current/.
 */
export async function loginWithPassword(email, password) {
  try {
    // 1) Log in via allauth headless
    await axios.post(
      `${HEADLESS_BASE}/auth/login`,
      {
        email, // Using 'email' key as configured in backend
        password,
      },
      { withCredentials: true },
    );
  } catch (error) {
    // FIX: If the server returns 409, it means the session is already authenticated.
    // We swallow this error and proceed to fetch the user details.
    if (error.response && error.response.status === 409) {
       // Proceed normally
    } else {
      throw new Error(extractErrorMessage(error));
    }
  }

  // 2) Fetch current user from your own API
  const user = await fetchCurrentUser();
  return user;
}

/**
 * Requests a password reset email via allauth headless.
 * Some setups accept "email", andere "login".
 */
export async function requestPasswordReset(email) {
  try {
    await axios.post(
      `${HEADLESS_BASE}/auth/password/reset`,
      { email },
      { withCredentials: true },
    );
  } catch (error) {
    throw new Error(extractErrorMessage(error));
  }
}

/**
 * Sets a new password using a reset key (from email link).
 * Typically used on "PasswordSet"/"PasswordReset" page.
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
 * oldPassword may be optional depending on your policy.
 */
export async function changePassword(oldPassword, newPassword) {
  try {
    await axios.post(
      `${HEADLESS_BASE}/account/password/change`,
      {
        old_password: oldPassword,
        new_password1: newPassword,
        new_password2: newPassword,
      },
      { withCredentials: true },
    );
  } catch (error) {
    throw new Error(extractErrorMessage(error));
  }
}

/**
 * Logs the user out via allauth headless.
 * Optionally, you can also call your legacy /api/users/logout/ if needed.
 */
export async function logoutSession() {
  try {
    await axios.post(
      `${HEADLESS_BASE}/auth/logout`,
      {},
      { withCredentials: true },
    );
  } catch (error) {
    // Logout-Fehler sind selten kritisch, daher hier nur loggen
    // und nicht weiterwerfen.
    // eslint-disable-next-line no-console
    console.error('Logout error:', error);
  }
}

/**
 * Starts an OAuth social login flow for the given provider.
 * Provider examples: "google", "microsoft".
 */
export function startSocialLogin(provider) {
  window.location.href = `${HEADLESS_BASE}/social/login/${provider}/`;
}

/**
 * Loads the current session information directly from allauth headless.
 * Can be useful in a dedicated AuthCallback page.
 */
export async function fetchHeadlessSession() {
  const res = await axios.get(`${HEADLESS_BASE}/auth/session`, {
    withCredentials: true,
  });
  return res.data;
}

/**
 * Placeholder for future Passkey (WebAuthn) login.
 * Here you will combine navigator.credentials.get(...) with a
 * headless WebAuthn endpoint when available.
 */
export async function loginWithPasskey() {
  // TODO: wire this up once WebAuthn endpoints are fully defined.
  throw new Error('Passkey login is not implemented yet.');
}

/**
 * Placeholder for future Passkey registration.
 * Used in Security/Account settings to add a new Passkey.
 */
export async function registerPasskey() {
  // TODO: implement WebAuthn registration flow.
  throw new Error('Passkey registration is not implemented yet.');
}

export const authApi = {
  fetchCurrentUser,
  loginWithPassword,
  requestPasswordReset,
  resetPasswordWithKey,
  changePassword,
  logoutSession,
  startSocialLogin,
  fetchHeadlessSession,
  loginWithPasskey,
  registerPasskey,
};