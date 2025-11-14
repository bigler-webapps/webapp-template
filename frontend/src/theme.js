// src/theme.js
import { createTheme } from '@mui/material/styles';
import '@fontsource/montserrat';
import '@fontsource/roboto';
import '@fontsource/open-sans';
import '@fontsource/dm-sans';

// Global MUI theme used across the app
const theme = createTheme({
  breakpoints: {
    // Custom breakpoint set including an XXL step
    keys: ['xs', 'sm', 'md', 'lg', 'xl', 'xxl'],
    values: {
      xs: 0,
      sm: 600,
      md: 900,
      lg: 1200,
      xl: 1536,
      xxl: 1680,
    },
  },
  palette: {
    primary: {
      main: '#468AB2',
    },
    secondary: {
      main: '#BF3227',
    },
    background: {
      default: '#FFFFFF',
    },
    text: {
      primary: '#212529',
    },
  },
  typography: {
    fontFamily: "'DM Sans', sans-serif",
    h1: {
      fontWeight: 600,
      letterSpacing: '0.0em',
    },
    h2: {
      fontWeight: 600,
      letterSpacing: '0.0em',
    },
    h3: {
      fontWeight: 600,
      letterSpacing: '0.0em',
    },
    h4: {
      fontWeight: 500,
      letterSpacing: '0.0em',
    },
    h5: {
      fontWeight: 500,
      letterSpacing: '0.0em',
    },
    h6: {
      fontWeight: 500,
      letterSpacing: '0.0em',
    },
    body1: {
      fontWeight: 400,
      letterSpacing: '0.0em',
    },
    body2: {
      fontWeight: 400,
      letterSpacing: '0.0em',
    },
    button: {
      fontWeight: 400,
      letterSpacing: '0.0em',
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 3,
          padding: '3px 8px',
          fontSize: '1rem',
        },
        contained: {
          boxShadow: 'none',
          '&:hover': {
            boxShadow: 'none',
          },
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        root: {
          // Provides consistent padding and left alignment for table cells
          padding: '8px',
          textAlign: 'left',
        },
      },
    },
  },
});

export default theme;
