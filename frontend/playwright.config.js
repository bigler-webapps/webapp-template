import { defineConfig, devices } from '@playwright/test';

// Used only by acceptance.py for the isolated test-management specs.
export default defineConfig({
  testDir: './tests',
  testMatch: '**/*.spec.js',
  workers: 1,
  fullyParallel: false,
  reporter: 'list',
  use: { trace: 'off', screenshot: 'off', video: 'off', locale: 'de-CH' },
  projects: [{ name: 'desktop', use: { ...devices['Desktop Chrome'] } }],
});
