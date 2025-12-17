import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ mode }) => ({
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
    // Only set API base URL in dev mode, production uses relative URLs
    'import.meta.env.VITE_API_BASE_URL': mode === 'development'
      ? JSON.stringify('http://localhost:18003')
      : JSON.stringify('')
  }
}))
