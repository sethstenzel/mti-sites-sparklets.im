import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 18003,
    proxy: {
      '/api': {
        target: 'http://localhost:18002',
        changeOrigin: true
      },
      '/contents': {
        target: 'http://localhost:18002',
        changeOrigin: true
      }
    }
  },
  define: {
    'import.meta.env.VITE_API_BASE_URL': JSON.stringify(process.env.VITE_API_BASE_URL || 'http://localhost:18003')
  }
})
