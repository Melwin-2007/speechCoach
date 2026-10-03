import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/health': 'http://localhost:8000',
      '/baselines': 'http://localhost:8000',
      '/analyze': 'http://localhost:8000',
      '/demo': 'http://localhost:8000',
    },
  },
})
