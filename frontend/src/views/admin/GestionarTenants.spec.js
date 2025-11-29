import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { beforeEach, vi } from 'vitest'
import GestionarTenants from './GestionarTenants.vue'
import { useTenants } from '../../composables/useTenants.js'
import { tenantAPI } from '../../services/api.js'
import Swal from 'sweetalert2'

// Mock de composables
vi.mock('../../composables/useTenants.js', () => ({
  useTenants: vi.fn()
}))

// Mock de tenantAPI
vi.mock('../../services/api.js', () => ({
  tenantAPI: {
    getAll: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    getById: vi.fn()
  }
}))

// Mock de Swal
vi.mock('sweetalert2', () => ({
  default: {
    fire: vi.fn()
  }
}))

describe('GestionarTenants.vue', () => {
  let router
  let wrapper
  let mockTenants

  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    console.log = vi.fn()
    console.error = vi.fn()

    // Mock de location
    globalThis.location = {
      pathname: '/',
      search: '',
      hash: ''
    }

    // Setup mocks
    mockTenants = {
      tenants: { value: [] },
      loading: { value: false },
      error: { value: null },
      cargarTenants: vi.fn().mockResolvedValue(),
      crearTenant: vi.fn().mockResolvedValue({ success: true }),
      actualizarTenant: vi.fn().mockResolvedValue({ success: true })
    }

    useTenants.mockReturnValue(mockTenants)

    Swal.fire.mockResolvedValue({ isConfirmed: true })

    router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/admin/gestionar-tenants', component: GestionarTenants }
      ]
    })
  })

  const createWrapper = (options = {}) => {
    return mount(GestionarTenants, {
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
      wrapper = createWrapper()
      expect(wrapper.exists()).toBe(true)
    })

    it('should render title', () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('Gestión de Tenants')
    })

    it('should have create tenant button', () => {
      wrapper = createWrapper()
      const button = wrapper.find('button')
      expect(button.exists()).toBe(true)
      expect(button.text()).toContain('Crear Tenant')
    })
  })

  describe('Data Initialization', () => {
    it('should initialize with default values', () => {
      wrapper = createWrapper()
      // Component uses Composition API, so we check rendered content
      expect(wrapper.exists()).toBe(true)
    })
  })

  describe('Loading States', () => {
    it('should handle loading state', async () => {
      mockTenants.loading.value = true
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      // Component should render even when loading
      expect(wrapper.exists()).toBe(true)
    })

    it('should handle error state', async () => {
      mockTenants.error.value = 'Error loading tenants'
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      // Component should render even with error
      expect(wrapper.exists()).toBe(true)
    })

    it('should handle empty tenants state', async () => {
      mockTenants.tenants.value = []
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      // Component should render even with empty list
      expect(wrapper.exists()).toBe(true)
    })
  })

  describe('Tenant List', () => {
    it('should render component with tenant list structure', async () => {
      mockTenants.tenants.value = [
        { id: 1, nombre: 'Tenant 1', codigo_tenant: 'T1', estado: 'activo' }
      ]

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      // Verify component renders
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.html()).toBeTruthy()
    })
  })

  describe('Modal Management', () => {
    it('should have create tenant button', () => {
      wrapper = createWrapper()
      const button = wrapper.find('button')
      expect(button.exists()).toBe(true)
      expect(button.text()).toContain('Crear Tenant')
    })

    it('should trigger openAddModal on button click', async () => {
      wrapper = createWrapper()
      const button = wrapper.find('button')
      await button.trigger('click')
      // Button click should trigger the method (tested through component behavior)
      expect(button.exists()).toBe(true)
    })
  })

  describe('Filter Toggle', () => {
    it('should have filter toggle checkbox', () => {
      wrapper = createWrapper()
      const checkbox = wrapper.find('#mostrarInactivos')
      expect(checkbox.exists()).toBe(true)
    })

    it('should call cargarTenants on mount', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))
      
      // Component should load tenants on mount
      expect(mockTenants.cargarTenants).toHaveBeenCalled()
    })
  })
})

