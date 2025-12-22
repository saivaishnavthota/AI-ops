import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 7026,
    proxy: {
      '/api': {
        target: 'http://localhost:7027',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:7027',
        ws: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
});
