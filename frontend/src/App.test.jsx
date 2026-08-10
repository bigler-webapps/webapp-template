import { readFileSync } from 'node:fs';

import { ThemeProvider } from '@mui/material';
import { render, screen } from '@testing-library/react';
import {
  assertThemeComplete,
  createAppTheme,
} from '@micha.bigler/ui-core-micha';
import { describe, expect, it } from 'vitest';

import App from './App';
import './i18n';
import theme from './theme';

const PLACEHOLDER_ACCENT = '#FF00FF';

const readFrontendFile = (relativePath) =>
  readFileSync(new URL(relativePath, import.meta.url), 'utf8');

describe('template frontend baseline', () => {
  it('builds the exported theme with createAppTheme and has no completeness findings', () => {
    expect(theme.themeCompleteness?.baseline).toBe(true);
    expect(assertThemeComplete(theme).findings).toEqual([]);
  });

  it('keeps the deliberate placeholder accent non-default and requires an app accent', () => {
    expect(theme.palette.primary.main).toBe(PLACEHOLDER_ACCENT);
    expect(assertThemeComplete(theme).findings).not.toEqual(
      expect.arrayContaining([
        expect.objectContaining({ surface: 'palette.primary.main' }),
      ]),
    );
    expect(() => createAppTheme({
      typography: { fontFamily: "'DM Sans', sans-serif" },
    })).toThrow('createAppTheme: appConfig.palette.primary is required.');
  });

  it('mounts and renders the application after the dependency bump', () => {
    render(
      <ThemeProvider theme={theme}>
        <App />
      </ThemeProvider>,
    );

    expect(screen.getByRole('banner')).toBeInTheDocument();
    // Home renders two h4 headings (WidePage's own title + the page's
    // Typography variant="h4") and no h1 -- pre-existing heading structure,
    // unrelated to this WO's scope (theme/dependency/HTML-meta only), so the
    // mount check confirms real content rendered without asserting a
    // specific count or level the page doesn't guarantee.
    expect(screen.getAllByRole('heading').length).toBeGreaterThan(0);
  });

  it('declares viewport coverage and reserves every safe-area edge in the light scheme', () => {
    const html = readFrontendFile('../index.html');
    const css = readFrontendFile('./index.css');

    expect(html).toMatch(
      /<meta\s+name="viewport"\s+content="[^"]*viewport-fit=cover[^"]*"\s*\/?>/,
    );
    expect(css).toMatch(/color-scheme:\s*light\s*;/);
    for (const edge of ['top', 'right', 'bottom', 'left']) {
      expect(css).toContain(
        `padding-${edge}: env(safe-area-inset-${edge});`,
      );
    }
  });
});
