import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { beforeEach, vi } from 'vitest'
import dashboardContent from './dashboard-content.js'
import authService from '../../services/authService.js'
import { ganadoAPI, potreroAPI, userAPI, tenantAPI } from '../../services/api.js'

// Mock de authService
vi.mock('../../services/authService.js', () => ({
  default: {
    getRole: vi.fn(),
    getUser: vi.fn()
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
  },
  tenantAPI: {
    getAll: vi.fn(),
    getById: vi.fn()
  }
}))

describe('dashboard-content.js', () => {
  let router
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    console.log = vi.fn()
    console.error = vi.fn()
    console.warn = vi.fn()

    // Mock de globalThis.window.crypto
    globalThis.window = {
      crypto: {
        getRandomValues: vi.fn((buffer) => {
          buffer[0] = Math.floor(Math.random() * 0x100000000)
          return buffer
        })
      },
      addEventListener: vi.fn(),
      removeEventListener: vi.fn()
    }

    // Crear router mock
    router = createRouter({
      history: createWebHistory(),
      routes: [
        { path: '/admin/dashboard', component: { template: '<div>Dashboard</div>' } }
      ]
    })
  })

  const createWrapper = (options = {}) => {
    return mount(dashboardContent, {
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
      expect(dashboardContent).toBeDefined()
      expect(dashboardContent.name).toBe('DashboardContent')
    })

    it('should have data function', () => {
      expect(typeof dashboardContent.data).toBe('function')
      const data = dashboardContent.data()
      expect(data).toHaveProperty('estadisticas')
      expect(data).toHaveProperty('currentTenant')
      expect(data).toHaveProperty('isSuperAdmin')
      expect(data).toHaveProperty('tenants')
      expect(data.estadisticas).toEqual({
        usuarios: 0,
        ganado: 0,
        potreros: 0,
        salud: 0,
        tenants: 0
      })
    })

    it('should have mounted hook', () => {
      expect(typeof dashboardContent.mounted).toBe('function')
    })

    it('should have beforeUnmount hook', () => {
      expect(typeof dashboardContent.beforeUnmount).toBe('function')
    })

    it('should have methods object', () => {
      expect(dashboardContent.methods).toBeDefined()
      expect(typeof dashboardContent.methods.checkUserRole).toBe('function')
      expect(typeof dashboardContent.methods.cargarTenants).toBe('function')
      expect(typeof dashboardContent.methods.cargarTenantActual).toBe('function')
      expect(typeof dashboardContent.methods.onTenantChanged).toBe('function')
      expect(typeof dashboardContent.methods._cargarUsuarios).toBe('function')
      expect(typeof dashboardContent.methods._cargarGanado).toBe('function')
      expect(typeof dashboardContent.methods._cargarPotreros).toBe('function')
      expect(typeof dashboardContent.methods._cargarEstadisticasSuperAdmin).toBe('function')
      expect(typeof dashboardContent.methods._cargarEstadisticasAdminNormal).toBe('function')
      expect(typeof dashboardContent.methods.cargarEstadisticas).toBe('function')
    })
  })

  describe('Data Initialization', () => {
    it('should initialize with default values', () => {
      const data = dashboardContent.data()
      expect(data.estadisticas.usuarios).toBe(0)
      expect(data.estadisticas.ganado).toBe(0)
      expect(data.estadisticas.potreros).toBe(0)
      expect(data.estadisticas.salud).toBe(0)
      expect(data.estadisticas.tenants).toBe(0)
      expect(data.currentTenant).toBeNull()
      expect(data.isSuperAdmin).toBe(false)
      expect(data.tenants).toEqual([])
    })
  })

  describe('Mounted Hook', () => {
    it('should check user role on mount', async () => {
      authService.getRole.mockReturnValue('admin')
      userAPI.getAll.mockResolvedValue({ data: { status: 'success', data: [] } })
      ganadoAPI.getAll.mockResolvedValue({ data: { status: 'success', data: [] } })
      potreroAPI.getAll.mockResolvedValue({ data: { status: 'success', data: [] } })

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(authService.getRole).toHaveBeenCalled()
      expect(console.log).toHaveBeenCalled()
    })

    it('should load tenants for super admin', async () => {
      authService.getRole.mockReturnValue('super_admin')
      tenantAPI.getAll.mockResolvedValue({
        data: { status: 'success', data: [{ id: 1 }, { id: 2 }] }
      })
      userAPI.getAll.mockResolvedValue({ data: { status: 'success', data: [] } })

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(tenantAPI.getAll).toHaveBeenCalledWith(true)
      expect(wrapper.vm.isSuperAdmin).toBe(true)
    })

    it('should load current tenant for normal admin', async () => {
      authService.getRole.mockReturnValue('admin')
      authService.getUser.mockReturnValue({ tenant_id: 1 })
      tenantAPI.getById.mockResolvedValue({
        data: { status: 'success', data: { id: 1, nombre: 'Tenant 1' } }
      })
      userAPI.getAll.mockResolvedValue({ data: { status: 'success', data: [] } })
      ganadoAPI.getAll.mockResolvedValue({ data: { status: 'success', data: [] } })
      potreroAPI.getAll.mockResolvedValue({ data: { status: 'success', data: [] } })

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(tenantAPI.getById).toHaveBeenCalledWith(1)
    })

    it('should add event listener for tenant-selected', async () => {
      authService.getRole.mockReturnValue('admin')
      userAPI.getAll.mockResolvedValue({ data: { status: 'success', data: [] } })
      ganadoAPI.getAll.mockResolvedValue({ data: { status: 'success', data: [] } })
      potreroAPI.getAll.mockResolvedValue({ data: { status: 'success', data: [] } })

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(globalThis.addEventListener).toHaveBeenCalledWith('tenant-selected', expect.any(Function))
    })
  })

  describe('beforeUnmount Hook', () => {
    it('should remove event listener on unmount', async () => {
      authService.getRole.mockReturnValue('admin')
      userAPI.getAll.mockResolvedValue({ data: { status: 'success', data: [] } })
      ganadoAPI.getAll.mockResolvedValue({ data: { status: 'success', data: [] } })
      potreroAPI.getAll.mockResolvedValue({ data: { status: 'success', data: [] } })

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.unmount()

      expect(globalThis.removeEventListener).toHaveBeenCalledWith('tenant-selected', expect.any(Function))
    })
  })

  describe('checkUserRole Method', () => {
    it('should set isSuperAdmin to true for super_admin role', () => {
      authService.getRole.mockReturnValue('super_admin')
      wrapper = createWrapper()
      wrapper.vm.checkUserRole()

      expect(wrapper.vm.isSuperAdmin).toBe(true)
      expect(console.log).toHaveBeenCalled()
    })

    it('should set isSuperAdmin to false for admin role', () => {
      authService.getRole.mockReturnValue('admin')
      wrapper = createWrapper()
      wrapper.vm.checkUserRole()

      expect(wrapper.vm.isSuperAdmin).toBe(false)
    })
  })

  describe('cargarTenants Method', () => {
    beforeEach(() => {
      wrapper = createWrapper()
    })

    it('should load tenants successfully', async () => {
      tenantAPI.getAll.mockResolvedValue({
        data: { status: 'success', data: [{ id: 1 }, { id: 2 }, { id: 3 }] }
      })

      await wrapper.vm.cargarTenants()

      expect(wrapper.vm.tenants).toHaveLength(3)
      expect(wrapper.vm.estadisticas.tenants).toBe(3)
      expect(console.log).toHaveBeenCalled()
    })

    it('should handle empty tenants response', async () => {
      tenantAPI.getAll.mockResolvedValue({
        data: { status: 'success', data: [] }
      })

      await wrapper.vm.cargarTenants()

      expect(wrapper.vm.tenants).toEqual([])
      expect(wrapper.vm.estadisticas.tenants).toBe(0)
    })

    it('should handle response without data property', async () => {
      tenantAPI.getAll.mockResolvedValue({
        data: { status: 'success' }
      })

      await wrapper.vm.cargarTenants()

      expect(wrapper.vm.tenants).toEqual([])
      expect(wrapper.vm.estadisticas.tenants).toBe(0)
    })

    it('should handle response with status not success', async () => {
      tenantAPI.getAll.mockResolvedValue({
        data: { status: 'error', message: 'Failed' }
      })

      await wrapper.vm.cargarTenants()

      expect(wrapper.vm.tenants).toEqual([])
      expect(wrapper.vm.estadisticas.tenants).toBe(0)
      expect(console.warn).toHaveBeenCalled()
    })

    it('should handle errors gracefully', async () => {
      const error = new Error('Network error')
      error.response = { data: { message: 'Error' }, status: 500 }
      tenantAPI.getAll.mockRejectedValue(error)

      await wrapper.vm.cargarTenants()

      expect(wrapper.vm.tenants).toEqual([])
      expect(wrapper.vm.estadisticas.tenants).toBe(0)
      expect(console.error).toHaveBeenCalled()
    })
  })

  describe('cargarTenantActual Method', () => {
    beforeEach(() => {
      wrapper = createWrapper()
    })

    it('should load current tenant successfully', async () => {
      authService.getUser.mockReturnValue({ tenant_id: 1 })
      tenantAPI.getById.mockResolvedValue({
        data: { status: 'success', data: { id: 1, nombre: 'Tenant 1' } }
      })

      await wrapper.vm.cargarTenantActual()

      expect(wrapper.vm.currentTenant).toEqual({ id: 1, nombre: 'Tenant 1' })
    })

    it('should not load tenant if user has no tenant_id', async () => {
      authService.getUser.mockReturnValue({})

      await wrapper.vm.cargarTenantActual()

      expect(tenantAPI.getById).not.toHaveBeenCalled()
      expect(wrapper.vm.currentTenant).toBeNull()
    })

    it('should not load tenant if user is null', async () => {
      authService.getUser.mockReturnValue(null)

      await wrapper.vm.cargarTenantActual()

      expect(tenantAPI.getById).not.toHaveBeenCalled()
    })

    it('should handle errors gracefully', async () => {
      authService.getUser.mockReturnValue({ tenant_id: 1 })
      tenantAPI.getById.mockRejectedValue(new Error('Not found'))

      await wrapper.vm.cargarTenantActual()

      expect(console.warn).toHaveBeenCalled()
    })
  })

  describe('onTenantChanged Method', () => {
    beforeEach(() => {
      wrapper = createWrapper()
      wrapper.vm.cargarEstadisticas = vi.fn()
    })

    it('should reload statistics when tenant changes', () => {
      wrapper.vm.onTenantChanged()

      expect(wrapper.vm.cargarEstadisticas).toHaveBeenCalled()
    })
  })

  describe('_cargarUsuarios Method', () => {
    beforeEach(() => {
      wrapper = createWrapper()
    })

    it('should load usuarios successfully', async () => {
      userAPI.getAll.mockResolvedValue({
        data: { status: 'success', data: [{ id: 1 }, { id: 2 }] }
      })

      await wrapper.vm._cargarUsuarios()

      expect(wrapper.vm.estadisticas.usuarios).toBe(2)
      expect(console.log).toHaveBeenCalled()
    })

    it('should handle response without data property', async () => {
      userAPI.getAll.mockResolvedValue({
        data: { status: 'success' }
      })

      await wrapper.vm._cargarUsuarios()

      expect(wrapper.vm.estadisticas.usuarios).toBe(0)
    })

    it('should handle response with status not success', async () => {
      userAPI.getAll.mockResolvedValue({
        data: { status: 'error' }
      })

      await wrapper.vm._cargarUsuarios()

      expect(wrapper.vm.estadisticas.usuarios).toBe(0)
      expect(console.warn).toHaveBeenCalled()
    })

    it('should handle errors gracefully', async () => {
      const error = new Error('Network error')
      error.response = { data: { message: 'Error' }, status: 500 }
      userAPI.getAll.mockRejectedValue(error)

      await wrapper.vm._cargarUsuarios()

      expect(wrapper.vm.estadisticas.usuarios).toBe(0)
      expect(console.error).toHaveBeenCalled()
    })
  })

  describe('_cargarGanado Method', () => {
    beforeEach(() => {
      wrapper = createWrapper()
    })

    it('should load ganado successfully', async () => {
      ganadoAPI.getAll.mockResolvedValue({
        data: { status: 'success', data: [{ id: 1 }, { id: 2 }, { id: 3 }] }
      })

      await wrapper.vm._cargarGanado()

      expect(wrapper.vm.estadisticas.ganado).toBe(3)
    })

    it('should handle response without data property', async () => {
      ganadoAPI.getAll.mockResolvedValue({
        data: { status: 'success' }
      })

      await wrapper.vm._cargarGanado()

      expect(wrapper.vm.estadisticas.ganado).toBe(0)
    })

    it('should handle response with status not success', async () => {
      ganadoAPI.getAll.mockResolvedValue({
        data: { status: 'error' }
      })

      await wrapper.vm._cargarGanado()

      expect(wrapper.vm.estadisticas.ganado).toBe(0)
      expect(console.warn).toHaveBeenCalled()
    })

    it('should handle errors gracefully', async () => {
      const error = new Error('Network error')
      error.response = { data: { message: 'Error' }, status: 500 }
      ganadoAPI.getAll.mockRejectedValue(error)

      await wrapper.vm._cargarGanado()

      expect(wrapper.vm.estadisticas.ganado).toBe(0)
      expect(console.error).toHaveBeenCalled()
    })
  })

  describe('_cargarPotreros Method', () => {
    beforeEach(() => {
      wrapper = createWrapper()
    })

    it('should load potreros successfully', async () => {
      potreroAPI.getAll.mockResolvedValue({
        data: { status: 'success', data: [{ id: 1 }, { id: 2 }] }
      })

      await wrapper.vm._cargarPotreros()

      expect(wrapper.vm.estadisticas.potreros).toBe(2)
    })

    it('should handle response without data property', async () => {
      potreroAPI.getAll.mockResolvedValue({
        data: { status: 'success' }
      })

      await wrapper.vm._cargarPotreros()

      expect(wrapper.vm.estadisticas.potreros).toBe(0)
    })

    it('should handle response with status not success', async () => {
      potreroAPI.getAll.mockResolvedValue({
        data: { status: 'error' }
      })

      await wrapper.vm._cargarPotreros()

      expect(wrapper.vm.estadisticas.potreros).toBe(0)
      expect(console.warn).toHaveBeenCalled()
    })

    it('should handle errors gracefully', async () => {
      const error = new Error('Network error')
      error.response = { data: { message: 'Error' }, status: 500 }
      potreroAPI.getAll.mockRejectedValue(error)

      await wrapper.vm._cargarPotreros()

      expect(wrapper.vm.estadisticas.potreros).toBe(0)
      expect(console.error).toHaveBeenCalled()
    })
  })

  describe('_cargarEstadisticasSuperAdmin Method', () => {
    beforeEach(() => {
      wrapper = createWrapper()
      wrapper.vm.isSuperAdmin = true
    })

    it('should load statistics for super admin with selected tenant', async () => {
      localStorage.setItem('qr_farm_selected_tenant_id', '123')
      userAPI.getAll.mockResolvedValue({
        data: { status: 'success', data: [{ id: 1 }] }
      })
      ganadoAPI.getAll.mockResolvedValue({
        data: { status: 'success', data: [{ id: 1 }, { id: 2 }] }
      })
      potreroAPI.getAll.mockResolvedValue({
        data: { status: 'success', data: [{ id: 1 }] }
      })

      await wrapper.vm._cargarEstadisticasSuperAdmin()

      expect(wrapper.vm.estadisticas.usuarios).toBe(1)
      expect(wrapper.vm.estadisticas.ganado).toBe(2)
      expect(wrapper.vm.estadisticas.potreros).toBe(1)
      expect(console.log).toHaveBeenCalled()
    })

    it('should set ganado and potreros to 0 when no tenant selected', async () => {
      localStorage.removeItem('qr_farm_selected_tenant_id')
      userAPI.getAll.mockResolvedValue({
        data: { status: 'success', data: [{ id: 1 }] }
      })

      await wrapper.vm._cargarEstadisticasSuperAdmin()

      expect(wrapper.vm.estadisticas.usuarios).toBe(1)
      expect(wrapper.vm.estadisticas.ganado).toBe(0)
      expect(wrapper.vm.estadisticas.potreros).toBe(0)
      expect(console.log).toHaveBeenCalled()
    })
  })

  describe('_cargarEstadisticasAdminNormal Method', () => {
    beforeEach(() => {
      wrapper = createWrapper()
      wrapper.vm.isSuperAdmin = false
    })

    it('should load statistics for normal admin', async () => {
      userAPI.getAll.mockResolvedValue({
        data: { status: 'success', data: [{ id: 1 }] }
      })
      ganadoAPI.getAll.mockResolvedValue({
        data: { status: 'success', data: [{ id: 1 }, { id: 2 }] }
      })
      potreroAPI.getAll.mockResolvedValue({
        data: { status: 'success', data: [{ id: 1 }] }
      })

      await wrapper.vm._cargarEstadisticasAdminNormal()

      expect(wrapper.vm.estadisticas.usuarios).toBe(1)
      expect(wrapper.vm.estadisticas.ganado).toBe(2)
      expect(wrapper.vm.estadisticas.potreros).toBe(1)
      expect(wrapper.vm.estadisticas.salud).toBeGreaterThanOrEqual(80)
      expect(wrapper.vm.estadisticas.salud).toBeLessThanOrEqual(99)
      expect(console.log).toHaveBeenCalled()
    })
  })

  describe('cargarEstadisticas Method', () => {
    beforeEach(() => {
      wrapper = createWrapper()
    })

    it('should call _cargarEstadisticasSuperAdmin for super admin', async () => {
      wrapper.vm.isSuperAdmin = true
      wrapper.vm._cargarEstadisticasSuperAdmin = vi.fn().mockResolvedValue()
      userAPI.getAll.mockResolvedValue({
        data: { status: 'success', data: [] }
      })

      await wrapper.vm.cargarEstadisticas()

      expect(wrapper.vm._cargarEstadisticasSuperAdmin).toHaveBeenCalled()
      expect(console.log).toHaveBeenCalled()
    })

    it('should call _cargarEstadisticasAdminNormal for normal admin', async () => {
      wrapper.vm.isSuperAdmin = false
      wrapper.vm._cargarEstadisticasAdminNormal = vi.fn().mockResolvedValue()

      await wrapper.vm.cargarEstadisticas()

      expect(wrapper.vm._cargarEstadisticasAdminNormal).toHaveBeenCalled()
    })

    it('should handle errors and set default values', async () => {
      wrapper.vm.isSuperAdmin = false
      wrapper.vm._cargarEstadisticasAdminNormal = vi.fn().mockRejectedValue(new Error('Test error'))

      await wrapper.vm.cargarEstadisticas()

      expect(wrapper.vm.estadisticas).toEqual({
        usuarios: 0,
        ganado: 0,
        potreros: 0,
        salud: 85,
        tenants: 0
      })
      expect(console.error).toHaveBeenCalled()
    })
  })

  describe('secureRandomInt Function', () => {
    it('should return a number between min and max when crypto is available', async () => {
      wrapper = createWrapper()
      wrapper.vm.isSuperAdmin = false
      userAPI.getAll.mockResolvedValue({ data: { status: 'success', data: [] } })
      ganadoAPI.getAll.mockResolvedValue({ data: { status: 'success', data: [] } })
      potreroAPI.getAll.mockResolvedValue({ data: { status: 'success', data: [] } })

      await wrapper.vm._cargarEstadisticasAdminNormal()

      expect(wrapper.vm.estadisticas.salud).toBeGreaterThanOrEqual(80)
      expect(wrapper.vm.estadisticas.salud).toBeLessThanOrEqual(99)
      expect(Number.isInteger(wrapper.vm.estadisticas.salud)).toBe(true)
    })

    it('should return lower value when crypto is not available', () => {
      const originalWindow = globalThis.window
      globalThis.window = undefined

      wrapper = createWrapper()
      wrapper.vm.isSuperAdmin = false
      userAPI.getAll.mockResolvedValue({ data: { status: 'success', data: [] } })
      ganadoAPI.getAll.mockResolvedValue({ data: { status: 'success', data: [] } })
      potreroAPI.getAll.mockResolvedValue({ data: { status: 'success', data: [] } })

      wrapper.vm._cargarEstadisticasAdminNormal().then(() => {
        expect(wrapper.vm.estadisticas.salud).toBe(80)
      })

      globalThis.window = originalWindow
    })
  })
})

