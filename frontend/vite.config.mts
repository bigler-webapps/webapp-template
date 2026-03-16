import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react-swc';
import path from 'path';
import { fileURLToPath } from 'url';

const rootDir = fileURLToPath(new URL('.', import.meta.url));
const fromRoot = (...segments: string[]) => path.resolve(rootDir, ...segments);

export default defineConfig({
  plugins: [react()],
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
