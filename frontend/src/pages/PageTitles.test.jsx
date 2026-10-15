import { AuthContext } from '@micha.bigler/ui-core-micha';
import { render, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';

import i18n from '../i18n';
import Home from './Home';
import WelcomePage from './WelcomePage';

const renderPage = (Page, authValue) => render(
  <AuthContext.Provider value={authValue}>
    <MemoryRouter>
      <Page />
    </MemoryRouter>
  </AuthContext.Provider>,
);

describe('page document titles', () => {
  it('sets the translated Home title', async () => {
    renderPage(Home, { user: null });

    await waitFor(() => {
      expect(document.title).toBe(i18n.t('Home.PAGE_TITLE'));
    });
  });

  it('sets the translated Welcome title', async () => {
    renderPage(WelcomePage, { user: { is_new: true }, login: () => {} });

    await waitFor(() => {
      expect(document.title).toBe(i18n.t('Welcome.PAGE_TITLE'));
    });
  });
});
