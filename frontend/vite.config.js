import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'node:path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    port: process.env.PORT ? Number.parseInt(process.env.PORT) : 5173,
    host: true,
    strictPort: false
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test-setup.js'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'lcov', 'json'],
      reportsDirectory: './coverage',
      include: ['src/**/*.{js,ts,vue}'],
      exclude: [
        'node_modules',
        '**/icov-report/**',
        '**/*.spec.{js,ts}',
        '**/*.test.{js,ts}',
        '**/test-setup.js',
        '**/test-helpers.*'
      ],
      tempDirectory: './node_modules/.vitest-coverage-temp'
    }
  }
})
