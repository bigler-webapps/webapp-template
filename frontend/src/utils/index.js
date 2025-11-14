// src/utils/index.js

// Returns cookie value for a given cookie name
export function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) {
    return parts.pop().split(';').shift();
  }
  return null;
}

// Returns base URL for the backend, here same origin
export function getBaseURL() {
  const origin = window.location.origin;
  return { http: origin };
}
