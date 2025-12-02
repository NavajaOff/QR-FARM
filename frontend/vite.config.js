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
        '**/coverage/**',
        '**/lcov-report/**',
        '**/*.spec.{js,ts}',
        '**/*.test.{js,ts}',
        '**/test-setup.js',
        '**/test-helpers.*',
        '**/__tests__/**',
        '**/__mocks__/**',
        '**/dist/**',
        '**/build/**'
      ],
      tempDirectory: './node_modules/.vitest-coverage-temp',
      // Ensure test files are not included in coverage report
      all: false,
      // Only include source files, not test files
      clean: true
    }
  }
})
