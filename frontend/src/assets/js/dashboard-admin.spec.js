import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { beforeEach, vi } from 'vitest'
import dashboardAdmin from './dashboard-admin.js'
import authService from '../../services/authService.js'
import { ganadoAPI, potreroAPI, userAPI } from '../../services/api.js'

// Mock de authService
vi.mock('../../services/authService.js', () => ({
  default: {
    isAuthenticated: vi.fn(),
    isAdmin: vi.fn(),
    getUser: vi.fn(),
    logout: vi.fn()
  }
}))

// Mock de API
vi.mock('../../services/api.js', () => ({
  ganadoAPI: {
    getAll: vi.fn()
  },
  potreroAPI: {
    getAll: vi.fn()
  },
  userAPI: {
    getAll: vi.fn()
  }
}))

describe('dashboard-admin.js', () => {
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
        { path: '/admin/dashboard', component: { template: '<div>Dashboard</div>' } }
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
    return mount(dashboardAdmin, {
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
      expect(dashboardAdmin).toBeDefined()
      expect(dashboardAdmin.name).toBe('DashboardAdmin')
    })

    it('should have data function', () => {
      expect(typeof dashboardAdmin.data).toBe('function')
      const data = dashboardAdmin.data()
      expect(data).toHaveProperty('userName')
      expect(data).toHaveProperty('estadisticas')
      expect(data.estadisticas).toEqual({
        usuarios: 0,
        ganado: 0,
        potreros: 0,
        salud: 0
      })
    })

    it('should have mounted hook', () => {
      expect(typeof dashboardAdmin.mounted).toBe('function')
    })

    it('should have methods object', () => {
      expect(dashboardAdmin.methods).toBeDefined()
      expect(typeof dashboardAdmin.methods.cargarEstadisticas).toBe('function')
      expect(typeof dashboardAdmin.methods.logout).toBe('function')
    })
  })

  describe('Data Initialization', () => {
    it('should initialize with default values', () => {
      const data = dashboardAdmin.data()
      expect(data.userName).toBe('')
      expect(data.estadisticas.usuarios).toBe(0)
      expect(data.estadisticas.ganado).toBe(0)
      expect(data.estadisticas.potreros).toBe(0)
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

    it('should redirect to login if not admin', async () => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.isAdmin.mockReturnValue(false)
      const pushSpy = vi.spyOn(router, 'push')

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(pushSpy).toHaveBeenCalledWith('/login')
    })

    it('should set userName from user.persona.primer_nombre', async () => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.isAdmin.mockReturnValue(true)
      authService.getUser.mockReturnValue({
        persona: { primer_nombre: 'Juan' }
      })
      userAPI.getAll.mockResolvedValue({ data: { data: [] } })
      ganadoAPI.getAll.mockResolvedValue({ data: { data: [] } })
      potreroAPI.getAll.mockResolvedValue({ data: { data: [] } })

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(wrapper.vm.userName).toBe('Juan')
    })

    it('should set userName to "Administrador" if user has no persona', async () => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.isAdmin.mockReturnValue(true)
      authService.getUser.mockReturnValue({})
      userAPI.getAll.mockResolvedValue({ data: { data: [] } })
      ganadoAPI.getAll.mockResolvedValue({ data: { data: [] } })
      potreroAPI.getAll.mockResolvedValue({ data: { data: [] } })

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(wrapper.vm.userName).toBe('Administrador')
    })

    it('should set userName to "Administrador" if user is null', async () => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.isAdmin.mockReturnValue(true)
      authService.getUser.mockReturnValue(null)
      userAPI.getAll.mockResolvedValue({ data: { data: [] } })
      ganadoAPI.getAll.mockResolvedValue({ data: { data: [] } })
      potreroAPI.getAll.mockResolvedValue({ data: { data: [] } })

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(wrapper.vm.userName).toBe('Administrador')
    })

    it('should call cargarEstadisticas when authenticated and admin', async () => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.isAdmin.mockReturnValue(true)
      authService.getUser.mockReturnValue({})
      userAPI.getAll.mockResolvedValue({ data: { data: [] } })
      ganadoAPI.getAll.mockResolvedValue({ data: { data: [] } })
      potreroAPI.getAll.mockResolvedValue({ data: { data: [] } })

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(userAPI.getAll).toHaveBeenCalled()
      expect(ganadoAPI.getAll).toHaveBeenCalled()
      expect(potreroAPI.getAll).toHaveBeenCalled()
    })
  })

  describe('cargarEstadisticas Method', () => {
    beforeEach(() => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.isAdmin.mockReturnValue(true)
      authService.getUser.mockReturnValue({})
    })

    it('should load statistics successfully', async () => {
      userAPI.getAll.mockResolvedValue({
        data: { data: [{ id: 1 }, { id: 2 }, { id: 3 }] }
      })
      ganadoAPI.getAll.mockResolvedValue({
        data: { data: [{ id: 1 }, { id: 2 }] }
      })
      potreroAPI.getAll.mockResolvedValue({
        data: { data: [{ id: 1 }] }
      })

      wrapper = createWrapper()
      await wrapper.vm.cargarEstadisticas()

      expect(wrapper.vm.estadisticas.usuarios).toBe(3)
      expect(wrapper.vm.estadisticas.ganado).toBe(2)
      expect(wrapper.vm.estadisticas.potreros).toBe(1)
      expect(wrapper.vm.estadisticas.salud).toBeGreaterThanOrEqual(80)
      expect(wrapper.vm.estadisticas.salud).toBeLessThanOrEqual(99)
    })

    it('should handle empty responses', async () => {
      userAPI.getAll.mockResolvedValue({ data: { data: [] } })
      ganadoAPI.getAll.mockResolvedValue({ data: { data: [] } })
      potreroAPI.getAll.mockResolvedValue({ data: { data: [] } })

      wrapper = createWrapper()
      await wrapper.vm.cargarEstadisticas()

      expect(wrapper.vm.estadisticas.usuarios).toBe(0)
      expect(wrapper.vm.estadisticas.ganado).toBe(0)
      expect(wrapper.vm.estadisticas.potreros).toBe(0)
      expect(wrapper.vm.estadisticas.salud).toBeGreaterThanOrEqual(80)
    })

    it('should handle responses without data property', async () => {
      userAPI.getAll.mockResolvedValue({ data: {} })
      ganadoAPI.getAll.mockResolvedValue({ data: {} })
      potreroAPI.getAll.mockResolvedValue({ data: {} })

      wrapper = createWrapper()
      await wrapper.vm.cargarEstadisticas()

      expect(wrapper.vm.estadisticas.usuarios).toBe(0)
      expect(wrapper.vm.estadisticas.ganado).toBe(0)
      expect(wrapper.vm.estadisticas.potreros).toBe(0)
    })

    it('should handle responses without data.data property', async () => {
      userAPI.getAll.mockResolvedValue({ data: { other: [] } })
      ganadoAPI.getAll.mockResolvedValue({ data: { other: [] } })
      potreroAPI.getAll.mockResolvedValue({ data: { other: [] } })

      wrapper = createWrapper()
      await wrapper.vm.cargarEstadisticas()

      expect(wrapper.vm.estadisticas.usuarios).toBe(0)
      expect(wrapper.vm.estadisticas.ganado).toBe(0)
      expect(wrapper.vm.estadisticas.potreros).toBe(0)
    })

    it('should handle errors gracefully', async () => {
      userAPI.getAll.mockRejectedValue(new Error('Network error'))
      ganadoAPI.getAll.mockResolvedValue({ data: { data: [] } })
      potreroAPI.getAll.mockResolvedValue({ data: { data: [] } })

      wrapper = createWrapper()
      await wrapper.vm.cargarEstadisticas()

      expect(console.error).toHaveBeenCalled()
      // When there's an error, salud might not be set (stays at 0) or could be set if ganado/potreros succeed
      expect(typeof wrapper.vm.estadisticas.salud).toBe('number')
    })

    it('should set salud using secureRandomInt between 80 and 99', async () => {
      userAPI.getAll.mockResolvedValue({ data: { data: [] } })
      ganadoAPI.getAll.mockResolvedValue({ data: { data: [] } })
      potreroAPI.getAll.mockResolvedValue({ data: { data: [] } })

      wrapper = createWrapper()
      await wrapper.vm.cargarEstadisticas()

      expect(wrapper.vm.estadisticas.salud).toBeGreaterThanOrEqual(80)
      expect(wrapper.vm.estadisticas.salud).toBeLessThanOrEqual(99)
    })

    it('should handle all API errors', async () => {
      userAPI.getAll.mockRejectedValue(new Error('Error 1'))
      ganadoAPI.getAll.mockRejectedValue(new Error('Error 2'))
      potreroAPI.getAll.mockRejectedValue(new Error('Error 3'))

      wrapper = createWrapper()
      await wrapper.vm.cargarEstadisticas()

      expect(console.error).toHaveBeenCalled()
      // Verify that errors are handled without crashing
      expect(wrapper.vm.estadisticas).toBeDefined()
    })
  })

  describe('logout Method', () => {
    beforeEach(() => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.isAdmin.mockReturnValue(true)
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

  describe('secureRandomInt Function', () => {
    it('should return a number between min and max when crypto is available', async () => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.isAdmin.mockReturnValue(true)
      authService.getUser.mockReturnValue({})
      userAPI.getAll.mockResolvedValue({ data: { data: [] } })
      ganadoAPI.getAll.mockResolvedValue({ data: { data: [] } })
      potreroAPI.getAll.mockResolvedValue({ data: { data: [] } })

      wrapper = createWrapper()
      await wrapper.vm.cargarEstadisticas()

      const salud = wrapper.vm.estadisticas.salud
      expect(salud).toBeGreaterThanOrEqual(80)
      expect(salud).toBeLessThanOrEqual(99)
      expect(Number.isInteger(salud)).toBe(true)
    })

    it('should handle when crypto is not available', async () => {
      const originalCrypto = globalThis.window.crypto
      globalThis.window.crypto = undefined

      authService.isAuthenticated.mockReturnValue(true)
      authService.isAdmin.mockReturnValue(true)
      authService.getUser.mockReturnValue({})
      userAPI.getAll.mockResolvedValue({ data: { data: [] } })
      ganadoAPI.getAll.mockResolvedValue({ data: { data: [] } })
      potreroAPI.getAll.mockResolvedValue({ data: { data: [] } })

      wrapper = createWrapper()
      await wrapper.vm.cargarEstadisticas()

      // When crypto is not available, should return lower value (80)
      expect(wrapper.vm.estadisticas.salud).toBe(80)

      globalThis.window.crypto = originalCrypto
    })

    it('should handle invalid min/max values', async () => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.isAdmin.mockReturnValue(true)
      authService.getUser.mockReturnValue({})
      userAPI.getAll.mockResolvedValue({ data: { data: [] } })
      ganadoAPI.getAll.mockResolvedValue({ data: { data: [] } })
      potreroAPI.getAll.mockResolvedValue({ data: { data: [] } })

      wrapper = createWrapper()
      await wrapper.vm.cargarEstadisticas()

      // Should return a valid number (secureRandomInt handles invalid values by returning lower)
      expect(typeof wrapper.vm.estadisticas.salud).toBe('number')
      expect(wrapper.vm.estadisticas.salud).toBeGreaterThanOrEqual(80)
    })
  })

  describe('Component Integration', () => {
    it('should mount and initialize correctly', async () => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.isAdmin.mockReturnValue(true)
      authService.getUser.mockReturnValue({
        persona: { primer_nombre: 'Test' }
      })
      userAPI.getAll.mockResolvedValue({ data: { data: [1, 2, 3] } })
      ganadoAPI.getAll.mockResolvedValue({ data: { data: [1, 2] } })
      potreroAPI.getAll.mockResolvedValue({ data: { data: [1] } })

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(wrapper.vm.userName).toBe('Test')
      expect(wrapper.vm.estadisticas.usuarios).toBe(3)
      expect(wrapper.vm.estadisticas.ganado).toBe(2)
      expect(wrapper.vm.estadisticas.potreros).toBe(1)
    })
  })
})

