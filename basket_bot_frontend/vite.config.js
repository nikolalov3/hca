import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,  // Nasłuchuj na wszystkich adresach IP
    allowedHosts: true, // <--- TO JEST KLUCZOWE (wyłącza blokadę hostów)
    cors: true
  }
})
