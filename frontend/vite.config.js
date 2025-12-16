import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 18003,
    proxy: {
      '/api': {
        target: 'http://localhost:18002',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/contents': {
        target: 'http://localhost:18002',
        changeOrigin: true
      }
    }
  }
})
