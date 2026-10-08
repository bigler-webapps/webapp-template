import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react-swc';
import path from 'path';
import { fileURLToPath } from 'url';

const rootDir = fileURLToPath(new URL('.', import.meta.url));
const fromRoot = (...segments: string[]) => path.resolve(rootDir, ...segments);

// Node >=22's experimental native `localStorage`/`sessionStorage` globals shadow jsdom's own
// Storage implementation with an incomplete one (missing e.g. `.clear()`), breaking any test
// that touches `localStorage` directly. Disabling it here (before vitest spawns its test
// workers, which re-read `NODE_OPTIONS` from the current process env) restores jsdom's own
// implementation without requiring every invocation to set the flag manually.
// Gated to `process.env.VITEST` (set by vitest itself) so `vite` dev/build/preview never has
// this forced on them.
if (
  process.env.VITEST &&
  !process.env.NODE_OPTIONS?.includes('--no-experimental-webstorage')
) {
  process.env.NODE_OPTIONS = `${process.env.NODE_OPTIONS ?? ''} --no-experimental-webstorage`.trim();
}

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './src/setupTests.js',
    css: false,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
      // Keep the baseline report when the suite exposes pre-existing failures.
      reportOnFailure: true,
    },
  },
  server: {
    port: 5173,
    watch: {
      usePolling: true,
    },
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
      },
      '/static/admin': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/admin': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
  resolve: {
    alias: [
      {
        find: /^@mui\/icons-material\/(.*)$/,
        replacement: `${fromRoot('node_modules', '@mui', 'icons-material').replace(
          /\\/g,
          '/'
        )}/$1.js`,
      },
      {
        find: '@micha.bigler/ui-core-micha',
        replacement: fromRoot('node_modules', '@micha.bigler', 'ui-core-micha'),
      },
      {
        find: 'components',
        replacement: fromRoot('src/components'),
      },
      {
        find: 'pages',
        replacement: fromRoot('src/pages'),
      },
      {
        find: 'utils',
        replacement: fromRoot('src/utils'),
      },
      {
        find: '@',
        replacement: fromRoot('src'),
      },
    ],
  },
  build: {
    outDir: 'build',
    assetsDir: 'static',
    sourcemap: false,
  },
  base: '/',
});
