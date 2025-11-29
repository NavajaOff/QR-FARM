import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    port: process.env.PORT ? parseInt(process.env.PORT) : 5173,
    host: true,
    strictPort: false
  },
  test: {
    globals: true,
    environment: 'jsdom',
    include: ['src/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}'],
    setupFiles: ['./src/test-setup.js'],
    coverage: {
      provider: 'v8',
      all: true,
      include: ['src/**/*.{vue,js,ts}'],
      exclude: ['node_modules/', 'dist/', '.git/', 'coverage/', 'src/**/*.spec.{js,ts}', 'src/**/*.test.{js,ts}'],
      reportsDirectory: './coverage-frontend',
      reporter: ['text', 'cobertura']
    }
  }
})
