import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { beforeEach, vi } from 'vitest'
import dashboardUsuario from './dashboard-usuario.js'
import authService from '../../services/authService.js'
import { ganadoAPI, vacunacionAPI } from '../../services/api.js'

// Mock de authService
vi.mock('../../services/authService.js', () => ({
  default: {
    isAuthenticated: vi.fn(),
    isUser: vi.fn(),
    getUser: vi.fn(),
    logout: vi.fn()
  }
}))

// Mock de API
vi.mock('../../services/api.js', () => ({
  ganadoAPI: {
    getAll: vi.fn()
  },
  vacunacionAPI: {
    getAll: vi.fn()
  }
}))

describe('dashboard-usuario.js', () => {
  let router
  let wrapper
  // Deterministic counter for crypto mock (resets in beforeEach)
  let mockRandomCounter = 0

  beforeEach(() => {
    vi.clearAllMocks()
    console.error = vi.fn()
    console.log = vi.fn()
    // Reset counter for each test
    mockRandomCounter = 0

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
        { path: '/user/dashboard', component: { template: '<div>Dashboard</div>' } }
      ]
    })

    // Mock de globalThis.window.crypto
    // Using deterministic values for tests instead of Math.random() for security
    globalThis.window = {
      crypto: {
        getRandomValues: vi.fn((buffer) => {
          // Use deterministic counter-based values for reproducible tests
          // This avoids using Math.random() which is not cryptographically secure
          mockRandomCounter += 1
          buffer[0] = (mockRandomCounter * 0x12345678) % 0x100000000
          return buffer
        })
      }
    }
  })

  const createWrapper = (options = {}) => {
    return mount(dashboardUsuario, {
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
      expect(dashboardUsuario).toBeDefined()
      expect(dashboardUsuario.name).toBe('DashboardUsuario')
    })

    it('should have data function', () => {
      expect(typeof dashboardUsuario.data).toBe('function')
      const data = dashboardUsuario.data()
      expect(data).toHaveProperty('userName')
      expect(data).toHaveProperty('estadisticas')
      expect(data.estadisticas).toEqual({
        ganado: 0,
        vacunas: 0,
        salud: 0
      })
    })

    it('should have mounted hook', () => {
      expect(typeof dashboardUsuario.mounted).toBe('function')
    })

    it('should have methods object', () => {
      expect(dashboardUsuario.methods).toBeDefined()
      expect(typeof dashboardUsuario.methods.cargarEstadisticas).toBe('function')
      expect(typeof dashboardUsuario.methods.logout).toBe('function')
    })
  })

  describe('Data Initialization', () => {
    it('should initialize with default values', () => {
      const data = dashboardUsuario.data()
      expect(data.userName).toBe('')
      expect(data.estadisticas.ganado).toBe(0)
      expect(data.estadisticas.vacunas).toBe(0)
      expect(data.estadisticas.salud).toBe(0)
    })
  })

  describe('Mounted Hook', () => {
    it('should redirect to login if not authenticated', async () => {
      authService.isAuthenticated.mockReturnValue(false)
      const pushSpy = vi.spyOn(router, 'push')

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(pushSpy).toHaveBeenCalledWith('/login')
    })

    it('should redirect to login if not user', async () => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.isUser.mockReturnValue(false)
      const pushSpy = vi.spyOn(router, 'push')

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(pushSpy).toHaveBeenCalledWith('/login')
    })

    it('should set userName from user.persona.primer_nombre', async () => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.isUser.mockReturnValue(true)
      authService.getUser.mockReturnValue({
        persona: { primer_nombre: 'Juan' }
      })
      ganadoAPI.getAll.mockResolvedValue({ data: { data: [] } })
      vacunacionAPI.getAll.mockResolvedValue({ data: { data: [] } })

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(wrapper.vm.userName).toBe('Juan')
    })

    it('should set userName to "Usuario" if user has no persona', async () => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.isUser.mockReturnValue(true)
      authService.getUser.mockReturnValue({})
      ganadoAPI.getAll.mockResolvedValue({ data: { data: [] } })
      vacunacionAPI.getAll.mockResolvedValue({ data: { data: [] } })

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(wrapper.vm.userName).toBe('Usuario')
    })

    it('should set userName to "Usuario" if user is null', async () => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.isUser.mockReturnValue(true)
      authService.getUser.mockReturnValue(null)
      ganadoAPI.getAll.mockResolvedValue({ data: { data: [] } })
      vacunacionAPI.getAll.mockResolvedValue({ data: { data: [] } })

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(wrapper.vm.userName).toBe('Usuario')
    })

    it('should call cargarEstadisticas when authenticated and user', async () => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.isUser.mockReturnValue(true)
      authService.getUser.mockReturnValue({})
      ganadoAPI.getAll.mockResolvedValue({ data: { data: [] } })
      vacunacionAPI.getAll.mockResolvedValue({ data: { data: [] } })

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(ganadoAPI.getAll).toHaveBeenCalled()
      expect(vacunacionAPI.getAll).toHaveBeenCalled()
    })
  })

  describe('cargarEstadisticas Method', () => {
    beforeEach(() => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.isUser.mockReturnValue(true)
      authService.getUser.mockReturnValue({ id: 1 })
    })

    it('should load statistics successfully', async () => {
      ganadoAPI.getAll.mockResolvedValue({
        data: { data: [{ id: 1, id_persona: 1 }, { id: 2, id_persona: 2 }, { id: 3, id_persona: 1 }] }
      })
      vacunacionAPI.getAll.mockResolvedValue({
        data: { data: [{ id: 1 }, { id: 2 }] }
      })

      wrapper = createWrapper()
      await wrapper.vm.cargarEstadisticas()

      expect(wrapper.vm.estadisticas.ganado).toBe(2)
      expect(wrapper.vm.estadisticas.vacunas).toBe(2)
      expect(wrapper.vm.estadisticas.salud).toBeGreaterThanOrEqual(80)
      expect(wrapper.vm.estadisticas.salud).toBeLessThanOrEqual(99)
    })

    it('should handle empty responses', async () => {
      ganadoAPI.getAll.mockResolvedValue({ data: { data: [] } })
      vacunacionAPI.getAll.mockResolvedValue({ data: { data: [] } })

      wrapper = createWrapper()
      await wrapper.vm.cargarEstadisticas()

      expect(wrapper.vm.estadisticas.ganado).toBe(0)
      expect(wrapper.vm.estadisticas.vacunas).toBe(0)
      expect(wrapper.vm.estadisticas.salud).toBeGreaterThanOrEqual(80)
    })

    it('should handle responses without data property', async () => {
      ganadoAPI.getAll.mockResolvedValue({ data: {} })
      vacunacionAPI.getAll.mockResolvedValue({ data: {} })

      wrapper = createWrapper()
      await wrapper.vm.cargarEstadisticas()

      expect(wrapper.vm.estadisticas.ganado).toBe(0)
      expect(wrapper.vm.estadisticas.vacunas).toBe(0)
    })

    it('should handle responses without data.data property', async () => {
      ganadoAPI.getAll.mockResolvedValue({ data: { other: [] } })
      vacunacionAPI.getAll.mockResolvedValue({ data: { other: [] } })

      wrapper = createWrapper()
      await wrapper.vm.cargarEstadisticas()

      expect(wrapper.vm.estadisticas.ganado).toBe(0)
      expect(wrapper.vm.estadisticas.vacunas).toBe(0)
    })

    it('should handle errors gracefully', async () => {
      ganadoAPI.getAll.mockRejectedValue(new Error('Network error'))
      vacunacionAPI.getAll.mockResolvedValue({ data: { data: [] } })

      wrapper = createWrapper()
      await wrapper.vm.cargarEstadisticas()

      expect(console.error).toHaveBeenCalled()
      expect(typeof wrapper.vm.estadisticas.salud).toBe('number')
    })

    it('should set salud using generarFraccionAleatoriaDemo between 80 and 99', async () => {
      ganadoAPI.getAll.mockResolvedValue({ data: { data: [] } })
      vacunacionAPI.getAll.mockResolvedValue({ data: { data: [] } })

      wrapper = createWrapper()
      await wrapper.vm.cargarEstadisticas()

      expect(wrapper.vm.estadisticas.salud).toBeGreaterThanOrEqual(80)
      expect(wrapper.vm.estadisticas.salud).toBeLessThanOrEqual(99)
    })

    it('should handle all API errors', async () => {
      ganadoAPI.getAll.mockRejectedValue(new Error('Error 1'))
      vacunacionAPI.getAll.mockRejectedValue(new Error('Error 2'))

      wrapper = createWrapper()
      await wrapper.vm.cargarEstadisticas()

      expect(console.error).toHaveBeenCalled()
      expect(wrapper.vm.estadisticas).toBeDefined()
    })
  })

  describe('logout Method', () => {
    beforeEach(() => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.isUser.mockReturnValue(true)
      authService.getUser.mockReturnValue({})
    })

    it('should call authService.logout', () => {
      wrapper = createWrapper()
      wrapper.vm.logout()

      expect(authService.logout).toHaveBeenCalled()
    })

    it('should redirect to login', () => {
      const pushSpy = vi.spyOn(router, 'push')
      wrapper = createWrapper()
      wrapper.vm.logout()

      expect(pushSpy).toHaveBeenCalledWith('/login')
    })
  })

  describe('generarFraccionAleatoriaDemo Function', () => {
    it('should return a fraction when crypto is available', async () => {
      // The function is called internally in cargarEstadisticas
      ganadoAPI.getAll.mockResolvedValue({ data: { data: [] } })
      vacunacionAPI.getAll.mockResolvedValue({ data: { data: [] } })

      wrapper = createWrapper()
      await wrapper.vm.cargarEstadisticas()

      expect(wrapper.vm.estadisticas.salud).toBeGreaterThanOrEqual(80)
      expect(wrapper.vm.estadisticas.salud).toBeLessThanOrEqual(99)
    })

    it('should handle when crypto is not available', async () => {
      const originalCrypto = globalThis.window.crypto
      globalThis.window.crypto = undefined

      ganadoAPI.getAll.mockResolvedValue({ data: { data: [] } })
      vacunacionAPI.getAll.mockResolvedValue({ data: { data: [] } })

      wrapper = createWrapper()
      await wrapper.vm.cargarEstadisticas()

      // When crypto is not available, should use timestamp fallback
      expect(wrapper.vm.estadisticas.salud).toBeGreaterThanOrEqual(80)
      expect(wrapper.vm.estadisticas.salud).toBeLessThanOrEqual(99)

      globalThis.window.crypto = originalCrypto
    })
  })

  describe('Component Integration', () => {
    it('should mount and initialize correctly', async () => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.isUser.mockReturnValue(true)
      authService.getUser.mockReturnValue({
        id: 1,
        persona: { primer_nombre: 'Test' }
      })
      ganadoAPI.getAll.mockResolvedValue({ data: { data: [{ id: 1, id_persona: 1 }, { id: 2, id_persona: 1 }] } })
      vacunacionAPI.getAll.mockResolvedValue({ data: { data: [1, 2, 3] } })

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(wrapper.vm.userName).toBe('Test')
      expect(wrapper.vm.estadisticas.ganado).toBe(2)
      expect(wrapper.vm.estadisticas.vacunas).toBe(3)
    })
  })

  describe('Edge Cases', () => {
    it('should handle cargarEstadisticas with null user', async () => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.isUser.mockReturnValue(true)
      authService.getUser.mockReturnValue(null)
      ganadoAPI.getAll.mockResolvedValue({ data: { data: [] } })
      vacunacionAPI.getAll.mockResolvedValue({ data: { data: [] } })

      wrapper = createWrapper()
      await wrapper.vm.cargarEstadisticas()

      expect(wrapper.vm.estadisticas.ganado).toBe(0)
      expect(wrapper.vm.estadisticas.vacunas).toBe(0)
    })

    it('should handle cargarEstadisticas with user without id', async () => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.isUser.mockReturnValue(true)
      authService.getUser.mockReturnValue({})
      ganadoAPI.getAll.mockResolvedValue({
        data: { data: [{ id: 1, id_persona: 1 }, { id: 2, id_persona: 2 }] }
      })
      vacunacionAPI.getAll.mockResolvedValue({ data: { data: [] } })

      wrapper = createWrapper()
      await wrapper.vm.cargarEstadisticas()

      // When userId is undefined, filter returns empty array
      expect(wrapper.vm.estadisticas.ganado).toBe(0)
    })

    it('should handle cargarEstadisticas with null ganadoResponse.data', async () => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.isUser.mockReturnValue(true)
      authService.getUser.mockReturnValue({ id: 1 })
      ganadoAPI.getAll.mockResolvedValue({ data: null })
      vacunacionAPI.getAll.mockResolvedValue({ data: { data: [] } })

      wrapper = createWrapper()
      await wrapper.vm.cargarEstadisticas()

      expect(wrapper.vm.estadisticas.ganado).toBe(0)
    })

    it('should handle cargarEstadisticas with null vacunasResponse.data', async () => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.isUser.mockReturnValue(true)
      authService.getUser.mockReturnValue({ id: 1 })
      ganadoAPI.getAll.mockResolvedValue({ data: { data: [] } })
      vacunacionAPI.getAll.mockResolvedValue({ data: null })

      wrapper = createWrapper()
      await wrapper.vm.cargarEstadisticas()

      expect(wrapper.vm.estadisticas.vacunas).toBe(0)
    })

    it('should handle userRole from user.rol.rol', async () => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.isUser.mockReturnValue(true)
      authService.getUser.mockReturnValue({
        persona: { primer_nombre: 'Test' },
        rol: { rol: 'admin' }
      })
      ganadoAPI.getAll.mockResolvedValue({ data: { data: [] } })
      vacunacionAPI.getAll.mockResolvedValue({ data: { data: [] } })

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(wrapper.vm.userRole).toBe('admin')
    })

    it('should handle userRole default when rol is missing', async () => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.isUser.mockReturnValue(true)
      authService.getUser.mockReturnValue({
        persona: { primer_nombre: 'Test' }
      })
      ganadoAPI.getAll.mockResolvedValue({ data: { data: [] } })
      vacunacionAPI.getAll.mockResolvedValue({ data: { data: [] } })

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(wrapper.vm.userRole).toBe('Usuario')
    })
  })
})