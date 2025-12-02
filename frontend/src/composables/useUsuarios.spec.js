import { beforeEach, vi } from 'vitest'
import { useUsuarios } from './useUsuarios'
import { userAPI } from '../services/api.js'

// Mock de userAPI
vi.mock('../services/api.js', () => ({
  userAPI: {
    getAll: vi.fn(),
    update: vi.fn(),
    changeStatus: vi.fn()
  }
}))

describe('useUsuarios', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    console.log = vi.fn()
    console.error = vi.fn()
  })

  it('should export useUsuarios composable', () => {
    expect(useUsuarios).toBeDefined()
    expect(typeof useUsuarios).toBe('function')
  })

  it('should return reactive refs and functions', () => {
    const { usuarios, loading, error, cargarUsuarios, actualizarUsuario, cambiarEstadoUsuario } = useUsuarios()

    expect(usuarios).toBeDefined()
    expect(loading).toBeDefined()
    expect(error).toBeDefined()
    expect(typeof cargarUsuarios).toBe('function')
    expect(typeof actualizarUsuario).toBe('function')
    expect(typeof cambiarEstadoUsuario).toBe('function')
  })

  it('should initialize with default values', () => {
    const { usuarios, loading, error } = useUsuarios()

    expect(usuarios.value).toEqual([])
    expect(loading.value).toBe(false)
    expect(error.value).toBeNull()
  })

  describe('cargarUsuarios', () => {
    it('should load usuarios successfully', async () => {
      const mockUsuarios = [
        { id: 1, nombre: 'Usuario 1', rol: { nombre_rol: 'admin' } },
        { id: 2, nombre: 'Usuario 2', rol: { nombre_rol: 'usuario' } }
      ]

      userAPI.getAll.mockResolvedValue({
        data: { status: 'success', data: mockUsuarios }
      })

      const { usuarios, loading, error, cargarUsuarios } = useUsuarios()

      await cargarUsuarios()

      expect(loading.value).toBe(false)
      expect(error.value).toBeNull()
      expect(usuarios.value).toEqual(mockUsuarios)
      expect(userAPI.getAll).toHaveBeenCalled()
    })

    it('should filter out super_admin users', async () => {
      const mockUsuarios = [
        { id: 1, nombre: 'Usuario 1', rol: { nombre_rol: 'admin' } },
        { id: 2, nombre: 'Super Admin', rol: { nombre_rol: 'super_admin' } },
        { id: 3, nombre: 'Usuario 2', rol: { nombre_rol: 'usuario' } }
      ]

      userAPI.getAll.mockResolvedValue({
        data: { status: 'success', data: mockUsuarios }
      })

      const { usuarios, cargarUsuarios } = useUsuarios()

      await cargarUsuarios()

      expect(usuarios.value).toHaveLength(2)
      expect(usuarios.value.find(u => u.rol?.nombre_rol === 'super_admin')).toBeUndefined()
    })

    it('should handle different rol formats', async () => {
      const mockUsuarios = [
        { id: 1, nombre: 'Usuario 1', rol: { rol: 'admin' } },
        { id: 2, nombre: 'Usuario 2', rol: 'usuario' }
      ]

      userAPI.getAll.mockResolvedValue({
        data: { status: 'success', data: mockUsuarios }
      })

      const { usuarios, cargarUsuarios } = useUsuarios()

      await cargarUsuarios()

      expect(usuarios.value).toHaveLength(2)
    })

    it('should handle empty response', async () => {
      userAPI.getAll.mockResolvedValue({
        data: { status: 'success', data: [] }
      })

      const { usuarios, loading, cargarUsuarios } = useUsuarios()

      await cargarUsuarios()

      expect(usuarios.value).toEqual([])
      expect(loading.value).toBe(false)
    })

    it('should handle response without data property', async () => {
      userAPI.getAll.mockResolvedValue({
        data: { status: 'success' }
      })

      const { usuarios, loading, cargarUsuarios } = useUsuarios()

      await cargarUsuarios()

      expect(usuarios.value).toEqual([])
      expect(loading.value).toBe(false)
    })

    it('should handle errors', async () => {
      const errorMessage = 'Network error'
      userAPI.getAll.mockRejectedValue(new Error(errorMessage))

      const { usuarios, loading, error, cargarUsuarios } = useUsuarios()

      await cargarUsuarios()

      expect(loading.value).toBe(false)
      expect(error.value).toBe(errorMessage)
      expect(usuarios.value).toEqual([])
      expect(console.error).toHaveBeenCalled()
    })
  })

  describe('actualizarUsuario', () => {
    it('should update usuario successfully', async () => {
      const mockUsuarios = [{ id: 1, nombre: 'Usuario 1' }]
      userAPI.getAll.mockResolvedValue({
        data: { status: 'success', data: mockUsuarios }
      })
      userAPI.update.mockResolvedValue({
        data: { status: 'success' }
      })

      const { actualizarUsuario, cargarUsuarios } = useUsuarios()
      await cargarUsuarios()

      const result = await actualizarUsuario(1, { nombre: 'Usuario Actualizado' })

      expect(result.success).toBe(true)
      expect(userAPI.update).toHaveBeenCalledWith(1, { nombre: 'Usuario Actualizado' })
      expect(userAPI.getAll).toHaveBeenCalledTimes(2) // Once in cargarUsuarios, once in actualizarUsuario
    })

    it('should handle update error', async () => {
      userAPI.update.mockResolvedValue({
        data: { status: 'error', message: 'Update failed' }
      })

      const { actualizarUsuario } = useUsuarios()

      const result = await actualizarUsuario(1, { nombre: 'Test' })

      expect(result.success).toBe(false)
      expect(result.message).toBe('Update failed')
    })

    it('should handle update exception', async () => {
      const errorMessage = 'Network error'
      userAPI.update.mockRejectedValue(new Error(errorMessage))

      const { actualizarUsuario } = useUsuarios()

      const result = await actualizarUsuario(1, { nombre: 'Test' })

      expect(result.success).toBe(false)
      expect(result.message).toBe(errorMessage)
    })
  })

  describe('cambiarEstadoUsuario', () => {
    it('should change status successfully', async () => {
      const mockUsuarios = [{ id: 1, nombre: 'Usuario 1' }]
      userAPI.getAll.mockResolvedValue({
        data: { status: 'success', data: mockUsuarios }
      })
      userAPI.changeStatus.mockResolvedValue({
        data: { status: 'success' }
      })

      const { cambiarEstadoUsuario, cargarUsuarios } = useUsuarios()
      await cargarUsuarios()

      const result = await cambiarEstadoUsuario(1, 'activo')

      expect(result.success).toBe(true)
      expect(userAPI.changeStatus).toHaveBeenCalledWith(1, 'activo')
      expect(userAPI.getAll).toHaveBeenCalledTimes(2)
    })

    it('should handle status change error', async () => {
      userAPI.changeStatus.mockResolvedValue({
        data: { status: 'error', message: 'Status change failed' }
      })

      const { cambiarEstadoUsuario } = useUsuarios()

      const result = await cambiarEstadoUsuario(1, 'inactivo')

      expect(result.success).toBe(false)
      expect(result.message).toBe('Status change failed')
    })

    it('should handle status change exception with response data', async () => {
      const error = new Error('Network error')
      error.response = { data: { message: 'Server error' } }
      userAPI.changeStatus.mockRejectedValue(error)

      const { cambiarEstadoUsuario } = useUsuarios()

      const result = await cambiarEstadoUsuario(1, 'activo')

      expect(result.success).toBe(false)
      expect(result.message).toBe('Server error')
      expect(console.error).toHaveBeenCalled()
    })

    it('should handle status change exception without response', async () => {
      const error = new Error('Network error')
      userAPI.changeStatus.mockRejectedValue(error)

      const { cambiarEstadoUsuario } = useUsuarios()

      const result = await cambiarEstadoUsuario(1, 'activo')

      expect(result.success).toBe(false)
      expect(result.message).toBe('Network error')
      expect(console.error).toHaveBeenCalled()
    })

    it('should handle status change exception with unknown error', async () => {
      const error = {}
      userAPI.changeStatus.mockRejectedValue(error)

      const { cambiarEstadoUsuario } = useUsuarios()

      const result = await cambiarEstadoUsuario(1, 'activo')

      expect(result.success).toBe(false)
      expect(result.message).toBe('Error al cambiar el estado del usuario')
      expect(console.error).toHaveBeenCalled()
    })
  })

  describe('Edge Cases', () => {
    it('should handle cargarUsuarios with response without status', async () => {
      userAPI.getAll.mockResolvedValue({
        data: { data: [] } // Missing status
      })

      const { cargarUsuarios, usuarios } = useUsuarios()
      await cargarUsuarios()

      expect(usuarios.value).toEqual([])
    })

    it('should handle cargarUsuarios with null data', async () => {
      userAPI.getAll.mockResolvedValue({
        data: { status: 'success', data: null }
      })

      const { cargarUsuarios, usuarios } = useUsuarios()
      await cargarUsuarios()

      expect(usuarios.value).toEqual([])
    })

    it('should filter usuarios with rol.nombre_rol', async () => {
      userAPI.getAll.mockResolvedValue({
        data: {
          status: 'success',
          data: [
            { id: 1, rol: { nombre_rol: 'admin' } },
            { id: 2, rol: { nombre_rol: 'super_admin' } },
            { id: 3, rol: { nombre_rol: 'user' } }
          ]
        }
      })

      const { cargarUsuarios, usuarios } = useUsuarios()
      await cargarUsuarios()

      expect(usuarios.value).toHaveLength(2)
      expect(usuarios.value.find(u => u.id === 2)).toBeUndefined()
    })

    it('should filter usuarios with rol.rol', async () => {
      userAPI.getAll.mockResolvedValue({
        data: {
          status: 'success',
          data: [
            { id: 1, rol: { rol: 'admin' } },
            { id: 2, rol: { rol: 'super_admin' } }
          ]
        }
      })

      const { cargarUsuarios, usuarios } = useUsuarios()
      await cargarUsuarios()

      expect(usuarios.value).toHaveLength(1)
      expect(usuarios.value[0].id).toBe(1)
    })

    it('should filter usuarios with rol as string', async () => {
      userAPI.getAll.mockResolvedValue({
        data: {
          status: 'success',
          data: [
            { id: 1, rol: 'admin' },
            { id: 2, rol: 'super_admin' }
          ]
        }
      })

      const { cargarUsuarios, usuarios } = useUsuarios()
      await cargarUsuarios()

      expect(usuarios.value).toHaveLength(1)
      expect(usuarios.value[0].id).toBe(1)
    })

    it('should handle usuarios with null rol', async () => {
      userAPI.getAll.mockResolvedValue({
        data: {
          status: 'success',
          data: [
            { id: 1, rol: null },
            { id: 2, rol: { nombre_rol: 'admin' } }
          ]
        }
      })

      const { cargarUsuarios, usuarios } = useUsuarios()
      await cargarUsuarios()

      // null rol !== 'super_admin', so both should be included
      expect(usuarios.value.length).toBeGreaterThanOrEqual(1)
    })

    it('should handle cambiarEstadoUsuario with error.response.data.message', async () => {
      userAPI.changeStatus.mockRejectedValue({
        response: {
          data: { message: 'Custom error message' }
        }
      })

      const { cambiarEstadoUsuario } = useUsuarios()
      const result = await cambiarEstadoUsuario(1, 'activo')

      expect(result.success).toBe(false)
      expect(result.message).toBe('Custom error message')
    })

    it('should handle cambiarEstadoUsuario with error.message', async () => {
      userAPI.changeStatus.mockRejectedValue({
        message: 'Network error'
      })

      const { cambiarEstadoUsuario } = useUsuarios()
      const result = await cambiarEstadoUsuario(1, 'activo')

      expect(result.success).toBe(false)
      expect(result.message).toBe('Network error')
    })

    it('should handle cambiarEstadoUsuario with error without message', async () => {
      userAPI.changeStatus.mockRejectedValue({})

      const { cambiarEstadoUsuario } = useUsuarios()
      const result = await cambiarEstadoUsuario(1, 'activo')

      expect(result.success).toBe(false)
      expect(result.message).toBe('Error al cambiar el estado del usuario')
    })

    it('should handle cambiarEstadoUsuario with response without status', async () => {
      userAPI.changeStatus.mockResolvedValue({
        data: {} // No status, no message
      })

      const { cambiarEstadoUsuario } = useUsuarios()
      const result = await cambiarEstadoUsuario(1, 'activo')

      expect(result.success).toBe(false)
      expect(result.message).toBe('Error desconocido')
    })
  })
})
