import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { beforeEach, vi } from 'vitest'
import DashboardContent from './DashboardContent.vue'
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

describe('DashboardContent.vue', () => {
  let router
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    console.log = vi.fn()
    console.error = vi.fn()
    console.warn = vi.fn()

    // Mock de location
    globalThis.location = {
      pathname: '/',
      search: '',
      hash: ''
    }

    // Mock de globalThis.window.crypto
    let mockRandomCounter = 0
    globalThis.window = {
      crypto: {
        getRandomValues: vi.fn((buffer) => {
          mockRandomCounter += 1
          buffer[0] = (mockRandomCounter * 0x12345678) % 0x100000000
          return buffer
        })
      },
      addEventListener: vi.fn(),
      removeEventListener: vi.fn()
    }
    globalThis.addEventListener = vi.fn()
    globalThis.removeEventListener = vi.fn()

    router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/admin/dashboard', component: DashboardContent }
      ]
    })
  })

  const createWrapper = (options = {}) => {
    return mount(DashboardContent, {
      global: {
        plugins: [router],
        mocks: {
          $router: router
        }
      },
      ...options
    })
  }

  describe('Component Mounting', () => {
    it('should mount correctly', () => {
      authService.getRole.mockReturnValue('admin')
      authService.getUser.mockReturnValue({ tenant_id: 1 })
      userAPI.getAll.mockResolvedValue({ data: { status: 'success', data: [] } })
      ganadoAPI.getAll.mockResolvedValue({ data: { status: 'success', data: [] } })
      potreroAPI.getAll.mockResolvedValue({ data: { status: 'success', data: [] } })

      wrapper = createWrapper()
      expect(wrapper.exists()).toBe(true)
    })

    it('should render title', () => {
      authService.getRole.mockReturnValue('admin')
      authService.getUser.mockReturnValue({ tenant_id: 1 })
      userAPI.getAll.mockResolvedValue({ data: { status: 'success', data: [] } })
      ganadoAPI.getAll.mockResolvedValue({ data: { status: 'success', data: [] } })
      potreroAPI.getAll.mockResolvedValue({ data: { status: 'success', data: [] } })

      wrapper = createWrapper()
      expect(wrapper.text()).toContain('Panel de Administración')
    })
  })

  describe('Super Admin View', () => {
    it('should show super admin welcome message', async () => {
      authService.getRole.mockReturnValue('super_admin')
      tenantAPI.getAll.mockResolvedValue({
        data: { status: 'success', data: [] }
      })
      userAPI.getAll.mockResolvedValue({ data: { status: 'success', data: [] } })

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(wrapper.vm.isSuperAdmin).toBe(true)
      expect(wrapper.text()).toContain('Super Administrador')
    })

    it('should show TenantSelector for super admin', async () => {
      authService.getRole.mockReturnValue('super_admin')
      tenantAPI.getAll.mockResolvedValue({
        data: { status: 'success', data: [] }
      })
      userAPI.getAll.mockResolvedValue({ data: { status: 'success', data: [] } })

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      const tenantSelector = wrapper.findComponent({ name: 'TenantSelector' })
      expect(tenantSelector.exists()).toBe(true)
    })
  })

  describe('Normal Admin View', () => {
    it('should show tenant information for normal admin', async () => {
      authService.getRole.mockReturnValue('admin')
      authService.getUser.mockReturnValue({ tenant_id: 1 })
      tenantAPI.getById.mockResolvedValue({
        data: { status: 'success', data: { id: 1, nombre: 'Test Tenant', codigo_tenant: 'TEST' } }
      })
      userAPI.getAll.mockResolvedValue({ data: { status: 'success', data: [] } })
      ganadoAPI.getAll.mockResolvedValue({ data: { status: 'success', data: [] } })
      potreroAPI.getAll.mockResolvedValue({ data: { status: 'success', data: [] } })

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(wrapper.vm.isSuperAdmin).toBe(false)
      expect(wrapper.vm.currentTenant).toBeDefined()
    })

    it('should show statistics cards for normal admin', async () => {
      authService.getRole.mockReturnValue('admin')
      authService.getUser.mockReturnValue({ tenant_id: 1 })
      tenantAPI.getById.mockResolvedValue({
        data: { status: 'success', data: { id: 1, nombre: 'Test Tenant' } }
      })
      userAPI.getAll.mockResolvedValue({
        data: { status: 'success', data: [{ id: 1 }, { id: 2 }] }
      })
      ganadoAPI.getAll.mockResolvedValue({
        data: { status: 'success', data: [{ id: 1 }] }
      })
      potreroAPI.getAll.mockResolvedValue({
        data: { status: 'success', data: [{ id: 1 }] }
      })

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(wrapper.text()).toContain('Usuarios Registrados')
      expect(wrapper.text()).toContain('Total Ganado')
      expect(wrapper.text()).toContain('Potreros')
    })
  })

  describe('Statistics Loading', () => {
    it('should load statistics on mount', async () => {
      authService.getRole.mockReturnValue('admin')
      authService.getUser.mockReturnValue({ tenant_id: 1 })
      tenantAPI.getById.mockResolvedValue({
        data: { status: 'success', data: { id: 1, nombre: 'Test Tenant' } }
      })
      userAPI.getAll.mockResolvedValue({ data: { status: 'success', data: [] } })
      ganadoAPI.getAll.mockResolvedValue({ data: { status: 'success', data: [] } })
      potreroAPI.getAll.mockResolvedValue({ data: { status: 'success', data: [] } })

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(userAPI.getAll).toHaveBeenCalled()
      expect(ganadoAPI.getAll).toHaveBeenCalled()
      expect(potreroAPI.getAll).toHaveBeenCalled()
    })
  })
})

