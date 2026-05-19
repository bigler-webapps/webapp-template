import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import './i18n';
import { CssBaseline, ThemeProvider } from '@mui/material';
import App from './App';
import theme from './theme';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <App />
    </ThemeProvider>
  </React.StrictMode>
);
