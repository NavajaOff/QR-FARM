import { expect, vi } from 'vitest'
import * as matchers from '@testing-library/jest-dom/matchers'

// Extender expect con matchers de jest-dom
expect.extend(matchers)

// Mock de import.meta.env
vi.stubGlobal('import.meta', {
  env: {
    VITE_BACKEND_URL: 'http://localhost:5000'
  }
})

// Mock de window.matchMedia para evitar errores de Swal
Object.defineProperty(globalThis.window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

// Mock de Swal
globalThis.Swal = {
  fire: vi.fn().mockResolvedValue({ isConfirmed: true }),
  showLoading: vi.fn()
}