import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { beforeEach, vi } from 'vitest'
import escanearQRUsuario from './escanear-qr-usuario.js'
import authService from '../../services/authService.js'

// Mock de authService
vi.mock('../../services/authService.js', () => ({
  default: {
    isAuthenticated: vi.fn(),
    isUser: vi.fn(),
    getUser: vi.fn(),
    logout: vi.fn()
  }
}))

// Mock de escanear-qr-base.js
vi.mock('./escanear-qr-base.js', () => ({
  escanearQRBase: {
    data() {
      return {
        isScanning: false,
        userName: 'Usuario',
        recentScans: [],
        estadisticas: null
      }
    },
    mounted() {
      // Mock mounted
    },
    methods: {
      iniciarEscaneo: vi.fn(),
      subirImagen: vi.fn(),
      handleFileUpload: vi.fn()
    }
  }
}))

describe('escanear-qr-usuario.js', () => {
  let router
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    console.error = vi.fn()
    console.log = vi.fn()

    // Mock de location para createMemoryHistory
    globalThis.location = {
      pathname: '/',
      search: '',
      hash: ''
    }

    // Crear router mock con createMemoryHistory
    router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/login', component: { template: '<div>Login</div>' } }
      ]
    })
  })

  const createWrapper = (options = {}) => {
    return mount(escanearQRUsuario, {
      global: {
        plugins: [router],
        mocks: {
          $router: router
        }
      },
      ...options
    })
  }

  describe('Component Definition', () => {
    it('should export a Vue component', () => {
      expect(escanearQRUsuario).toBeDefined()
      expect(escanearQRUsuario.name).toBe('EscanearQR')
    })

    it('should have escanearQRConfig', () => {
      expect(escanearQRUsuario.escanearQRConfig).toBeDefined()
      expect(escanearQRUsuario.escanearQRConfig.authorize).toBeDefined()
      expect(escanearQRUsuario.escanearQRConfig.onAuthorized).toBeDefined()
      expect(escanearQRUsuario.escanearQRConfig.successButtonColor).toBe('#28a745')
      expect(escanearQRUsuario.escanearQRConfig.recentScans).toHaveLength(2)
    })

    it('should have methods object', () => {
      expect(escanearQRUsuario.methods).toBeDefined()
    })
  })

  describe('escanearQRConfig', () => {
    it('should have correct authorize function', () => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.isUser.mockReturnValue(true)
      expect(escanearQRUsuario.escanearQRConfig.authorize(authService)).toBe(true)

      authService.isAuthenticated.mockReturnValue(false)
      expect(escanearQRUsuario.escanearQRConfig.authorize(authService)).toBe(false)

      authService.isAuthenticated.mockReturnValue(true)
      authService.isUser.mockReturnValue(false)
      expect(escanearQRUsuario.escanearQRConfig.authorize(authService)).toBe(false)
    })

    it('should have onAuthorized function that sets userName', () => {
      authService.getUser.mockReturnValue({
        persona: { primer_nombre: 'Juan' }
      })

      const mockThis = { userName: '' }
      escanearQRUsuario.escanearQRConfig.onAuthorized.call(mockThis, authService)

      expect(mockThis.userName).toBe('Juan')
    })

    it('should set userName to "Usuario" if no persona', () => {
      authService.getUser.mockReturnValue({})

      const mockThis = { userName: '' }
      escanearQRUsuario.escanearQRConfig.onAuthorized.call(mockThis, authService)

      expect(mockThis.userName).toBe('Usuario')
    })

    it('should have recentScans data', () => {
      expect(escanearQRUsuario.escanearQRConfig.recentScans).toEqual([
        { id: 1, nombre: 'Rosita', fecha: '2025-10-31 10:30' },
        { id: 2, nombre: 'Luna', fecha: '2025-10-30 15:45' }
      ])
    })
  })

  describe('Component Integration', () => {
    it('should mount correctly', () => {
      wrapper = createWrapper()
      expect(wrapper.vm).toBeDefined()
    })
  })
})