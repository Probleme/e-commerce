import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    watch: {
      usePolling: true,
    },
    hmr: {
      protocol: 'wss',
      host: 'localhost',
      port: 8002,  // Changed to match Nginx SSL port
      clientPort: 8002,  // Added to ensure client connects to the correct port
      path: 'hmr/',  // Added to avoid conflicts with other WebSocket connections
    },
    proxy: {
      '/api': {
        target: 'https://localhost:8002',  // Updated to use HTTPS
        changeOrigin: true,
        secure: false,  // Keep false if using self-signed certificates
        ws: true,  // Enable WebSocket proxy
      },
    },
  },
});