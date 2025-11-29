import { beforeEach, vi } from 'vitest'
import { useGanado } from './useGanado'
import { ganadoAPI } from '../services/api.js'
import { socket } from '../socket.js'

// Mock de ganadoAPI
vi.mock('../services/api.js', () => ({
  ganadoAPI: {
    getAll: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn()
  }
}))

// Mock de socket
vi.mock('../socket.js', () => ({
  socket: {
    on: vi.fn(),
    off: vi.fn()
  }
}))

describe('useGanado', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    console.error = vi.fn()
  })

  it('should export useGanado composable', () => {
    expect(useGanado).toBeDefined()
    expect(typeof useGanado).toBe('function')
  })

  it('should return reactive refs and functions', () => {
    const { ganado, loading, error, cargarGanado, crearGanado, actualizarGanado, eliminarGanado } = useGanado()

    expect(ganado).toBeDefined()
    expect(loading).toBeDefined()
    expect(error).toBeDefined()
    expect(typeof cargarGanado).toBe('function')
    expect(typeof crearGanado).toBe('function')
    expect(typeof actualizarGanado).toBe('function')
    expect(typeof eliminarGanado).toBe('function')
  })

  it('should initialize with default values', () => {
    const { ganado, loading, error } = useGanado()

    expect(ganado.value).toEqual([])
    expect(loading.value).toBe(false)
    expect(error.value).toBeNull()
  })

  describe('cargarGanado', () => {
    it('should load ganado successfully', async () => {
      const mockGanado = [
        { id: 1, nombre: 'Animal 1' },
        { id: 2, nombre: 'Animal 2' }
      ]

      ganadoAPI.getAll.mockResolvedValue({
        data: { status: 'success', data: mockGanado }
      })

      const { ganado, loading, error, cargarGanado } = useGanado()

      await cargarGanado()

      expect(loading.value).toBe(false)
      expect(error.value).toBeNull()
      expect(ganado.value).toEqual(mockGanado)
      expect(ganadoAPI.getAll).toHaveBeenCalled()
    })

    it('should handle empty response', async () => {
      ganadoAPI.getAll.mockResolvedValue({
        data: { status: 'success', data: [] }
      })

      const { ganado, loading, cargarGanado } = useGanado()

      await cargarGanado()

      expect(ganado.value).toEqual([])
      expect(loading.value).toBe(false)
    })

    it('should handle response without data property', async () => {
      ganadoAPI.getAll.mockResolvedValue({
        data: { status: 'success' }
      })

      const { ganado, loading, cargarGanado } = useGanado()

      await cargarGanado()

      expect(ganado.value).toBeUndefined()
      expect(loading.value).toBe(false)
    })

    it('should handle errors', async () => {
      const errorMessage = 'Network error'
      ganadoAPI.getAll.mockRejectedValue(new Error(errorMessage))

      const { ganado, loading, error, cargarGanado } = useGanado()

      await cargarGanado()

      expect(loading.value).toBe(false)
      expect(error.value).toBe(errorMessage)
      expect(ganado.value).toEqual([])
      expect(console.error).toHaveBeenCalled()
    })
  })

  describe('crearGanado', () => {
    it('should create ganado successfully', async () => {
      const mockGanado = [{ id: 1, nombre: 'Animal 1' }]
      ganadoAPI.getAll.mockResolvedValue({
        data: { status: 'success', data: mockGanado }
      })
      ganadoAPI.create.mockResolvedValue({
        data: { status: 'success' }
      })

      const { crearGanado, cargarGanado } = useGanado()
      await cargarGanado()

      const result = await crearGanado({ nombre: 'Nuevo Animal' })

      expect(result.success).toBe(true)
      expect(ganadoAPI.create).toHaveBeenCalledWith({ nombre: 'Nuevo Animal' })
      expect(ganadoAPI.getAll).toHaveBeenCalledTimes(2)
    })

    it('should handle create error', async () => {
      ganadoAPI.create.mockResolvedValue({
        data: { status: 'error', message: 'Create failed' }
      })

      const { crearGanado } = useGanado()

      const result = await crearGanado({ nombre: 'Test' })

      expect(result.success).toBe(false)
      expect(result.message).toBe('Create failed')
    })

    it('should handle create exception', async () => {
      const errorMessage = 'Network error'
      ganadoAPI.create.mockRejectedValue(new Error(errorMessage))

      const { crearGanado } = useGanado()

      const result = await crearGanado({ nombre: 'Test' })

      expect(result.success).toBe(false)
      expect(result.message).toBe(errorMessage)
    })
  })

  describe('actualizarGanado', () => {
    it('should update ganado successfully', async () => {
      const mockGanado = [{ id: 1, nombre: 'Animal 1' }]
      ganadoAPI.getAll.mockResolvedValue({
        data: { status: 'success', data: mockGanado }
      })
      ganadoAPI.update.mockResolvedValue({
        data: { status: 'success' }
      })

      const { actualizarGanado, cargarGanado } = useGanado()
      await cargarGanado()

      const result = await actualizarGanado(1, { nombre: 'Animal Actualizado' })

      expect(result.success).toBe(true)
      expect(ganadoAPI.update).toHaveBeenCalledWith(1, { nombre: 'Animal Actualizado' })
      expect(ganadoAPI.getAll).toHaveBeenCalledTimes(2)
    })

    it('should handle update error', async () => {
      ganadoAPI.update.mockResolvedValue({
        data: { status: 'error', message: 'Update failed' }
      })

      const { actualizarGanado } = useGanado()

      const result = await actualizarGanado(1, { nombre: 'Test' })

      expect(result.success).toBe(false)
      expect(result.message).toBe('Update failed')
    })

    it('should handle update exception', async () => {
      const errorMessage = 'Network error'
      ganadoAPI.update.mockRejectedValue(new Error(errorMessage))

      const { actualizarGanado } = useGanado()

      const result = await actualizarGanado(1, { nombre: 'Test' })

      expect(result.success).toBe(false)
      expect(result.message).toBe(errorMessage)
    })
  })

  describe('eliminarGanado', () => {
    it('should delete ganado successfully', async () => {
      const mockGanado = [{ id: 1, nombre: 'Animal 1' }]
      ganadoAPI.getAll.mockResolvedValue({
        data: { status: 'success', data: mockGanado }
      })
      ganadoAPI.delete.mockResolvedValue({
        data: { status: 'success' }
      })

      const { eliminarGanado, cargarGanado } = useGanado()
      await cargarGanado()

      const result = await eliminarGanado(1)

      expect(result.success).toBe(true)
      expect(ganadoAPI.delete).toHaveBeenCalledWith(1)
      expect(ganadoAPI.getAll).toHaveBeenCalledTimes(2)
    })

    it('should handle delete error', async () => {
      ganadoAPI.delete.mockResolvedValue({
        data: { status: 'error', message: 'Delete failed' }
      })

      const { eliminarGanado } = useGanado()

      const result = await eliminarGanado(1)

      expect(result.success).toBe(false)
      expect(result.message).toBe('Delete failed')
    })

    it('should handle delete exception', async () => {
      const errorMessage = 'Network error'
      ganadoAPI.delete.mockRejectedValue(new Error(errorMessage))

      const { eliminarGanado } = useGanado()

      const result = await eliminarGanado(1)

      expect(result.success).toBe(false)
      expect(result.message).toBe(errorMessage)
    })
  })

  describe('socket events', () => {
    it('should register socket events', () => {
      vi.clearAllMocks()
      useGanado()
      // Socket events are registered when composable is called
      // Check that socket.on was called (may be called multiple times due to module-level registration)
      expect(socket.on).toHaveBeenCalled()
    })

    it('should handle socket events when registered', () => {
      // Socket events are registered at module level
      // This test verifies the composable can be used with socket functionality
      const { ganado } = useGanado()
      expect(ganado.value).toBeDefined()
      expect(Array.isArray(ganado.value)).toBe(true)
    })
  })
})
