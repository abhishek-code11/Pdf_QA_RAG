// Vite = the dev server + build tool that runs our React app.
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // "proxy" forwards these URLs to the Python backend on port 8000.
    // So in React we can just write fetch('/ask') — no CORS setup needed in Python.
    proxy: {
      '/pdf': 'http://localhost:8000',
      '/ask': 'http://localhost:8000',
    },
  },
})
