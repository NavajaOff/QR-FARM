import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { beforeEach, vi } from 'vitest'
import escanearQRAdmin from './escanear-qr-admin.js'
import authService from '../../services/authService.js'

// Mock de authService
vi.mock('../../services/authService.js', () => ({
  default: {
    isAuthenticated: vi.fn(),
    isAdmin: vi.fn(),
    getUser: vi.fn(),
    logout: vi.fn()
  }
}))

// Mock de Swal
globalThis.Swal = {
  fire: vi.fn((options) => {
    if (options && options.didOpen) {
      options.didOpen()
    }
    return Promise.resolve()
  }),
  showLoading: vi.fn()
}

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

describe('escanear-qr-admin.js', () => {
  let router
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()

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
        { path: '/login', component: { template: '<div>Login</div>' } },
        { path: '/admin/gestionar-animales', component: { template: '<div>Gestionar Animales</div>' } }
      ]
    })
  })

  const createWrapper = (options = {}) => {
    return mount(escanearQRAdmin, {
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
      expect(escanearQRAdmin).toBeDefined()
      expect(escanearQRAdmin.name).toBe('EscanearQRAdmin')
    })

    it('should have escanearQRConfig', () => {
      expect(escanearQRAdmin.escanearQRConfig).toBeDefined()
      expect(escanearQRAdmin.escanearQRConfig.authorize).toBeDefined()
      expect(escanearQRAdmin.escanearQRConfig.successButtonColor).toBe('#007bff')
      expect(escanearQRAdmin.escanearQRConfig.recentScans).toHaveLength(3)
      expect(escanearQRAdmin.escanearQRConfig.estadisticas).toBeDefined()
    })

    it('should have methods object', () => {
      expect(escanearQRAdmin.methods).toBeDefined()
      expect(typeof escanearQRAdmin.methods.verTodosAnimales).toBe('function')
      expect(typeof escanearQRAdmin.methods.generarReporte).toBe('function')
      expect(typeof escanearQRAdmin.methods.exportarDatos).toBe('function')
    })
  })

  describe('escanearQRConfig', () => {
    it('should have correct authorize function', () => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.isAdmin.mockReturnValue(true)
      expect(escanearQRAdmin.escanearQRConfig.authorize(authService)).toBe(true)

      authService.isAuthenticated.mockReturnValue(false)
      expect(escanearQRAdmin.escanearQRConfig.authorize(authService)).toBe(false)

      authService.isAuthenticated.mockReturnValue(true)
      authService.isAdmin.mockReturnValue(false)
      expect(escanearQRAdmin.escanearQRConfig.authorize(authService)).toBe(false)
    })

    it('should have recentScans data', () => {
      expect(escanearQRAdmin.escanearQRConfig.recentScans).toEqual([
        { id: 1, nombre: 'Rosita', fecha: '2025-10-31 10:30' },
        { id: 2, nombre: 'Luna', fecha: '2025-10-30 15:45' },
        { id: 3, nombre: 'Bella', fecha: '2025-10-30 12:20' }
      ])
    })

    it('should have estadisticas data', () => {
      expect(escanearQRAdmin.escanearQRConfig.estadisticas).toEqual({
        totalEscaneos: 24,
        animalesUnicos: 18,
        tasaExito: 96,
        tiempoPromedio: 2.3
      })
    })
  })

  describe('verTodosAnimales Method', () => {
    it('should navigate to /admin/gestionar-animales', () => {
      const pushSpy = vi.spyOn(router, 'push')
      wrapper = createWrapper()
      wrapper.vm.verTodosAnimales()

      expect(pushSpy).toHaveBeenCalledWith('/admin/gestionar-animales')
    })
  })

  describe('generarReporte Method', () => {
    beforeEach(() => {
      vi.useFakeTimers()
    })

    afterEach(() => {
      vi.useRealTimers()
    })

    it('should show loading Swal and then success Swal', async () => {
      wrapper = createWrapper()
      wrapper.vm.generarReporte()

      expect(Swal.fire).toHaveBeenCalledWith(expect.any(Object))
      expect(Swal.showLoading).toHaveBeenCalled()

      await vi.advanceTimersByTime(1500)

      expect(Swal.fire).toHaveBeenCalledWith({
        title: 'Reporte generado',
        text: 'El reporte ha sido generado exitosamente',
        icon: 'success',
        confirmButtonColor: '#007bff'
      })
    })

    it('should not show Swal if Swal is undefined', () => {
      const originalSwal = globalThis.Swal
      globalThis.Swal = undefined

      wrapper = createWrapper()
      wrapper.vm.generarReporte()

      expect(originalSwal.fire).not.toHaveBeenCalled()

      globalThis.Swal = originalSwal
    })
  })

  describe('exportarDatos Method', () => {
    beforeEach(() => {
      vi.useFakeTimers()
    })

    afterEach(() => {
      vi.useRealTimers()
    })

    it('should show loading Swal and then success Swal', async () => {
      wrapper = createWrapper()
      wrapper.vm.exportarDatos()

      expect(Swal.fire).toHaveBeenCalledWith(expect.any(Object))
      expect(Swal.showLoading).toHaveBeenCalled()

      await vi.advanceTimersByTime(2000)

      expect(Swal.fire).toHaveBeenCalledWith({
        title: 'Exportación completada',
        text: 'Los datos han sido exportados exitosamente',
        icon: 'success',
        confirmButtonColor: '#007bff'
      })
    })

    it('should not show Swal if Swal is undefined', () => {
      const originalSwal = globalThis.Swal
      globalThis.Swal = undefined

      wrapper = createWrapper()
      wrapper.vm.exportarDatos()

      expect(originalSwal.fire).not.toHaveBeenCalled()

      globalThis.Swal = originalSwal
    })
  })

  describe('Component Integration', () => {
    it('should mount correctly', () => {
      wrapper = createWrapper()
      expect(wrapper.vm).toBeDefined()
    })
  })
})