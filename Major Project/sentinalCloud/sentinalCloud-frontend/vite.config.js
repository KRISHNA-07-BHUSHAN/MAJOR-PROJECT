import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // This is the crucial part for Docker
    host: true, // Listen on all addresses, including 0.0.0.0
    port: 5173, // The port the container will expose
    // Helps with hot-reloading in some Docker/WSL setups
    watch: {
      usePolling: true,
    },
    // Proxy API requests to the backend container
    proxy: {
      // Requests to any path starting with /api will be forwarded
      '/api': {
        // The target is the backend service's name and port in Docker
        target: 'http://localhost:8000',
        // Important for virtual hosts
        changeOrigin: true,
        // Optional: remove '/api' from the forwarded request path
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})