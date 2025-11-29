import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { beforeEach, vi } from 'vitest'
import GestionarUsuarios from './GestionarUsuarios.vue'
import gestionarUsuarios from '../../assets/js/gestionar-usuarios.js'
import { useUsuarios } from '../../composables/useUsuarios.js'
import { useTenants } from '../../composables/useTenants.js'
import authService from '../../services/authService.js'

// Mock del componente JS
vi.mock('../../assets/js/gestionar-usuarios.js', () => ({
  default: {
    name: 'GestionarUsuarios',
    setup: vi.fn(),
    data: vi.fn(() => ({
      showAddUserModal: false,
      showEditModal: false,
      creatingUser: false,
      addForm: {},
      editForm: {},
      originalEditData: null,
      editingUserId: null
    })),
    computed: {
      isCurrentUserAdmin: vi.fn(() => true),
      isSuperAdmin: vi.fn(() => false)
    },
    mounted: vi.fn(),
    methods: {
      openAddModal: vi.fn(),
      closeAddModal: vi.fn(),
      createUser: vi.fn(),
      editUser: vi.fn(),
      updateUser: vi.fn(),
      toggleUserStatus: vi.fn()
    }
  }
}))

// Mock de composables
vi.mock('../../composables/useUsuarios.js', () => ({
  useUsuarios: vi.fn()
}))

vi.mock('../../composables/useTenants.js', () => ({
  useTenants: vi.fn()
}))

// Mock de authService
vi.mock('../../services/authService.js', () => ({
  default: {
    isAdmin: vi.fn(),
    getRole: vi.fn()
  }
}))

describe('GestionarUsuarios.vue', () => {
  let router
  let wrapper
  let mockUsuarios
  let mockTenants

  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    console.log = vi.fn()

    // Mock de location
    globalThis.location = {
      pathname: '/',
      search: '',
      hash: ''
    }

    // Setup mocks
    mockUsuarios = {
      usuarios: { value: [] },
      loading: { value: false },
      error: { value: null },
      cargarUsuarios: vi.fn().mockResolvedValue(),
      actualizarUsuario: vi.fn().mockResolvedValue({ success: true }),
      cambiarEstadoUsuario: vi.fn().mockResolvedValue({ success: true })
    }

    mockTenants = {
      tenants: { value: [] },
      loading: { value: false },
      cargarTenants: vi.fn().mockResolvedValue()
    }

    useUsuarios.mockReturnValue(mockUsuarios)
    useTenants.mockReturnValue(mockTenants)

    authService.isAdmin.mockReturnValue(true)
    authService.getRole.mockReturnValue('admin')

    router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/admin/gestionar-usuarios', component: GestionarUsuarios }
      ]
    })
  })

  const createWrapper = (options = {}) => {
    return mount(GestionarUsuarios, {
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
      expect(wrapper.text()).toContain('Gestión de Usuarios')
    })

    it('should have add user button', () => {
      wrapper = createWrapper()
      const button = wrapper.find('button.btn-primary')
      expect(button.exists()).toBe(true)
      expect(button.text()).toContain('Agregar usuario')
    })
  })

  describe('User Table', () => {
    it('should have table structure', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      // Verify table structure exists
      const table = wrapper.find('table')
      expect(table.exists()).toBe(true)
    })

    it('should have table headers', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      // Verify table headers exist
      const headers = wrapper.findAll('th')
      expect(headers.length).toBeGreaterThan(0)
    })
  })

  describe('User Actions', () => {
    it('should render user table structure', async () => {
      mockUsuarios.usuarios.value = [
        { id: 1, nombre: 'Usuario 1', email: 'user1@example.com', rol: 'admin', estado: 'activo' }
      ]

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      // Verify table structure exists
      const table = wrapper.find('table')
      expect(table.exists()).toBe(true)
    })

    it('should have table headers', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      // Verify table headers exist
      const headers = wrapper.findAll('th')
      expect(headers.length).toBeGreaterThan(0)
    })
  })
})

