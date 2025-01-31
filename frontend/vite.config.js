import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // listen on all IPs
    port: 5173, // default vite port
    strictPort: true, // fail if the port is already in use
    hmr: {
      port: 5173, // hmr is on the same port as the dev server
    },
    watch: {
      usePolling: true, // Enable polling to handle file changes better in Docker
    },
  },
});
