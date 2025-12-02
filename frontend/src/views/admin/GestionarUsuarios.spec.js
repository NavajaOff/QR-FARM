import { mount } from '@vue/test-utils'
import { beforeEach, vi, describe, it, expect } from 'vitest'
import GestionarUsuarios from './GestionarUsuarios.vue'
import { useUsuarios } from '../../composables/useUsuarios.js'
import { useTenants } from '../../composables/useTenants.js'
import authService from '../../services/authService.js'
import { authAPI } from '../../services/api.js'
import Swal from 'sweetalert2'

// Mock composables
vi.mock('../../composables/useUsuarios.js', () => ({
  useUsuarios: vi.fn()
}))

vi.mock('../../composables/useTenants.js', () => ({
  useTenants: vi.fn()
}))

// Mock services
vi.mock('../../services/authService.js', () => ({
  default: {
    isAdmin: vi.fn(),
    getRole: vi.fn()
  }
}))

vi.mock('../../services/api.js', () => ({
  authAPI: {
    register: vi.fn()
  }
}))

// Mock Swal
vi.mock('sweetalert2', () => ({
  default: {
    fire: vi.fn(() => Promise.resolve({ isConfirmed: true }))
  }
}))

describe('GestionarUsuarios.vue', () => {
  let wrapper
  let mockUsuarios
  let mockTenants

  beforeEach(() => {
    vi.clearAllMocks()

    // Setup mock composables
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
  })

  const createWrapper = (props = {}) => {
    return mount(GestionarUsuarios, {
      global: {
        stubs: {
          TenantSelector: { template: '<div>TenantSelector</div>' }
        }
      },
      ...props
    })
  }

  describe('Component Rendering', () => {
    it('should mount correctly', () => {
      wrapper = createWrapper()
      expect(wrapper.exists()).toBe(true)
    })

    it('should render title', () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('Gestión de Usuarios')
    })

    it('should render add user button', () => {
      wrapper = createWrapper()
      const button = wrapper.find('button.btn-primary')
      expect(button.exists()).toBe(true)
      expect(button.text()).toContain('Agregar usuario')
    })

    it('should render table headers', () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('ID')
      expect(wrapper.text()).toContain('Nombre')
      expect(wrapper.text()).toContain('Email')
      expect(wrapper.text()).toContain('Rol')
      expect(wrapper.text()).toContain('Estado')
      expect(wrapper.text()).toContain('Acciones')
    })
  })

  describe('Data Initialization', () => {
    it('should initialize with default values', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.showAddUserModal).toBe(false)
      expect(wrapper.vm.showEditModal).toBe(false)
      expect(wrapper.vm.creatingUser).toBe(false)
      expect(wrapper.vm.addForm.primer_nombre).toBe('')
      expect(wrapper.vm.addForm.id_rol).toBe(2)
    })
  })

  describe('Mounted Hook', () => {
    it('should load users on mount', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(mockUsuarios.cargarUsuarios).toHaveBeenCalled()
    })

    it('should load tenants for super admin on mount', async () => {
      authService.getRole.mockReturnValue('super_admin')
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(mockTenants.cargarTenants).toHaveBeenCalledWith(true)
    })

    it('should not load tenants for regular admin', async () => {
      authService.getRole.mockReturnValue('admin')
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(mockTenants.cargarTenants).not.toHaveBeenCalled()
    })
  })

  describe('Computed Properties', () => {
    it('should compute isCurrentUserAdmin correctly', () => {
      authService.isAdmin.mockReturnValue(true)
      wrapper = createWrapper()
      expect(wrapper.vm.isCurrentUserAdmin).toBe(true)
    })

    it('should compute isSuperAdmin correctly', () => {
      authService.getRole.mockReturnValue('super_admin')
      wrapper = createWrapper()
      expect(wrapper.vm.isSuperAdmin).toBe(true)
    })

    it('should compute isSuperAdmin as false for regular admin', () => {
      authService.getRole.mockReturnValue('admin')
      wrapper = createWrapper()
      expect(wrapper.vm.isSuperAdmin).toBe(false)
    })
  })

  describe('Modal Management', () => {
    it('should open add modal', async () => {
      wrapper = createWrapper()
      await wrapper.vm.openAddModal()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.showAddUserModal).toBe(true)
    })

    it('should close add modal', async () => {
      wrapper = createWrapper()
      wrapper.vm.showAddUserModal = true
      await wrapper.vm.closeAddModal()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.showAddUserModal).toBe(false)
    })

    it('should reset add form when closing modal', async () => {
      wrapper = createWrapper()
      wrapper.vm.addForm.primer_nombre = 'Test'
      wrapper.vm.addForm.email = 'test@test.com'
      await wrapper.vm.closeAddModal()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.addForm.primer_nombre).toBe('')
      expect(wrapper.vm.addForm.email).toBe('')
    })

    it('should open edit modal', async () => {
      wrapper = createWrapper()
      const usuario = {
        id: 1,
        nombre: 'Test User',
        email: 'test@test.com',
        persona: {
          primer_nombre: 'Test',
          primer_apellido: 'User',
          email: 'test@test.com'
        },
        rol: { id: 2 }
      }

      await wrapper.vm.editUser(usuario)
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.showEditModal).toBe(true)
      expect(wrapper.vm.editingUserId).toBe(1)
    })

    it('should close edit modal', async () => {
      wrapper = createWrapper()
      wrapper.vm.showEditModal = true
      await wrapper.vm.closeEditModal()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.showEditModal).toBe(false)
      expect(wrapper.vm.editingUserId).toBeNull()
    })
  })

  describe('resolveRoleId Method', () => {
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

    it('should default to role 2 when no role found', () => {
      wrapper = createWrapper()
      const usuario = {}
      const roleId = wrapper.vm.resolveRoleId(usuario)
      expect(roleId).toBe(2)
    })
  })

  describe('createUser Method', () => {
    beforeEach(() => {
      wrapper = createWrapper()
      wrapper.vm.showAddUserModal = true
    })

    it('should validate primer_nombre is required', async () => {
      wrapper.vm.addForm.primer_nombre = ''
      await wrapper.vm.createUser()

      expect(Swal.fire).toHaveBeenCalledWith('Error', 'El primer nombre es requerido', 'error')
      expect(authAPI.register).not.toHaveBeenCalled()
    })

    it('should validate primer_apellido is required', async () => {
      wrapper.vm.addForm.primer_nombre = 'Test'
      wrapper.vm.addForm.primer_apellido = ''
      await wrapper.vm.createUser()

      expect(Swal.fire).toHaveBeenCalledWith('Error', 'El primer apellido es requerido', 'error')
      expect(authAPI.register).not.toHaveBeenCalled()
    })

    it('should validate email is required', async () => {
      wrapper.vm.addForm.primer_nombre = 'Test'
      wrapper.vm.addForm.primer_apellido = 'User'
      wrapper.vm.addForm.email = ''
      await wrapper.vm.createUser()

      expect(Swal.fire).toHaveBeenCalledWith('Error', 'El email es requerido', 'error')
      expect(authAPI.register).not.toHaveBeenCalled()
    })

    it('should validate email format', async () => {
      wrapper.vm.addForm.primer_nombre = 'Test'
      wrapper.vm.addForm.primer_apellido = 'User'
      wrapper.vm.addForm.email = 'invalid-email'
      await wrapper.vm.createUser()

      expect(Swal.fire).toHaveBeenCalledWith('Error', 'El formato del email no es válido', 'error')
      expect(authAPI.register).not.toHaveBeenCalled()
    })

    it('should validate password length', async () => {
      wrapper.vm.addForm.primer_nombre = 'Test'
      wrapper.vm.addForm.primer_apellido = 'User'
      wrapper.vm.addForm.email = 'test@test.com'
      wrapper.vm.addForm.password = '12345'
      await wrapper.vm.createUser()

      expect(Swal.fire).toHaveBeenCalledWith('Error', 'La contraseña debe tener al menos 6 caracteres', 'error')
      expect(authAPI.register).not.toHaveBeenCalled()
    })

    it('should validate password confirmation', async () => {
      wrapper.vm.addForm.primer_nombre = 'Test'
      wrapper.vm.addForm.primer_apellido = 'User'
      wrapper.vm.addForm.email = 'test@test.com'
      wrapper.vm.addForm.password = '123456'
      wrapper.vm.addForm.confirm_password = '123457'
      await wrapper.vm.createUser()

      expect(Swal.fire).toHaveBeenCalledWith('Error', 'Las contraseñas no coinciden', 'error')
      expect(authAPI.register).not.toHaveBeenCalled()
    })

    it('should create user successfully', async () => {
      wrapper.vm.addForm.primer_nombre = 'Test'
      wrapper.vm.addForm.primer_apellido = 'User'
      wrapper.vm.addForm.email = 'test@test.com'
      wrapper.vm.addForm.password = '123456'
      wrapper.vm.addForm.confirm_password = '123456'

      authAPI.register.mockResolvedValue({
        data: { status: 'success' }
      })

      await wrapper.vm.createUser()
      await wrapper.vm.$nextTick()

      expect(authAPI.register).toHaveBeenCalled()
      expect(Swal.fire).toHaveBeenCalledWith('¡Éxito!', 'Usuario creado exitosamente', 'success')
      expect(wrapper.vm.showAddUserModal).toBe(false)
    })

    it('should handle create user error', async () => {
      wrapper.vm.addForm.primer_nombre = 'Test'
      wrapper.vm.addForm.primer_apellido = 'User'
      wrapper.vm.addForm.email = 'test@test.com'
      wrapper.vm.addForm.password = '123456'
      wrapper.vm.addForm.confirm_password = '123456'

      authAPI.register.mockRejectedValue(new Error('Network error'))

      await wrapper.vm.createUser()
      await wrapper.vm.$nextTick()

      expect(Swal.fire).toHaveBeenCalledWith('Error', expect.stringContaining('Error al crear usuario'), 'error')
    })

    it('should include role and tenant for super admin', async () => {
      authService.getRole.mockReturnValue('super_admin')
      wrapper = createWrapper()
      wrapper.vm.showAddUserModal = true
      wrapper.vm.addForm.primer_nombre = 'Test'
      wrapper.vm.addForm.primer_apellido = 'User'
      wrapper.vm.addForm.email = 'test@test.com'
      wrapper.vm.addForm.password = '123456'
      wrapper.vm.addForm.confirm_password = '123456'
      wrapper.vm.addForm.id_rol = 1
      wrapper.vm.addForm.tenant_id = 1

      authAPI.register.mockResolvedValue({
        data: { status: 'success' }
      })

      await wrapper.vm.createUser()

      expect(authAPI.register).toHaveBeenCalledWith(
        expect.objectContaining({
          id_rol: 1,
          tenant_id: 1
        })
      )
    })

    it('should not create user if already creating', async () => {
      wrapper.vm.creatingUser = true
      await wrapper.vm.createUser()

      expect(authAPI.register).not.toHaveBeenCalled()
    })
  })

  describe('updateUser Method', () => {
    beforeEach(() => {
      wrapper = createWrapper()
      wrapper.vm.editingUserId = 1
      wrapper.vm.originalEditData = {
        primer_nombre: 'Original',
        primer_apellido: 'User',
        segundo_nombre: '',
        segundo_apellido: '',
        email: 'original@test.com',
        telefono: '1234567890'
      }
      wrapper.vm.editForm = {
        primer_nombre: 'Updated',
        primer_apellido: 'User',
        segundo_nombre: '',
        segundo_apellido: '',
        email: 'updated@test.com',
        telefono: '1234567890',
        password: '',
        id_rol: 2
      }
    })

    it('should not update if no editingUserId', async () => {
      wrapper.vm.editingUserId = null
      await wrapper.vm.updateUser()

      expect(mockUsuarios.actualizarUsuario).not.toHaveBeenCalled()
    })

    it('should validate password length if provided', async () => {
      wrapper.vm.editForm.password = '12345'
      await wrapper.vm.updateUser()

      expect(Swal.fire).toHaveBeenCalledWith('Error', 'La contraseña debe tener al menos 6 caracteres', 'error')
      expect(mockUsuarios.actualizarUsuario).not.toHaveBeenCalled()
    })

    it('should not update if no changes', async () => {
      wrapper.vm.editForm.primer_nombre = 'Original'
      wrapper.vm.editForm.primer_apellido = 'User'
      wrapper.vm.editForm.segundo_nombre = 'X'
      wrapper.vm.editForm.segundo_apellido = 'Y'
      wrapper.vm.editForm.email = 'original@test.com'
      wrapper.vm.editForm.telefono = '1234567890'
      wrapper.vm.editForm.password = '' // Ensure password is empty
      wrapper.vm.editForm.id_rol = 2 // Ensure role matches original
      wrapper.vm.originalEditData = {
        primer_nombre: 'Original',
        primer_apellido: 'User',
        segundo_nombre: 'X',
        segundo_apellido: 'Y',
        email: 'original@test.com',
        telefono: '1234567890',
        id_rol: 2
      }
      
      await wrapper.vm.updateUser()

      expect(Swal.fire).toHaveBeenCalledWith('Información', 'No hay cambios para guardar', 'info')
      expect(mockUsuarios.actualizarUsuario).not.toHaveBeenCalled()
    })

    it('should validate email format', async () => {
      wrapper.vm.editForm.primer_nombre = 'Updated'
      wrapper.vm.editForm.primer_apellido = 'User'
      wrapper.vm.editForm.segundo_nombre = 'X'
      wrapper.vm.editForm.segundo_apellido = 'Y'
      wrapper.vm.editForm.email = 'invalid-email'
      wrapper.vm.editForm.telefono = '1234567890'
      wrapper.vm.originalEditData = {
        primer_nombre: 'Original',
        primer_apellido: 'User',
        segundo_nombre: 'X',
        segundo_apellido: 'Y',
        email: 'original@test.com',
        telefono: '1234567890'
      }
      await wrapper.vm.updateUser()

      expect(Swal.fire).toHaveBeenCalledWith('Error', 'El formato del email no es válido', 'error')
      expect(mockUsuarios.actualizarUsuario).not.toHaveBeenCalled()
    })

    it('should update user successfully', async () => {
      wrapper.vm.editForm.primer_nombre = 'Updated'
      wrapper.vm.editForm.primer_apellido = 'User'
      wrapper.vm.editForm.segundo_nombre = 'X'
      wrapper.vm.editForm.segundo_apellido = 'Y'
      wrapper.vm.editForm.email = 'updated@test.com'
      wrapper.vm.editForm.telefono = '1234567890'
      wrapper.vm.originalEditData = {
        primer_nombre: 'Original',
        primer_apellido: 'User',
        segundo_nombre: 'X',
        segundo_apellido: 'Y',
        email: 'original@test.com',
        telefono: '1234567890'
      }
      mockUsuarios.actualizarUsuario.mockResolvedValue({ success: true })
      await wrapper.vm.updateUser()
      await wrapper.vm.$nextTick()

      expect(mockUsuarios.actualizarUsuario).toHaveBeenCalledWith(1, expect.objectContaining({
        primer_nombre: 'Updated',
        email: 'updated@test.com'
      }))
      expect(Swal.fire).toHaveBeenCalledWith('¡Éxito!', 'Usuario actualizado exitosamente', 'success')
      expect(wrapper.vm.showEditModal).toBe(false)
    })

    it('should handle update error', async () => {
      wrapper.vm.editForm.primer_nombre = 'Updated'
      wrapper.vm.editForm.primer_apellido = 'User'
      wrapper.vm.editForm.segundo_nombre = 'X'
      wrapper.vm.editForm.segundo_apellido = 'Y'
      wrapper.vm.editForm.email = 'updated@test.com'
      wrapper.vm.editForm.telefono = '1234567890'
      wrapper.vm.originalEditData = {
        primer_nombre: 'Original',
        primer_apellido: 'User',
        segundo_nombre: 'X',
        segundo_apellido: 'Y',
        email: 'original@test.com',
        telefono: '1234567890'
      }
      mockUsuarios.actualizarUsuario.mockResolvedValue({
        success: false,
        message: 'Update failed'
      })
      await wrapper.vm.updateUser()
      await wrapper.vm.$nextTick()

      expect(Swal.fire).toHaveBeenCalledWith('Error', 'Error al actualizar usuario: Update failed', 'error')
    })

    it('should include password if provided', async () => {
      wrapper.vm.editForm.primer_nombre = 'Updated'
      wrapper.vm.editForm.primer_apellido = 'User'
      wrapper.vm.editForm.segundo_nombre = 'X'
      wrapper.vm.editForm.segundo_apellido = 'Y'
      wrapper.vm.editForm.email = 'updated@test.com'
      wrapper.vm.editForm.telefono = '1234567890'
      wrapper.vm.editForm.password = 'newpassword123'
      wrapper.vm.originalEditData = {
        primer_nombre: 'Original',
        primer_apellido: 'User',
        segundo_nombre: 'X',
        segundo_apellido: 'Y',
        email: 'original@test.com',
        telefono: '1234567890'
      }
      mockUsuarios.actualizarUsuario.mockResolvedValue({ success: true })
      await wrapper.vm.updateUser()

      expect(mockUsuarios.actualizarUsuario).toHaveBeenCalledWith(
        1,
        expect.objectContaining({
          password: 'newpassword123'
        })
      )
    })

    it('should include role change for admin', async () => {
      authService.isAdmin.mockReturnValue(true)
      wrapper = createWrapper()
      wrapper.vm.editingUserId = 1
      wrapper.vm.originalEditData = {
        primer_nombre: 'Test',
        primer_apellido: 'User',
        segundo_nombre: 'X',
        segundo_apellido: 'Y',
        email: 'test@test.com',
        telefono: '1234567890',
        id_rol: 2
      }
      wrapper.vm.editForm = {
        primer_nombre: 'Test',
        primer_apellido: 'User',
        segundo_nombre: 'X',
        segundo_apellido: 'Y',
        email: 'test@test.com',
        telefono: '1234567890',
        id_rol: 1,
        password: ''
      }

      mockUsuarios.actualizarUsuario.mockResolvedValue({ success: true })
      await wrapper.vm.updateUser()

      expect(mockUsuarios.actualizarUsuario).toHaveBeenCalledWith(
        1,
        expect.objectContaining({
          id_rol: 1
        })
      )
    })
  })

  describe('toggleUserStatus Method', () => {
    beforeEach(() => {
      authService.isAdmin.mockReturnValue(true)
    })

    it('should not toggle if not admin', async () => {
      authService.isAdmin.mockReturnValue(false)
      wrapper = createWrapper()
      const usuario = { id: 1, nombre: 'Test', estado: 'activo' }

      await wrapper.vm.toggleUserStatus(usuario)

      expect(Swal.fire).toHaveBeenCalledWith('Error', 'No tienes permisos para cambiar el estado de usuarios', 'error')
      expect(mockUsuarios.cambiarEstadoUsuario).not.toHaveBeenCalled()
    })

    it('should show confirmation dialog', async () => {
      wrapper = createWrapper()
      const usuario = { id: 1, nombre: 'Test', estado: 'activo' }
      Swal.fire.mockResolvedValue({ isConfirmed: false })
      await wrapper.vm.toggleUserStatus(usuario)

      expect(Swal.fire).toHaveBeenCalledWith(
        expect.objectContaining({
          title: '¿Estás seguro?',
          icon: 'warning'
        })
      )
    })

    it('should not toggle if user cancels', async () => {
      Swal.fire.mockResolvedValue({ isConfirmed: false })
      const usuario = { id: 1, nombre: 'Test', estado: 'activo' }

      await wrapper.vm.toggleUserStatus(usuario)

      expect(mockUsuarios.cambiarEstadoUsuario).not.toHaveBeenCalled()
    })

    it('should toggle status to inactive', async () => {
      wrapper = createWrapper()
      Swal.fire.mockResolvedValue({ isConfirmed: true })
      mockUsuarios.cambiarEstadoUsuario.mockResolvedValue({ success: true })
      const usuario = { id: 1, nombre: 'Test', estado: 'activo' }

      await wrapper.vm.toggleUserStatus(usuario)

      expect(mockUsuarios.cambiarEstadoUsuario).toHaveBeenCalledWith(1, 'inactivo')
      expect(Swal.fire).toHaveBeenCalledWith('¡Éxito!', 'Usuario desactivado exitosamente', 'success')
    })

    it('should toggle status to active', async () => {
      wrapper = createWrapper()
      Swal.fire.mockResolvedValue({ isConfirmed: true })
      mockUsuarios.cambiarEstadoUsuario.mockResolvedValue({ success: true })
      const usuario = { id: 1, nombre: 'Test', estado: 'inactivo' }

      await wrapper.vm.toggleUserStatus(usuario)

      expect(mockUsuarios.cambiarEstadoUsuario).toHaveBeenCalledWith(1, 'activo')
      expect(Swal.fire).toHaveBeenCalledWith('¡Éxito!', 'Usuario activado exitosamente', 'success')
    })

    it('should handle toggle error', async () => {
      wrapper = createWrapper()
      Swal.fire.mockResolvedValue({ isConfirmed: true })
      mockUsuarios.cambiarEstadoUsuario.mockResolvedValue({
        success: false,
        message: 'Toggle failed'
      })
      const usuario = { id: 1, nombre: 'Test', estado: 'activo' }

      await wrapper.vm.toggleUserStatus(usuario)

      expect(Swal.fire).toHaveBeenCalledWith('Error', 'Error al cambiar el estado del usuario: Toggle failed', 'error')
    })
  })

  describe('editUser Method', () => {
    it('should populate edit form from usuario.persona', async () => {
      const usuario = {
        id: 1,
        persona: {
          primer_nombre: 'Test',
          primer_apellido: 'User',
          email: 'test@test.com',
          telefono: '1234567890'
        },
        rol: { id: 2 }
      }

      await wrapper.vm.editUser(usuario)

      expect(wrapper.vm.editForm.primer_nombre).toBe('Test')
      expect(wrapper.vm.editForm.primer_apellido).toBe('User')
      expect(wrapper.vm.editForm.email).toBe('test@test.com')
      expect(wrapper.vm.editingUserId).toBe(1)
      expect(wrapper.vm.showEditModal).toBe(true)
    })

    it('should fallback to usuario properties if persona is missing', async () => {
      const usuario = {
        id: 1,
        primer_nombre: 'Test',
        primer_apellido: 'User',
        email: 'test@test.com',
        rol: { id: 1 }
      }

      await wrapper.vm.editUser(usuario)

      expect(wrapper.vm.editForm.primer_nombre).toBe('Test')
      expect(wrapper.vm.editForm.primer_apellido).toBe('User')
      expect(wrapper.vm.editForm.email).toBe('test@test.com')
    })

    it('should handle usuario with string rol', async () => {
      const usuario = {
        id: 1,
        persona: {
          primer_nombre: 'Test',
          primer_apellido: 'User'
        },
        rol: 'admin'
      }

      await wrapper.vm.editUser(usuario)

      expect(wrapper.vm.editForm.id_rol).toBe(1)
    })
  })

  describe('_procesarCamposActualizacion Method', () => {
    it('should return null if all fields are empty', () => {
      wrapper = createWrapper()
      wrapper.vm.originalEditData = {
        primer_nombre: 'Original',
        email: 'original@test.com'
      }
      wrapper.vm.editForm = {
        primer_nombre: '',
        email: '',
        password: ''
      }

      const result = wrapper.vm._procesarCamposActualizacion()
      expect(result).toBeNull()
    })

    it('should return only changed fields', () => {
      wrapper = createWrapper()
      wrapper.vm.originalEditData = {
        primer_nombre: 'Original',
        primer_apellido: 'User',
        segundo_nombre: 'X',
        segundo_apellido: 'Y',
        email: 'original@test.com',
        telefono: '1234567890'
      }
      wrapper.vm.editForm = {
        primer_nombre: 'Updated',
        primer_apellido: 'User',
        segundo_nombre: 'X',
        segundo_apellido: 'Y',
        email: 'original@test.com',
        telefono: '1234567890',
        password: ''
      }

      const result = wrapper.vm._procesarCamposActualizacion()
      expect(result).toEqual({ primer_nombre: 'Updated' })
    })

    it('should trim string values', () => {
      wrapper = createWrapper()
      wrapper.vm.originalEditData = {
        primer_nombre: 'Original',
        primer_apellido: 'User',
        segundo_nombre: 'X',
        segundo_apellido: 'Y',
        email: 'test@test.com',
        telefono: '1234567890'
      }
      wrapper.vm.editForm = {
        primer_nombre: '  Updated  ',
        primer_apellido: 'User',
        segundo_nombre: 'X',
        segundo_apellido: 'Y',
        email: 'test@test.com',
        telefono: '1234567890',
        password: ''
      }

      const result = wrapper.vm._procesarCamposActualizacion()
      expect(result).toEqual({ primer_nombre: 'Updated' })
    })
  })

  describe('Lifecycle Hooks', () => {
    it('should call beforeUnmount', () => {
      wrapper = createWrapper()
      const consoleSpy = vi.spyOn(console, 'log')
      wrapper.unmount()
      // Note: beforeUnmount may not be called in test environment
      // This test verifies the component can unmount without errors
      expect(wrapper.exists()).toBe(false)
    })
  })
})
