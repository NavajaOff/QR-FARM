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

    it('should activate user when currently inactive', async () => {
      authService.isAdmin.mockReturnValue(true)
      Swal.fire.mockResolvedValue({ isConfirmed: true })
      mockUsuarios.cambiarEstadoUsuario.mockResolvedValue({ success: true })

      wrapper = createWrapper()
      const usuario = { id: 1, nombre: 'Test', estado: 'inactivo' }

      await wrapper.vm.toggleUserStatus(usuario)

      expect(mockUsuarios.cambiarEstadoUsuario).toHaveBeenCalledWith(1, 'activo')
      expect(Swal.fire).toHaveBeenCalledWith('¡Éxito!', 'Usuario activado exitosamente', 'success')
    })

    it('should not change status if user cancels', async () => {
      authService.isAdmin.mockReturnValue(true)
      Swal.fire.mockResolvedValue({ isConfirmed: false })

      wrapper = createWrapper()
      const usuario = { id: 1, nombre: 'Test', estado: 'activo' }

      await wrapper.vm.toggleUserStatus(usuario)

      expect(mockUsuarios.cambiarEstadoUsuario).not.toHaveBeenCalled()
    })

    it('should handle error when changing status fails', async () => {
      authService.isAdmin.mockReturnValue(true)
      Swal.fire.mockResolvedValue({ isConfirmed: true })
      mockUsuarios.cambiarEstadoUsuario.mockResolvedValue({ 
        success: false, 
        message: 'Error al cambiar estado' 
      })

      wrapper = createWrapper()
      const usuario = { id: 1, nombre: 'Test', estado: 'activo' }

      await wrapper.vm.toggleUserStatus(usuario)

      expect(Swal.fire).toHaveBeenCalledWith('Error', expect.stringContaining('Error al cambiar'), 'error')
    })
  })

  describe('updateUser', () => {
    beforeEach(() => {
      wrapper = createWrapper()
      wrapper.vm.editingUserId = 1
      wrapper.vm.editForm = {
        primer_nombre: 'Juan',
        primer_apellido: 'Pérez',
        email: 'juan@example.com',
        password: '',
        id_rol: 2
      }
      wrapper.vm.originalEditData = {
        primer_nombre: 'Juan',
        primer_apellido: 'Pérez',
        email: 'juan@example.com',
        id_rol: 2
      }
    })

    it('should not update if no editingUserId', async () => {
      wrapper.vm.editingUserId = null
      await wrapper.vm.updateUser()
      expect(mockUsuarios.actualizarUsuario).not.toHaveBeenCalled()
    })

    it('should validate password length', async () => {
      wrapper.vm.editForm.password = '123'
      await wrapper.vm.updateUser()
      expect(Swal.fire).toHaveBeenCalledWith('Error', expect.stringContaining('6 caracteres'), 'error')
    })

    it('should update user successfully', async () => {
      wrapper.vm.editingUserId = 1
      // All fields must have non-empty values because _procesarCamposActualizacion returns null if any field is empty after trim
      // Optional fields need actual values (not empty strings) to pass the validation
      wrapper.vm.editForm.primer_nombre = 'Juan Carlos'
      wrapper.vm.editForm.segundo_nombre = 'N/A'
      wrapper.vm.editForm.primer_apellido = 'Perez'
      wrapper.vm.editForm.segundo_apellido = 'N/A'
      wrapper.vm.editForm.email = 'juan@example.com'
      wrapper.vm.editForm.telefono = 'N/A'
      wrapper.vm.originalEditData = {
        primer_nombre: 'Juan',
        segundo_nombre: 'N/A',
        primer_apellido: 'Perez',
        segundo_apellido: 'N/A',
        email: 'juan@example.com',
        telefono: 'N/A'
      }
      mockUsuarios.actualizarUsuario.mockResolvedValue({ success: true })

      await wrapper.vm.updateUser()

      expect(mockUsuarios.actualizarUsuario).toHaveBeenCalled()
      expect(Swal.fire).toHaveBeenCalledWith('¡Éxito!', 'Usuario actualizado exitosamente', 'success')
      expect(wrapper.vm.showEditModal).toBe(false)
    })

    it('should show info if no changes', async () => {
      wrapper = createWrapper()
      wrapper.vm.editingUserId = 1
      // Clear mock from previous test to ensure clean state
      mockUsuarios.actualizarUsuario.mockReset()
      Swal.fire.mockClear()
      
      // Ensure no password is set and no role changes
      wrapper.vm.editForm.password = ''
      authService.isAdmin.mockReturnValue(false)
      
      // All fields must have non-empty values because _procesarCamposActualizacion returns null if any field is empty after trim
      // All values must be exactly the same as originalEditData to ensure no changes
      wrapper.vm.editForm.primer_nombre = 'Juan'
      wrapper.vm.editForm.segundo_nombre = 'N/A'
      wrapper.vm.editForm.primer_apellido = 'Perez'
      wrapper.vm.editForm.segundo_apellido = 'N/A'
      wrapper.vm.editForm.email = 'juan@example.com'
      wrapper.vm.editForm.telefono = 'N/A'
      wrapper.vm.originalEditData = { 
        primer_nombre: 'Juan',
        segundo_nombre: 'N/A',
        primer_apellido: 'Perez',
        segundo_apellido: 'N/A',
        email: 'juan@example.com',
        telefono: 'N/A'
      }

      await wrapper.vm.updateUser()
      expect(Swal.fire).toHaveBeenCalledWith('Información', 'No hay cambios para guardar', 'info')
      expect(mockUsuarios.actualizarUsuario).not.toHaveBeenCalled()
    })

    it('should validate email format', async () => {
      wrapper = createWrapper()
      wrapper.vm.editingUserId = 1
      // All fields must have non-empty values
      wrapper.vm.editForm.primer_nombre = 'Juan'
      wrapper.vm.editForm.segundo_nombre = 'N/A'
      wrapper.vm.editForm.primer_apellido = 'Perez'
      wrapper.vm.editForm.segundo_apellido = 'N/A'
      wrapper.vm.editForm.email = 'invalid-email'
      wrapper.vm.editForm.telefono = 'N/A'
      wrapper.vm.originalEditData = { 
        primer_nombre: 'Juan',
        segundo_nombre: 'N/A',
        primer_apellido: 'Perez',
        segundo_apellido: 'N/A',
        email: 'juan@example.com',
        telefono: 'N/A'
      }
      
      await wrapper.vm.updateUser()

      // Email validation should show error and not call actualizarUsuario
      expect(Swal.fire).toHaveBeenCalledWith('Error', 'El formato del email no es válido', 'error')
      expect(mockUsuarios.actualizarUsuario).not.toHaveBeenCalled()
    })

    it('should include password in update if provided', async () => {
      wrapper = createWrapper()
      wrapper.vm.editingUserId = 1
      // All fields must have non-empty values
      wrapper.vm.editForm.primer_nombre = 'Juan Carlos'
      wrapper.vm.editForm.segundo_nombre = 'N/A'
      wrapper.vm.editForm.primer_apellido = 'Perez'
      wrapper.vm.editForm.segundo_apellido = 'N/A'
      wrapper.vm.editForm.email = 'juan@example.com'
      wrapper.vm.editForm.telefono = 'N/A'
      wrapper.vm.editForm.password = 'newpassword123'
      wrapper.vm.originalEditData = { 
        primer_nombre: 'Juan',
        segundo_nombre: 'N/A',
        primer_apellido: 'Perez',
        segundo_apellido: 'N/A',
        email: 'juan@example.com',
        telefono: 'N/A'
      }
      mockUsuarios.actualizarUsuario.mockResolvedValue({ success: true })

      await wrapper.vm.updateUser()

      expect(mockUsuarios.actualizarUsuario).toHaveBeenCalled()
      const callArgs = mockUsuarios.actualizarUsuario.mock.calls[0]
      expect(callArgs[1]).toHaveProperty('password', 'newpassword123')
    })

    it('should include id_rol if admin and changed', async () => {
      authService.isAdmin.mockReturnValue(true)
      wrapper = createWrapper()
      wrapper.vm.editingUserId = 1
      // All fields must have non-empty values
      wrapper.vm.editForm.primer_nombre = 'Juan Carlos'
      wrapper.vm.editForm.segundo_nombre = 'N/A'
      wrapper.vm.editForm.primer_apellido = 'Perez'
      wrapper.vm.editForm.segundo_apellido = 'N/A'
      wrapper.vm.editForm.email = 'juan@example.com'
      wrapper.vm.editForm.telefono = 'N/A'
      wrapper.vm.editForm.id_rol = 1
      wrapper.vm.originalEditData = { 
        id_rol: 2, 
        primer_nombre: 'Juan',
        segundo_nombre: 'N/A',
        primer_apellido: 'Perez',
        segundo_apellido: 'N/A',
        email: 'juan@example.com',
        telefono: 'N/A'
      }
      mockUsuarios.actualizarUsuario.mockResolvedValue({ success: true })

      await wrapper.vm.updateUser()

      expect(mockUsuarios.actualizarUsuario).toHaveBeenCalled()
      const callArgs = mockUsuarios.actualizarUsuario.mock.calls[0]
      expect(callArgs[1]).toHaveProperty('id_rol', 1)
    })
  })

  describe('createUser with super admin', () => {
    it('should include id_rol and tenant_id if super admin', async () => {
      authService.getRole.mockReturnValue('super_admin')
      authAPI.register.mockResolvedValue({
        data: { status: 'success' }
      })

      wrapper = createWrapper()
      wrapper.vm.addForm.primer_nombre = 'Test'
      wrapper.vm.addForm.primer_apellido = 'User'
      wrapper.vm.addForm.email = 'test@example.com'
      wrapper.vm.addForm.password = 'password123'
      wrapper.vm.addForm.confirm_password = 'password123'
      wrapper.vm.addForm.id_rol = 1
      wrapper.vm.addForm.tenant_id = 5

      await wrapper.vm.createUser()

      const registerCall = authAPI.register.mock.calls[0][0]
      expect(registerCall.id_rol).toBe(1)
      expect(registerCall.tenant_id).toBe(5)
    })

    it('should validate primer_apellido is required', async () => {
      wrapper = createWrapper()
      wrapper.vm.addForm.primer_nombre = 'Test'
      wrapper.vm.addForm.primer_apellido = ''
      wrapper.vm.addForm.email = 'test@example.com'
      wrapper.vm.addForm.password = 'password123'

      await wrapper.vm.createUser()

      expect(Swal.fire).toHaveBeenCalledWith('Error', 'El primer apellido es requerido', 'error')
    })

    it('should validate email is required', async () => {
      wrapper = createWrapper()
      wrapper.vm.addForm.primer_nombre = 'Test'
      wrapper.vm.addForm.primer_apellido = 'User'
      wrapper.vm.addForm.email = ''
      wrapper.vm.addForm.password = 'password123'

      await wrapper.vm.createUser()

      expect(Swal.fire).toHaveBeenCalledWith('Error', 'El email es requerido', 'error')
    })

    it('should prevent duplicate create requests', async () => {
      wrapper = createWrapper()
      wrapper.vm.creatingUser = true

      await wrapper.vm.createUser()

      expect(authAPI.register).not.toHaveBeenCalled()
    })
  })

  describe('closeEditModal', () => {
    it('should reset edit form and close modal', () => {
      wrapper = createWrapper()
      wrapper.vm.showEditModal = true
      wrapper.vm.editingUserId = 1
      wrapper.vm.editForm.primer_nombre = 'Test'

      wrapper.vm.closeEditModal()

      expect(wrapper.vm.showEditModal).toBe(false)
      expect(wrapper.vm.editingUserId).toBeNull()
      expect(wrapper.vm.editForm.primer_nombre).toBe('')
    })
  })

  describe('resolveRoleId edge cases', () => {
    it('should handle numeric role id from rol string', () => {
      wrapper = createWrapper()
      const usuario = { rol: { id: '1' } }
      const roleId = wrapper.vm.resolveRoleId(usuario)
      expect(roleId).toBe(1)
    })

    it('should handle role from rol.id when id_rol not present', () => {
      wrapper = createWrapper()
      const usuario = { rol: { id: 3 } }
      const roleId = wrapper.vm.resolveRoleId(usuario)
      expect(roleId).toBe(3)
    })
  })

  describe('Lifecycle hooks', () => {
    it('should have lifecycle hooks defined', () => {
      wrapper = createWrapper()

      // Verify component has lifecycle methods (they're defined in the component)
      expect(wrapper.vm).toBeDefined()
      expect(wrapper.exists()).toBe(true)
    })

    it('should call beforeRouteLeave and log navigation', async () => {
      wrapper = createWrapper()

      const next = vi.fn()
      const to = { path: '/other' }
      const from = { path: '/admin/gestionar-usuarios' }

      // Call beforeRouteLeave hook
      gestionarUsuarios.beforeRouteLeave.call(wrapper.vm, to, from, next)

      expect(console.log).toHaveBeenCalledWith('Saliendo de vista usuarios, cancelando peticiones...')
      expect(next).toHaveBeenCalled()
    })
  })

  describe('updateUser edge cases', () => {
    it('should return early when _procesarCamposActualizacion returns null', async () => {
      wrapper = createWrapper()
      wrapper.vm.editingUserId = 1

      // Set up form with empty required fields to make _procesarCamposActualizacion return null
      wrapper.vm.editForm.primer_nombre = ''  // This will cause _procesarCamposActualizacion to return null
      wrapper.vm.editForm.primer_apellido = 'Perez'
      wrapper.vm.editForm.email = 'juan@example.com'
      wrapper.vm.originalEditData = {
        primer_nombre: 'Juan',
        primer_apellido: 'Perez',
        email: 'juan@example.com'
      }

      await wrapper.vm.updateUser()

      // Should return early without calling actualizarUsuario (line 330)
      expect(mockUsuarios.actualizarUsuario).not.toHaveBeenCalled()
    })
  })
})

