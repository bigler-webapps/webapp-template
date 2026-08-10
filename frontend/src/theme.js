import { createAppTheme } from '@micha.bigler/ui-core-micha';

// Only DM Sans is referenced in typography.fontFamily below. We import the
// latin subset for weights 400/500/600. Add other fontsource packages here
// if the app's theme picks them up.
import '@fontsource/dm-sans/latin-400.css';
import '@fontsource/dm-sans/latin-500.css';
import '@fontsource/dm-sans/latin-600.css';

const theme = createAppTheme({
  palette: {
    primary: {
      // TODO: replace with this app's accent
      main: '#FF00FF',
    },
  },
  typography: {
    fontFamily: "'DM Sans', sans-serif",
  },
});

export default theme;
