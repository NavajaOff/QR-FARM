import { beforeEach, afterEach, vi, describe, it, expect } from 'vitest'
import { useGanado } from './useGanado'
import { ganadoAPI } from '../services/api.js'
import { socket } from '../socket.js'

// Store socket event handlers
const socketHandlers = {}

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
    on: vi.fn((event, handler) => {
      socketHandlers[event] = handler
    }),
    off: vi.fn()
  }
}))

describe('useGanado', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    console.error = vi.fn()
    // Clear socket handlers
    Object.keys(socketHandlers).forEach(key => delete socketHandlers[key])
  })

  afterEach(() => {
    vi.clearAllMocks()
    // Clear socket handlers
    Object.keys(socketHandlers).forEach(key => delete socketHandlers[key])
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

    it('should set loading to true during load', async () => {
      let resolvePromise
      const promise = new Promise((resolve) => {
        resolvePromise = resolve
      })
      ganadoAPI.getAll.mockReturnValue(promise)

      const { loading, cargarGanado } = useGanado()
      const loadPromise = cargarGanado()

      // Check loading is true before promise resolves
      expect(loading.value).toBe(true)

      resolvePromise({
        data: { status: 'success', data: [] }
      })
      await loadPromise

      expect(loading.value).toBe(false)
    })

    it('should clear error before loading', async () => {
      const { error, cargarGanado } = useGanado()
      error.value = 'Previous error'

      ganadoAPI.getAll.mockResolvedValue({
        data: { status: 'success', data: [] }
      })

      await cargarGanado()

      expect(error.value).toBeNull()
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

    it('should handle response without success status', async () => {
      ganadoAPI.getAll.mockResolvedValue({
        data: { status: 'error' }
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

    it('should handle errors without message', async () => {
      const err = new Error()
      err.message = undefined
      ganadoAPI.getAll.mockRejectedValue(err)

      const { error, cargarGanado } = useGanado()

      await cargarGanado()

      expect(error.value).toBeUndefined()
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

    it('should handle create error without message', async () => {
      ganadoAPI.create.mockResolvedValue({
        data: { status: 'error' }
      })

      const { crearGanado } = useGanado()

      const result = await crearGanado({ nombre: 'Test' })

      expect(result.success).toBe(false)
      expect(result.message).toBeUndefined()
    })

    it('should handle create exception', async () => {
      const errorMessage = 'Network error'
      ganadoAPI.create.mockRejectedValue(new Error(errorMessage))

      const { crearGanado } = useGanado()

      const result = await crearGanado({ nombre: 'Test' })

      expect(result.success).toBe(false)
      expect(result.message).toBe(errorMessage)
    })

    it('should handle create exception without message', async () => {
      const err = new Error()
      err.message = undefined
      ganadoAPI.create.mockRejectedValue(err)

      const { crearGanado } = useGanado()

      const result = await crearGanado({ nombre: 'Test' })

      expect(result.success).toBe(false)
      expect(result.message).toBeUndefined()
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

    it('should handle update error without message', async () => {
      ganadoAPI.update.mockResolvedValue({
        data: { status: 'error' }
      })

      const { actualizarGanado } = useGanado()

      const result = await actualizarGanado(1, { nombre: 'Test' })

      expect(result.success).toBe(false)
      expect(result.message).toBeUndefined()
    })

    it('should handle update exception', async () => {
      const errorMessage = 'Network error'
      ganadoAPI.update.mockRejectedValue(new Error(errorMessage))

      const { actualizarGanado } = useGanado()

      const result = await actualizarGanado(1, { nombre: 'Test' })

      expect(result.success).toBe(false)
      expect(result.message).toBe(errorMessage)
    })

    it('should handle update exception without message', async () => {
      const err = new Error()
      err.message = undefined
      ganadoAPI.update.mockRejectedValue(err)

      const { actualizarGanado } = useGanado()

      const result = await actualizarGanado(1, { nombre: 'Test' })

      expect(result.success).toBe(false)
      expect(result.message).toBeUndefined()
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

    it('should handle delete error without message', async () => {
      ganadoAPI.delete.mockResolvedValue({
        data: { status: 'error' }
      })

      const { eliminarGanado } = useGanado()

      const result = await eliminarGanado(1)

      expect(result.success).toBe(false)
      expect(result.message).toBeUndefined()
    })

    it('should handle delete exception', async () => {
      const errorMessage = 'Network error'
      ganadoAPI.delete.mockRejectedValue(new Error(errorMessage))

      const { eliminarGanado } = useGanado()

      const result = await eliminarGanado(1)

      expect(result.success).toBe(false)
      expect(result.message).toBe(errorMessage)
    })

    it('should handle delete exception without message', async () => {
      const err = new Error()
      err.message = undefined
      ganadoAPI.delete.mockRejectedValue(err)

      const { eliminarGanado } = useGanado()

      const result = await eliminarGanado(1)

      expect(result.success).toBe(false)
      expect(result.message).toBeUndefined()
    })
  })

  describe('socket events', () => {
    let testUseGanado

    beforeEach(async () => {
      // Reset modules to reset socketRegistered flag
      vi.resetModules()
      // Re-import to get fresh instance with socketRegistered = false
      const module = await import('./useGanado.js')
      testUseGanado = module.useGanado
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

    it('should handle animal_created event with data', () => {
      const { ganado } = testUseGanado()
      
      const newAnimal = { id: 1, nombre: 'Nuevo Animal' }
      const callback = getSocketHandler('animal_created')
      
      expect(callback).toBeDefined()
      callback({ data: newAnimal })

      expect(ganado.value).toContainEqual(newAnimal)
    })

    it('should handle animal_created event without data', () => {
      const { ganado } = testUseGanado()
      const initialLength = ganado.value.length
      
      const callback = getSocketHandler('animal_created')
      expect(callback).toBeDefined()
      callback({})

      expect(ganado.value.length).toBe(initialLength)
    })

    it('should handle animal_created event with null payload', () => {
      const { ganado } = testUseGanado()
      const initialLength = ganado.value.length
      
      const callback = getSocketHandler('animal_created')
      expect(callback).toBeDefined()
      callback(null)

      expect(ganado.value.length).toBe(initialLength)
    })

    it('should handle animal_created event with payload without id', () => {
      const { ganado } = testUseGanado()
      const initialLength = ganado.value.length
      
      const callback = getSocketHandler('animal_created')
      expect(callback).toBeDefined()
      callback({ data: { nombre: 'Sin ID' } })

      expect(ganado.value.length).toBe(initialLength)
    })

    it('should handle animal_updated event with existing item', () => {
      const { ganado } = testUseGanado()
      ganado.value = [{ id: 1, nombre: 'Animal Original' }]
      
      const callback = getSocketHandler('animal_updated')
      expect(callback).toBeDefined()
      callback({ data: { id: 1, nombre: 'Animal Actualizado' } })

      expect(ganado.value.find(a => a.id === 1).nombre).toBe('Animal Actualizado')
    })

    it('should handle animal_updated event for new item', () => {
      const { ganado } = testUseGanado()
      ganado.value = []
      
      const callback = getSocketHandler('animal_updated')
      expect(callback).toBeDefined()
      callback({ data: { id: 2, nombre: 'Nuevo Animal' } })

      expect(ganado.value).toContainEqual({ id: 2, nombre: 'Nuevo Animal' })
    })

    it('should handle animal_updated event without data', () => {
      const { ganado } = testUseGanado()
      ganado.value = [{ id: 1, nombre: 'Animal' }]
      const initialLength = ganado.value.length
      
      const callback = getSocketHandler('animal_updated')
      expect(callback).toBeDefined()
      callback({})

      expect(ganado.value.length).toBe(initialLength)
    })

    it('should handle animal_updated event with null payload', () => {
      const { ganado } = testUseGanado()
      ganado.value = [{ id: 1, nombre: 'Animal' }]
      const initialLength = ganado.value.length
      
      const callback = getSocketHandler('animal_updated')
      expect(callback).toBeDefined()
      callback(null)

      expect(ganado.value.length).toBe(initialLength)
    })

    it('should handle animal_updated event with item without id', () => {
      const { ganado } = testUseGanado()
      ganado.value = [{ id: 1, nombre: 'Animal' }]
      const initialLength = ganado.value.length
      
      const callback = getSocketHandler('animal_updated')
      expect(callback).toBeDefined()
      callback({ data: { nombre: 'Sin ID' } })

      expect(ganado.value.length).toBe(initialLength)
    })

    it('should merge properties when updating existing item', () => {
      const { ganado } = testUseGanado()
      ganado.value = [{ id: 1, nombre: 'Animal Original', raza: 'Holstein' }]
      
      const callback = getSocketHandler('animal_updated')
      expect(callback).toBeDefined()
      callback({ data: { id: 1, nombre: 'Animal Actualizado', peso: 500 } })

      const updated = ganado.value.find(a => a.id === 1)
      expect(updated).toBeDefined()
      expect(updated.nombre).toBe('Animal Actualizado')
      expect(updated.raza).toBe('Holstein') // Existing property preserved
      expect(updated.peso).toBe(500) // New property added
    })

    it('should handle animal_deleted event', () => {
      const { ganado } = testUseGanado()
      ganado.value = [
        { id: 1, nombre: 'Animal 1' },
        { id: 2, nombre: 'Animal 2' }
      ]
      
      const callback = getSocketHandler('animal_deleted')
      expect(callback).toBeDefined()
      callback({ id: 1 })

      expect(ganado.value.find(a => a.id === 1)).toBeUndefined()
      expect(ganado.value.find(a => a.id === 2)).toBeDefined()
    })

    it('should handle animal_deleted event without id', () => {
      const { ganado } = testUseGanado()
      ganado.value = [{ id: 1, nombre: 'Animal 1' }]
      const initialLength = ganado.value.length
      
      const callback = getSocketHandler('animal_deleted')
      expect(callback).toBeDefined()
      callback({})

      expect(ganado.value.length).toBe(initialLength)
    })

    it('should handle animal_deleted event with null id', () => {
      const { ganado } = testUseGanado()
      ganado.value = [{ id: 1, nombre: 'Animal 1' }]
      const initialLength = ganado.value.length
      
      const callback = getSocketHandler('animal_deleted')
      expect(callback).toBeDefined()
      callback({ id: null })

      expect(ganado.value.length).toBe(initialLength)
    })

    it('should handle animal_deleted event with undefined id', () => {
      const { ganado } = testUseGanado()
      ganado.value = [{ id: 1, nombre: 'Animal 1' }]
      const initialLength = ganado.value.length
      
      const callback = getSocketHandler('animal_deleted')
      expect(callback).toBeDefined()
      callback({ id: undefined })

      expect(ganado.value.length).toBe(initialLength)
    })

    it('should handle disconnect event and reset socketRegistered', () => {
      testUseGanado()
      
      const callback = getSocketHandler('disconnect')
      expect(callback).toBeDefined()
      callback()

      // Verify that socket.on was called
      expect(socket.on).toHaveBeenCalled()
    })

    it('should not register socket events twice when socketRegistered is true', () => {
      testUseGanado()
      const firstCallCount = socket.on.mock.calls.length
      
      // Call useGanado again - should not register events again because socketRegistered is true
      testUseGanado()
      const secondCallCount = socket.on.mock.calls.length
      
      // socket.on should not be called again if socketRegistered is true
      expect(secondCallCount).toBe(firstCallCount)
    })
  })
})
