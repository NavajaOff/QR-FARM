import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { beforeEach, vi } from 'vitest'
import gestionarUsuarios from './gestionar-usuarios.js'
import { useUsuarios } from '../../composables/useUsuarios.js'
import { useTenants } from '../../composables/useTenants.js'
import authService from '../../services/authService.js'
import { authAPI } from '../../services/api.js'
import Swal from 'sweetalert2'

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

// Mock de authAPI
vi.mock('../../services/api.js', () => ({
  authAPI: {
    register: vi.fn()
  }
}))

// Mock de Swal
vi.mock('sweetalert2', () => ({
  default: {
    fire: vi.fn()
  }
}))

describe('gestionar-usuarios.js', () => {
  let router
  let wrapper
  let mockUsuarios
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

    Swal.fire.mockResolvedValue({ isConfirmed: true })

    router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/admin/gestionar-usuarios', component: gestionarUsuarios }
      ]
    })
  })

  const createWrapper = (options = {}) => {
    return mount(gestionarUsuarios, {
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
      expect(gestionarUsuarios).toBeDefined()
      expect(gestionarUsuarios.name).toBe('GestionarUsuarios')
    })

    it('should have setup function', () => {
      expect(typeof gestionarUsuarios.setup).toBe('function')
    })

    it('should have data function', () => {
      expect(typeof gestionarUsuarios.data).toBe('function')
      const data = gestionarUsuarios.data()
      expect(data).toHaveProperty('showAddUserModal')
      expect(data).toHaveProperty('showEditModal')
      expect(data).toHaveProperty('addForm')
      expect(data).toHaveProperty('editForm')
    })

    it('should have computed properties', () => {
      expect(gestionarUsuarios.computed).toBeDefined()
      expect(typeof gestionarUsuarios.computed.isCurrentUserAdmin).toBe('function')
      expect(typeof gestionarUsuarios.computed.isSuperAdmin).toBe('function')
    })

    it('should have mounted hook', () => {
      expect(typeof gestionarUsuarios.mounted).toBe('function')
    })

    it('should have methods', () => {
      expect(gestionarUsuarios.methods).toBeDefined()
      expect(typeof gestionarUsuarios.methods.openAddModal).toBe('function')
      expect(typeof gestionarUsuarios.methods.createUser).toBe('function')
      expect(typeof gestionarUsuarios.methods.editUser).toBe('function')
      expect(typeof gestionarUsuarios.methods.updateUser).toBe('function')
    })
  })

  describe('Computed Properties', () => {
    it('should return isCurrentUserAdmin from authService', () => {
      authService.isAdmin.mockReturnValue(true)
      const instance = createWrapper()
      expect(instance.vm.isCurrentUserAdmin).toBe(true)
    })

    it('should return isSuperAdmin based on role', () => {
      authService.getRole.mockReturnValue('super_admin')
      const instance = createWrapper()
      expect(instance.vm.isSuperAdmin).toBe(true)
    })
  })

  describe('Mounted Hook', () => {
    it('should load usuarios on mount', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(mockUsuarios.cargarUsuarios).toHaveBeenCalled()
    })

    it('should load tenants if super admin', async () => {
      authService.getRole.mockReturnValue('super_admin')
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(mockTenants.cargarTenants).toHaveBeenCalledWith(true)
    })

    it('should not load tenants if not super admin', async () => {
      authService.getRole.mockReturnValue('admin')
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(mockTenants.cargarTenants).not.toHaveBeenCalled()
    })
  })

  describe('resolveRoleId', () => {
    it('should resolve role from id_rol', () => {
      wrapper = createWrapper()
      const usuario = { id_rol: 1 }
      const roleId = wrapper.vm.resolveRoleId(usuario)
      expect(roleId).toBe(1)
    })

    it('should resolve role from persona.id_rol', () => {
      wrapper = createWrapper()
      const usuario = { persona: { id_rol: 2 } }
      const roleId = wrapper.vm.resolveRoleId(usuario)
      expect(roleId).toBe(2)
    })

    it('should resolve role from rol.id', () => {
      wrapper = createWrapper()
      const usuario = { rol: { id: 1 } }
      const roleId = wrapper.vm.resolveRoleId(usuario)
      expect(roleId).toBe(1)
    })

    it('should resolve role from rol string (admin)', () => {
      wrapper = createWrapper()
      const usuario = { rol: 'admin' }
      const roleId = wrapper.vm.resolveRoleId(usuario)
      expect(roleId).toBe(1)
    })

    it('should resolve role from rol string (usuario)', () => {
      wrapper = createWrapper()
      const usuario = { rol: 'usuario' }
      const roleId = wrapper.vm.resolveRoleId(usuario)
      expect(roleId).toBe(2)
    })

    it('should return default role 2 when no role found', () => {
      wrapper = createWrapper()
      const usuario = {}
      const roleId = wrapper.vm.resolveRoleId(usuario)
      expect(roleId).toBe(2)
    })
  })

  describe('Modal Management', () => {
    it('should open add modal', () => {
      wrapper = createWrapper()
      wrapper.vm.openAddModal()
      expect(wrapper.vm.showAddUserModal).toBe(true)
    })

    it('should close add modal', () => {
      wrapper = createWrapper()
      wrapper.vm.showAddUserModal = true
      wrapper.vm.closeAddModal()
      expect(wrapper.vm.showAddUserModal).toBe(false)
    })

    it('should reset add form', () => {
      wrapper = createWrapper()
      wrapper.vm.addForm.primer_nombre = 'Test'
      wrapper.vm.resetAddForm()
      expect(wrapper.vm.addForm.primer_nombre).toBe('')
    })
  })

  describe('createUser', () => {
    it('should validate required fields', async () => {
      wrapper = createWrapper()
      wrapper.vm.addForm.primer_nombre = ''
      
      await wrapper.vm.createUser()

      expect(Swal.fire).toHaveBeenCalledWith('Error', 'El primer nombre es requerido', 'error')
      expect(authAPI.register).not.toHaveBeenCalled()
    })

    it('should validate email format', async () => {
      wrapper = createWrapper()
      wrapper.vm.addForm.primer_nombre = 'Test'
      wrapper.vm.addForm.primer_apellido = 'User'
      wrapper.vm.addForm.email = 'invalid-email'
      wrapper.vm.addForm.password = 'password123'
      wrapper.vm.addForm.confirm_password = 'password123'

      await wrapper.vm.createUser()

      expect(Swal.fire).toHaveBeenCalledWith('Error', 'El formato del email no es válido', 'error')
    })

    it('should validate password length', async () => {
      wrapper = createWrapper()
      wrapper.vm.addForm.primer_nombre = 'Test'
      wrapper.vm.addForm.primer_apellido = 'User'
      wrapper.vm.addForm.email = 'test@example.com'
      wrapper.vm.addForm.password = '12345'
      wrapper.vm.addForm.confirm_password = '12345'

      await wrapper.vm.createUser()

      expect(Swal.fire).toHaveBeenCalledWith('Error', 'La contraseña debe tener al menos 6 caracteres', 'error')
    })

    it('should validate password confirmation', async () => {
      wrapper = createWrapper()
      wrapper.vm.addForm.primer_nombre = 'Test'
      wrapper.vm.addForm.primer_apellido = 'User'
      wrapper.vm.addForm.email = 'test@example.com'
      wrapper.vm.addForm.password = 'password123'
      wrapper.vm.addForm.confirm_password = 'different'

      await wrapper.vm.createUser()

      expect(Swal.fire).toHaveBeenCalledWith('Error', 'Las contraseñas no coinciden', 'error')
    })

    it('should create user successfully', async () => {
      authAPI.register.mockResolvedValue({
        data: { status: 'success' }
      })

      wrapper = createWrapper()
      wrapper.vm.addForm.primer_nombre = 'Test'
      wrapper.vm.addForm.primer_apellido = 'User'
      wrapper.vm.addForm.email = 'test@example.com'
      wrapper.vm.addForm.password = 'password123'
      wrapper.vm.addForm.confirm_password = 'password123'

      await wrapper.vm.createUser()

      expect(authAPI.register).toHaveBeenCalled()
      expect(Swal.fire).toHaveBeenCalledWith('¡Éxito!', 'Usuario creado exitosamente', 'success')
      expect(wrapper.vm.showAddUserModal).toBe(false)
    })

    it('should handle create error', async () => {
      authAPI.register.mockResolvedValue({
        data: { status: 'error', message: 'Email already exists' }
      })

      wrapper = createWrapper()
      wrapper.vm.addForm.primer_nombre = 'Test'
      wrapper.vm.addForm.primer_apellido = 'User'
      wrapper.vm.addForm.email = 'test@example.com'
      wrapper.vm.addForm.password = 'password123'
      wrapper.vm.addForm.confirm_password = 'password123'

      await wrapper.vm.createUser()

      expect(Swal.fire).toHaveBeenCalledWith('Error', expect.stringContaining('Error al crear usuario'), 'error')
    })
  })

  describe('editUser', () => {
    it('should populate edit form with user data', () => {
      wrapper = createWrapper()
      const usuario = {
        id: 1,
        persona: {
          primer_nombre: 'Test',
          primer_apellido: 'User',
          email: 'test@example.com'
        },
        id_rol: 1
      }

      wrapper.vm.editUser(usuario)

      expect(wrapper.vm.showEditModal).toBe(true)
      expect(wrapper.vm.editingUserId).toBe(1)
      expect(wrapper.vm.editForm.primer_nombre).toBe('Test')
    })
  })

  describe('toggleUserStatus', () => {
    it('should require admin permissions', async () => {
      authService.isAdmin.mockReturnValue(false)
      wrapper = createWrapper()

      const usuario = { id: 1, nombre: 'Test', estado: 'activo' }
      await wrapper.vm.toggleUserStatus(usuario)

      expect(Swal.fire).toHaveBeenCalledWith('Error', 'No tienes permisos para cambiar el estado de usuarios', 'error')
    })

    it('should toggle user status successfully', async () => {
      authService.isAdmin.mockReturnValue(true)
      Swal.fire.mockResolvedValue({ isConfirmed: true })
      mockUsuarios.cambiarEstadoUsuario.mockResolvedValue({ success: true })

      wrapper = createWrapper()
      const usuario = { id: 1, nombre: 'Test', estado: 'activo' }

      await wrapper.vm.toggleUserStatus(usuario)

      expect(mockUsuarios.cambiarEstadoUsuario).toHaveBeenCalledWith(1, 'inactivo')
      expect(Swal.fire).toHaveBeenCalledWith('¡Éxito!', 'Usuario desactivado exitosamente', 'success')
    })
  })
})

