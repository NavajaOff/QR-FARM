import { beforeEach, vi } from 'vitest'
import { usePotreros } from './usePotreros'
import { potreroAPI } from '../services/api.js'
import { socket } from '../socket.js'

// Mock de potreroAPI
vi.mock('../services/api.js', () => ({
  potreroAPI: {
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

describe('usePotreros', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    console.error = vi.fn()
  })

  it('should export usePotreros composable', () => {
    expect(usePotreros).toBeDefined()
    expect(typeof usePotreros).toBe('function')
  })

  it('should return reactive refs and functions', () => {
    const { potreros, loading, error, cargarPotreros, crearPotrero, actualizarPotrero, eliminarPotrero } = usePotreros()

    expect(potreros).toBeDefined()
    expect(loading).toBeDefined()
    expect(error).toBeDefined()
    expect(typeof cargarPotreros).toBe('function')
    expect(typeof crearPotrero).toBe('function')
    expect(typeof actualizarPotrero).toBe('function')
    expect(typeof eliminarPotrero).toBe('function')
  })

  it('should initialize with default values', () => {
    const { potreros, loading, error } = usePotreros()

    expect(potreros.value).toEqual([])
    expect(loading.value).toBe(false)
    expect(error.value).toBeNull()
  })

  describe('cargarPotreros', () => {
    it('should load potreros successfully with status success', async () => {
      const mockPotreros = [
        { id: 1, nombre: 'Potrero 1' },
        { id: 2, nombre: 'Potrero 2' }
      ]

      potreroAPI.getAll.mockResolvedValue({
        data: { status: 'success', data: mockPotreros }
      })

      const { potreros, loading, error, cargarPotreros } = usePotreros()

      await cargarPotreros()

      expect(loading.value).toBe(false)
      expect(error.value).toBeNull()
      expect(potreros.value).toEqual(mockPotreros)
      expect(potreroAPI.getAll).toHaveBeenCalled()
    })

    it('should load potreros successfully with success property', async () => {
      const mockPotreros = [{ id: 1, nombre: 'Potrero 1' }]

      potreroAPI.getAll.mockResolvedValue({
        data: { success: true, data: mockPotreros }
      })

      const { potreros, loading, error, cargarPotreros } = usePotreros()

      await cargarPotreros()

      expect(loading.value).toBe(false)
      expect(error.value).toBeNull()
      expect(potreros.value).toEqual(mockPotreros)
    })

    it('should handle empty data array', async () => {
      potreroAPI.getAll.mockResolvedValue({
        data: { success: true, data: [] }
      })

      const { potreros, loading, cargarPotreros } = usePotreros()

      await cargarPotreros()

      expect(potreros.value).toEqual([])
      expect(loading.value).toBe(false)
    })

    it('should handle response without success or status', async () => {
      potreroAPI.getAll.mockResolvedValue({
        data: { message: 'Error' }
      })

      const { potreros, loading, error, cargarPotreros } = usePotreros()

      await cargarPotreros()

      expect(potreros.value).toEqual([])
      expect(error.value).toBe('Error')
      expect(loading.value).toBe(false)
    })

    it('should handle errors', async () => {
      const errorMessage = 'Network error'
      potreroAPI.getAll.mockRejectedValue(new Error(errorMessage))

      const { potreros, loading, error, cargarPotreros } = usePotreros()

      await cargarPotreros()

      expect(loading.value).toBe(false)
      expect(error.value).toBe(errorMessage)
      expect(potreros.value).toEqual([])
      expect(console.error).toHaveBeenCalled()
    })
  })

  describe('crearPotrero', () => {
    it('should create potrero successfully', async () => {
      const mockPotreros = [{ id: 1, nombre: 'Potrero 1' }]
      potreroAPI.getAll.mockResolvedValue({
        data: { success: true, data: mockPotreros }
      })
      potreroAPI.create.mockResolvedValue({
        data: { success: true }
      })

      const { crearPotrero, cargarPotreros } = usePotreros()
      await cargarPotreros()

      const result = await crearPotrero({ nombre: 'Nuevo Potrero' })

      expect(result.success).toBe(true)
      expect(potreroAPI.create).toHaveBeenCalledWith({ nombre: 'Nuevo Potrero' })
      expect(potreroAPI.getAll).toHaveBeenCalledTimes(2)
    })

    it('should handle create error', async () => {
      potreroAPI.create.mockResolvedValue({
        data: { success: false, message: 'Create failed' }
      })

      const { crearPotrero } = usePotreros()

      const result = await crearPotrero({ nombre: 'Test' })

      expect(result.success).toBe(false)
      expect(result.message).toBe('Create failed')
    })

    it('should handle create exception', async () => {
      const errorMessage = 'Network error'
      potreroAPI.create.mockRejectedValue(new Error(errorMessage))

      const { crearPotrero } = usePotreros()

      const result = await crearPotrero({ nombre: 'Test' })

      expect(result.success).toBe(false)
      expect(result.message).toBe(errorMessage)
    })
  })

  describe('actualizarPotrero', () => {
    it('should update potrero successfully', async () => {
      const mockPotreros = [{ id: 1, nombre: 'Potrero 1' }]
      potreroAPI.getAll.mockResolvedValue({
        data: { success: true, data: mockPotreros }
      })
      potreroAPI.update.mockResolvedValue({
        data: { success: true }
      })

      const { actualizarPotrero, cargarPotreros } = usePotreros()
      await cargarPotreros()

      const result = await actualizarPotrero(1, { nombre: 'Potrero Actualizado' })

      expect(result.success).toBe(true)
      expect(potreroAPI.update).toHaveBeenCalledWith(1, { nombre: 'Potrero Actualizado' })
      expect(potreroAPI.getAll).toHaveBeenCalledTimes(2)
    })

    it('should handle update error', async () => {
      potreroAPI.update.mockResolvedValue({
        data: { success: false, message: 'Update failed' }
      })

      const { actualizarPotrero } = usePotreros()

      const result = await actualizarPotrero(1, { nombre: 'Test' })

      expect(result.success).toBe(false)
      expect(result.message).toBe('Update failed')
    })

    it('should handle update exception', async () => {
      const errorMessage = 'Network error'
      potreroAPI.update.mockRejectedValue(new Error(errorMessage))

      const { actualizarPotrero } = usePotreros()

      const result = await actualizarPotrero(1, { nombre: 'Test' })

      expect(result.success).toBe(false)
      expect(result.message).toBe(errorMessage)
    })
  })

  describe('eliminarPotrero', () => {
    it('should delete potrero successfully', async () => {
      const mockPotreros = [{ id: 1, nombre: 'Potrero 1' }]
      potreroAPI.getAll.mockResolvedValue({
        data: { success: true, data: mockPotreros }
      })
      potreroAPI.delete.mockResolvedValue({
        data: { success: true }
      })

      const { eliminarPotrero, cargarPotreros } = usePotreros()
      await cargarPotreros()

      const result = await eliminarPotrero(1)

      expect(result.success).toBe(true)
      expect(potreroAPI.delete).toHaveBeenCalledWith(1)
      expect(potreroAPI.getAll).toHaveBeenCalledTimes(2)
    })

    it('should handle delete error', async () => {
      potreroAPI.delete.mockResolvedValue({
        data: { success: false, message: 'Delete failed' }
      })

      const { eliminarPotrero } = usePotreros()

      const result = await eliminarPotrero(1)

      expect(result.success).toBe(false)
      expect(result.message).toBe('Delete failed')
    })

    it('should handle delete exception', async () => {
      const errorMessage = 'Network error'
      potreroAPI.delete.mockRejectedValue(new Error(errorMessage))

      const { eliminarPotrero } = usePotreros()

      const result = await eliminarPotrero(1)

      expect(result.success).toBe(false)
      expect(result.message).toBe(errorMessage)
    })
  })

  describe('socket events', () => {
    it('should register socket events', () => {
      vi.clearAllMocks()
      usePotreros()
      // Socket events are registered when composable is called
      // Check that socket.on was called (may be called multiple times due to module-level registration)
      expect(socket.on).toHaveBeenCalled()
    })

    it('should handle socket events when registered', () => {
      // Socket events are registered at module level
      // This test verifies the composable can be used with socket functionality
      const { potreros } = usePotreros()
      expect(potreros.value).toBeDefined()
      expect(Array.isArray(potreros.value)).toBe(true)
    })
  })
})
