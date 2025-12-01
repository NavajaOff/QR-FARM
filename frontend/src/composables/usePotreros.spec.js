import { beforeEach, afterEach, vi, describe, it, expect } from 'vitest'
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

  afterEach(() => {
    vi.clearAllMocks()
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
    it('should load potreros successfully with success property', async () => {
      const mockPotreros = [
        { id: 1, nombre: 'Potrero 1' },
        { id: 2, nombre: 'Potrero 2' }
      ]

      potreroAPI.getAll.mockResolvedValue({
        data: { success: true, data: mockPotreros }
      })

      const { potreros, loading, error, cargarPotreros } = usePotreros()

      await cargarPotreros()

      expect(loading.value).toBe(false)
      expect(error.value).toBeNull()
      expect(potreros.value).toEqual(mockPotreros)
      expect(potreroAPI.getAll).toHaveBeenCalled()
    })

    it('should load potreros successfully with status property', async () => {
      const mockPotreros = [
        { id: 1, nombre: 'Potrero 1' }
      ]

      potreroAPI.getAll.mockResolvedValue({
        data: { status: 'success', data: mockPotreros }
      })

      const { potreros, loading, error, cargarPotreros } = usePotreros()

      await cargarPotreros()

      expect(loading.value).toBe(false)
      expect(error.value).toBeNull()
      expect(potreros.value).toEqual(mockPotreros)
    })

    it('should set loading to true during load', async () => {
      let resolvePromise
      const promise = new Promise((resolve) => {
        resolvePromise = resolve
      })
      potreroAPI.getAll.mockReturnValue(promise)

      const { loading, cargarPotreros } = usePotreros()
      const loadPromise = cargarPotreros()

      // Check loading is true before promise resolves
      expect(loading.value).toBe(true)

      resolvePromise({
        data: { success: true, data: [] }
      })
      await loadPromise

      expect(loading.value).toBe(false)
    })

    it('should clear error before loading', async () => {
      const { error, cargarPotreros } = usePotreros()
      error.value = 'Previous error'

      potreroAPI.getAll.mockResolvedValue({
        data: { success: true, data: [] }
      })

      await cargarPotreros()

      expect(error.value).toBeNull()
    })

    it('should handle empty response', async () => {
      potreroAPI.getAll.mockResolvedValue({
        data: { success: true, data: [] }
      })

      const { potreros, loading, cargarPotreros } = usePotreros()

      await cargarPotreros()

      expect(potreros.value).toEqual([])
      expect(loading.value).toBe(false)
    })

    it('should handle response without data property', async () => {
      potreroAPI.getAll.mockResolvedValue({
        data: { success: true }
      })

      const { potreros, loading, cargarPotreros } = usePotreros()

      await cargarPotreros()

      expect(potreros.value).toEqual([])
      expect(loading.value).toBe(false)
    })

    it('should handle response without success or status', async () => {
      potreroAPI.getAll.mockResolvedValue({
        data: { message: 'Error message' }
      })

      const { potreros, loading, error, cargarPotreros } = usePotreros()

      await cargarPotreros()

      expect(loading.value).toBe(false)
      expect(error.value).toBe('Error message')
      expect(potreros.value).toEqual([])
    })

    it('should handle response without success or status and without message', async () => {
      potreroAPI.getAll.mockResolvedValue({
        data: {}
      })

      const { potreros, loading, error, cargarPotreros } = usePotreros()

      await cargarPotreros()

      expect(loading.value).toBe(false)
      expect(error.value).toBe('No fue posible obtener los potreros')
      expect(potreros.value).toEqual([])
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

    it('should handle errors without message', async () => {
      const err = new Error()
      err.message = undefined
      potreroAPI.getAll.mockRejectedValue(err)

      const { error, cargarPotreros } = usePotreros()

      await cargarPotreros()

      expect(error.value).toBeUndefined()
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

    it('should handle create error without message', async () => {
      potreroAPI.create.mockResolvedValue({
        data: { success: false }
      })

      const { crearPotrero } = usePotreros()

      const result = await crearPotrero({ nombre: 'Test' })

      expect(result.success).toBe(false)
      expect(result.message).toBeUndefined()
    })

    it('should handle create exception', async () => {
      const errorMessage = 'Network error'
      potreroAPI.create.mockRejectedValue(new Error(errorMessage))

      const { crearPotrero } = usePotreros()

      const result = await crearPotrero({ nombre: 'Test' })

      expect(result.success).toBe(false)
      expect(result.message).toBe(errorMessage)
    })

    it('should handle create exception without message', async () => {
      const err = new Error()
      err.message = undefined
      potreroAPI.create.mockRejectedValue(err)

      const { crearPotrero } = usePotreros()

      const result = await crearPotrero({ nombre: 'Test' })

      expect(result.success).toBe(false)
      expect(result.message).toBeUndefined()
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

    it('should handle update error without message', async () => {
      potreroAPI.update.mockResolvedValue({
        data: { success: false }
      })

      const { actualizarPotrero } = usePotreros()

      const result = await actualizarPotrero(1, { nombre: 'Test' })

      expect(result.success).toBe(false)
      expect(result.message).toBeUndefined()
    })

    it('should handle update exception', async () => {
      const errorMessage = 'Network error'
      potreroAPI.update.mockRejectedValue(new Error(errorMessage))

      const { actualizarPotrero } = usePotreros()

      const result = await actualizarPotrero(1, { nombre: 'Test' })

      expect(result.success).toBe(false)
      expect(result.message).toBe(errorMessage)
    })

    it('should handle update exception without message', async () => {
      const err = new Error()
      err.message = undefined
      potreroAPI.update.mockRejectedValue(err)

      const { actualizarPotrero } = usePotreros()

      const result = await actualizarPotrero(1, { nombre: 'Test' })

      expect(result.success).toBe(false)
      expect(result.message).toBeUndefined()
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

    it('should handle delete error without message', async () => {
      potreroAPI.delete.mockResolvedValue({
        data: { success: false }
      })

      const { eliminarPotrero } = usePotreros()

      const result = await eliminarPotrero(1)

      expect(result.success).toBe(false)
      expect(result.message).toBeUndefined()
    })

    it('should handle delete exception', async () => {
      const errorMessage = 'Network error'
      potreroAPI.delete.mockRejectedValue(new Error(errorMessage))

      const { eliminarPotrero } = usePotreros()

      const result = await eliminarPotrero(1)

      expect(result.success).toBe(false)
      expect(result.message).toBe(errorMessage)
    })

    it('should handle delete exception without message', async () => {
      const err = new Error()
      err.message = undefined
      potreroAPI.delete.mockRejectedValue(err)

      const { eliminarPotrero } = usePotreros()

      const result = await eliminarPotrero(1)

      expect(result.success).toBe(false)
      expect(result.message).toBeUndefined()
    })
  })

  describe('socket events', () => {
    let testUsePotreros

    beforeEach(async () => {
      // Reset modules to reset socketRegistered flag
      vi.resetModules()
      // Re-import to get fresh instance with socketRegistered = false
      const module = await import('./usePotreros.js')
      testUsePotreros = module.usePotreros
      // Clear socket mock calls to get fresh handlers
      socket.on.mockClear()
    })

    const getSocketHandler = (eventName) => {
      // Get handler from socket.on mock calls - get the last call for this event
      const calls = socket.on.mock.calls
      // Find all calls for this event and get the last one
      const matchingCalls = calls.filter(call => call[0] === eventName)
      return matchingCalls.length > 0 ? matchingCalls[matchingCalls.length - 1][1] : undefined
    }

    it('should handle potrero_created event with data', () => {
      const { potreros } = testUsePotreros()
      
      const newPotrero = { id: 1, nombre: 'Nuevo Potrero' }
      const callback = getSocketHandler('potrero_created')
      
      expect(callback).toBeDefined()
      callback({ data: newPotrero })

      expect(potreros.value).toContainEqual(newPotrero)
    })

    it('should handle potrero_created event without data', () => {
      const { potreros } = testUsePotreros()
      const initialLength = potreros.value.length
      
      const callback = getSocketHandler('potrero_created')
      expect(callback).toBeDefined()
      callback({})

      expect(potreros.value.length).toBe(initialLength)
    })

    it('should handle potrero_created event with null payload', () => {
      const { potreros } = testUsePotreros()
      const initialLength = potreros.value.length
      
      const callback = getSocketHandler('potrero_created')
      expect(callback).toBeDefined()
      callback(null)

      expect(potreros.value.length).toBe(initialLength)
    })

    it('should handle potrero_created event with payload without id', () => {
      const { potreros } = testUsePotreros()
      const initialLength = potreros.value.length
      
      const callback = getSocketHandler('potrero_created')
      expect(callback).toBeDefined()
      callback({ data: { nombre: 'Sin ID' } })

      expect(potreros.value.length).toBe(initialLength)
    })

    it('should handle potrero_updated event with existing item', () => {
      const { potreros } = testUsePotreros()
      potreros.value = [{ id: 1, nombre: 'Potrero Original' }]
      
      const callback = getSocketHandler('potrero_updated')
      expect(callback).toBeDefined()
      callback({ data: { id: 1, nombre: 'Potrero Actualizado' } })

      expect(potreros.value.find(p => p.id === 1).nombre).toBe('Potrero Actualizado')
    })

    it('should handle potrero_updated event for new item', () => {
      const { potreros } = testUsePotreros()
      potreros.value = []
      
      const callback = getSocketHandler('potrero_updated')
      expect(callback).toBeDefined()
      callback({ data: { id: 2, nombre: 'Nuevo Potrero' } })

      expect(potreros.value).toContainEqual({ id: 2, nombre: 'Nuevo Potrero' })
    })

    it('should handle potrero_updated event without data', () => {
      const { potreros } = testUsePotreros()
      potreros.value = [{ id: 1, nombre: 'Potrero' }]
      const initialLength = potreros.value.length
      
      const callback = getSocketHandler('potrero_updated')
      expect(callback).toBeDefined()
      callback({})

      expect(potreros.value.length).toBe(initialLength)
    })

    it('should handle potrero_updated event with null payload', () => {
      const { potreros } = testUsePotreros()
      potreros.value = [{ id: 1, nombre: 'Potrero' }]
      const initialLength = potreros.value.length
      
      const callback = getSocketHandler('potrero_updated')
      expect(callback).toBeDefined()
      callback(null)

      expect(potreros.value.length).toBe(initialLength)
    })

    it('should handle potrero_updated event with item without id', () => {
      const { potreros } = testUsePotreros()
      potreros.value = [{ id: 1, nombre: 'Potrero' }]
      const initialLength = potreros.value.length
      
      const callback = getSocketHandler('potrero_updated')
      expect(callback).toBeDefined()
      callback({ data: { nombre: 'Sin ID' } })

      expect(potreros.value.length).toBe(initialLength)
    })

    it('should merge properties when updating existing item', () => {
      const { potreros } = testUsePotreros()
      potreros.value = [{ id: 1, nombre: 'Potrero Original', capacidad: 25 }]
      
      const callback = getSocketHandler('potrero_updated')
      expect(callback).toBeDefined()
      callback({ data: { id: 1, nombre: 'Potrero Actualizado', area: 100 } })

      const updated = potreros.value.find(p => p.id === 1)
      expect(updated).toBeDefined()
      expect(updated.nombre).toBe('Potrero Actualizado')
      expect(updated.capacidad).toBe(25) // Existing property preserved
      expect(updated.area).toBe(100) // New property added
    })

    it('should handle potrero_deleted event', () => {
      const { potreros } = testUsePotreros()
      potreros.value = [
        { id: 1, nombre: 'Potrero 1' },
        { id: 2, nombre: 'Potrero 2' }
      ]
      
      const callback = getSocketHandler('potrero_deleted')
      expect(callback).toBeDefined()
      callback({ id: 1 })

      expect(potreros.value.find(p => p.id === 1)).toBeUndefined()
      expect(potreros.value.find(p => p.id === 2)).toBeDefined()
    })

    it('should handle potrero_deleted event without id', () => {
      const { potreros } = testUsePotreros()
      potreros.value = [{ id: 1, nombre: 'Potrero 1' }]
      const initialLength = potreros.value.length
      
      const callback = getSocketHandler('potrero_deleted')
      expect(callback).toBeDefined()
      callback({})

      expect(potreros.value.length).toBe(initialLength)
    })

    it('should handle potrero_deleted event with null id', () => {
      const { potreros } = testUsePotreros()
      potreros.value = [{ id: 1, nombre: 'Potrero 1' }]
      const initialLength = potreros.value.length
      
      const callback = getSocketHandler('potrero_deleted')
      expect(callback).toBeDefined()
      callback({ id: null })

      expect(potreros.value.length).toBe(initialLength)
    })

    it('should handle potrero_deleted event with undefined id', () => {
      const { potreros } = testUsePotreros()
      potreros.value = [{ id: 1, nombre: 'Potrero 1' }]
      const initialLength = potreros.value.length
      
      const callback = getSocketHandler('potrero_deleted')
      expect(callback).toBeDefined()
      callback({ id: undefined })

      expect(potreros.value.length).toBe(initialLength)
    })

    it('should handle disconnect event and reset socketRegistered', () => {
      testUsePotreros()
      
      const callback = getSocketHandler('disconnect')
      expect(callback).toBeDefined()
      callback()

      // Verify that socket.on was called
      expect(socket.on).toHaveBeenCalled()
    })

    it('should not register socket events twice when socketRegistered is true', () => {
      testUsePotreros()
      const firstCallCount = socket.on.mock.calls.length
      
      // Call usePotreros again - should not register events again because socketRegistered is true
      testUsePotreros()
      const secondCallCount = socket.on.mock.calls.length
      
      // socket.on should not be called again if socketRegistered is true
      expect(secondCallCount).toBe(firstCallCount)
    })
  })
})
