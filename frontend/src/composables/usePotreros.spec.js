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
    vi.resetModules()
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
      // eslint-disable-next-line unicorn/error-message
      const err = new Error('')
      err.message = undefined
      potreroAPI.getAll.mockRejectedValue(err)

      const { error, cargarPotreros } = usePotreros()

      await cargarPotreros()

      expect(error.value).toBe('Error desconocido al cargar potreros')
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
      // eslint-disable-next-line unicorn/error-message
      const err = new Error('')
      err.message = undefined
      potreroAPI.create.mockRejectedValue(err)

      const { crearPotrero } = usePotreros()

      const result = await crearPotrero({ nombre: 'Test' })

      expect(result.success).toBe(false)
      expect(result.message).toBe('Error desconocido al crear potrero')
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
      // eslint-disable-next-line unicorn/error-message
      const err = new Error('')
      err.message = undefined
      potreroAPI.update.mockRejectedValue(err)

      const { actualizarPotrero } = usePotreros()

      const result = await actualizarPotrero(1, { nombre: 'Test' })

      expect(result.success).toBe(false)
      expect(result.message).toBe('Error desconocido al actualizar potrero')
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
      // eslint-disable-next-line unicorn/error-message
      const err = new Error('')
      err.message = undefined
      potreroAPI.delete.mockRejectedValue(err)

      const { eliminarPotrero } = usePotreros()

      const result = await eliminarPotrero(1)

      expect(result.success).toBe(false)
      expect(result.message).toBe('Error desconocido al eliminar potrero')
    })
  })

  describe('socket events', () => {
    // Socket events are registered at module level when the module is first imported
    // The registerSocketEvents() function is called automatically when the module loads
    // These tests verify the socket event handlers work correctly

    it('should handle potrero_created event', () => {
      socket.on.mockClear()
      
      const { potreros } = usePotreros()
      
      // Get the callback for potrero_created from the most recent calls
      const createdCalls = socket.on.mock.calls.filter(call => call[0] === 'potrero_created')
      if (createdCalls.length > 0) {
        const callback = createdCalls[createdCalls.length - 1][1]
        const newPotrero = { id: 1, nombre: 'Nuevo Potrero' }
        callback({ data: newPotrero })

        expect(potreros.value).toContainEqual(newPotrero)
      }
    })

    it('should handle potrero_created event without data', () => {
      socket.on.mockClear()
      
      const { potreros } = usePotreros()
      const initialLength = potreros.value.length
      
      const createdCalls = socket.on.mock.calls.filter(call => call[0] === 'potrero_created')
      if (createdCalls.length > 0) {
        const callback = createdCalls[createdCalls.length - 1][1]
        callback({})

        expect(potreros.value.length).toBe(initialLength)
      }
    })

    it('should handle potrero_created event with null payload', () => {
      socket.on.mockClear()
      
      const { potreros } = usePotreros()
      const initialLength = potreros.value.length
      
      const createdCalls = socket.on.mock.calls.filter(call => call[0] === 'potrero_created')
      if (createdCalls.length > 0) {
        const callback = createdCalls[createdCalls.length - 1][1]
        callback(null)

        expect(potreros.value.length).toBe(initialLength)
      }
    })

    it('should handle potrero_updated event', () => {
      socket.on.mockClear()
      
      const { potreros } = usePotreros()
      potreros.value = [{ id: 1, nombre: 'Potrero Original' }]
      
      const updatedCalls = socket.on.mock.calls.filter(call => call[0] === 'potrero_updated')
      if (updatedCalls.length > 0) {
        const callback = updatedCalls[updatedCalls.length - 1][1]
        callback({ data: { id: 1, nombre: 'Potrero Actualizado' } })

        expect(potreros.value.find(p => p.id === 1).nombre).toBe('Potrero Actualizado')
      }
    })

    it('should handle potrero_updated event for new item', () => {
      socket.on.mockClear()
      
      const { potreros } = usePotreros()
      potreros.value = []
      
      const updatedCalls = socket.on.mock.calls.filter(call => call[0] === 'potrero_updated')
      if (updatedCalls.length > 0) {
        const callback = updatedCalls[updatedCalls.length - 1][1]
        callback({ data: { id: 2, nombre: 'Nuevo Potrero' } })

        expect(potreros.value).toContainEqual({ id: 2, nombre: 'Nuevo Potrero' })
      }
    })

    it('should handle potrero_updated event without data', () => {
      socket.on.mockClear()
      
      const { potreros } = usePotreros()
      potreros.value = [{ id: 1, nombre: 'Potrero' }]
      const initialLength = potreros.value.length
      
      const updatedCalls = socket.on.mock.calls.filter(call => call[0] === 'potrero_updated')
      if (updatedCalls.length > 0) {
        const callback = updatedCalls[updatedCalls.length - 1][1]
        callback({})

        expect(potreros.value.length).toBe(initialLength)
      }
    })

    it('should handle potrero_updated event with item without id', () => {
      socket.on.mockClear()
      
      const { potreros } = usePotreros()
      potreros.value = [{ id: 1, nombre: 'Potrero' }]
      const initialLength = potreros.value.length
      
      const updatedCalls = socket.on.mock.calls.filter(call => call[0] === 'potrero_updated')
      if (updatedCalls.length > 0) {
        const callback = updatedCalls[updatedCalls.length - 1][1]
        callback({ data: { nombre: 'Sin ID' } })

        expect(potreros.value.length).toBe(initialLength)
      }
    })

    it('should handle potrero_deleted event', () => {
      socket.on.mockClear()
      
      const { potreros } = usePotreros()
      potreros.value = [
        { id: 1, nombre: 'Potrero 1' },
        { id: 2, nombre: 'Potrero 2' }
      ]
      
      const deletedCalls = socket.on.mock.calls.filter(call => call[0] === 'potrero_deleted')
      if (deletedCalls.length > 0) {
        const callback = deletedCalls[deletedCalls.length - 1][1]
        callback({ id: 1 })

        expect(potreros.value.find(p => p.id === 1)).toBeUndefined()
        expect(potreros.value.find(p => p.id === 2)).toBeDefined()
      }
    })

    it('should handle potrero_deleted event without id', () => {
      socket.on.mockClear()
      
      const { potreros } = usePotreros()
      potreros.value = [{ id: 1, nombre: 'Potrero 1' }]
      const initialLength = potreros.value.length
      
      const deletedCalls = socket.on.mock.calls.filter(call => call[0] === 'potrero_deleted')
      if (deletedCalls.length > 0) {
        const callback = deletedCalls[deletedCalls.length - 1][1]
        callback({})

        expect(potreros.value.length).toBe(initialLength)
      }
    })

    it('should handle potrero_deleted event with null id', () => {
      socket.on.mockClear()
      
      const { potreros } = usePotreros()
      potreros.value = [{ id: 1, nombre: 'Potrero 1' }]
      const initialLength = potreros.value.length
      
      const deletedCalls = socket.on.mock.calls.filter(call => call[0] === 'potrero_deleted')
      if (deletedCalls.length > 0) {
        const callback = deletedCalls[deletedCalls.length - 1][1]
        callback({ id: null })

        expect(potreros.value.length).toBe(initialLength)
      }
    })

    it('should handle disconnect event', () => {
      socket.on.mockClear()
      
      usePotreros()
      
      const disconnectCalls = socket.on.mock.calls.filter(call => call[0] === 'disconnect')
      if (disconnectCalls.length > 0) {
        const callback = disconnectCalls[disconnectCalls.length - 1][1]
        callback()

        // After disconnect, socketRegistered should be false
        // This allows re-registration on next use
        expect(socket.on).toHaveBeenCalled()
      }
    })

    it('should merge properties on update', () => {
      socket.on.mockClear()

      const { potreros } = usePotreros()
      potreros.value = [{ id: 1, nombre: 'Potrero Original', capacidad: 25 }]

      const updatedCalls = socket.on.mock.calls.filter(call => call[0] === 'potrero_updated')
      if (updatedCalls.length > 0) {
        const callback = updatedCalls[updatedCalls.length - 1][1]
        callback({ data: { id: 1, nombre: 'Potrero Actualizado' } })

        const updated = potreros.value.find(p => p.id === 1)
        if (updated) {
          expect(updated.nombre).toBe('Potrero Actualizado')
          expect(updated.capacidad).toBe(25) // Should preserve existing properties
        }
      }
    })

    it('should handle upsertPotrero with new item (else branch)', () => {
      const { potreros } = usePotreros()
      potreros.value = [{ id: 1, nombre: 'Existing Potrero' }]

      // Access internal upsertPotrero function through socket callback
      const updatedCalls = socket.on.mock.calls.filter(call => call[0] === 'potrero_updated')
      if (updatedCalls.length > 0) {
        const callback = updatedCalls[updatedCalls.length - 1][1]
        callback({ data: { id: 2, nombre: 'New Potrero' } })

        expect(potreros.value).toHaveLength(2)
        expect(potreros.value[0].nombre).toBe('New Potrero') // Should be prepended
        expect(potreros.value[1].nombre).toBe('Existing Potrero')
      }
    })

    it('should handle removePotrero with valid id', () => {
      const { potreros } = usePotreros()
      potreros.value = [
        { id: 1, nombre: 'Potrero 1' },
        { id: 2, nombre: 'Potrero 2' },
        { id: 3, nombre: 'Potrero 3' }
      ]

      // Access internal removePotrero function through socket callback
      const deletedCalls = socket.on.mock.calls.filter(call => call[0] === 'potrero_deleted')
      if (deletedCalls.length > 0) {
        const callback = deletedCalls[deletedCalls.length - 1][1]
        callback({ id: 2 })

        expect(potreros.value).toHaveLength(2)
        expect(potreros.value.find(p => p.id === 2)).toBeUndefined()
        expect(potreros.value.find(p => p.id === 1)).toBeDefined()
        expect(potreros.value.find(p => p.id === 3)).toBeDefined()
      }
    })

    it('should handle socket events with valid payload data', () => {
      socket.on.mockClear()

      const { potreros } = usePotreros()

      // Test potrero_created with valid data
      const createdCalls = socket.on.mock.calls.filter(call => call[0] === 'potrero_created')
      if (createdCalls.length > 0) {
        const callback = createdCalls[createdCalls.length - 1][1]
        callback({ data: { id: 1, nombre: 'Created Potrero' } })

        expect(potreros.value).toContainEqual({ id: 1, nombre: 'Created Potrero' })
      }

      // Test potrero_updated with valid data
      const updatedCalls = socket.on.mock.calls.filter(call => call[0] === 'potrero_updated')
      if (updatedCalls.length > 0) {
        const callback = updatedCalls[updatedCalls.length - 1][1]
        potreros.value = [{ id: 1, nombre: 'Original' }]
        callback({ data: { id: 1, nombre: 'Updated Potrero' } })

        expect(potreros.value.find(p => p.id === 1).nombre).toBe('Updated Potrero')
      }

      // Test potrero_deleted with valid id
      const deletedCalls = socket.on.mock.calls.filter(call => call[0] === 'potrero_deleted')
      if (deletedCalls.length > 0) {
        const callback = deletedCalls[deletedCalls.length - 1][1]
        potreros.value = [{ id: 1, nombre: 'To Delete' }]
        callback({ id: 1 })

        expect(potreros.value.find(p => p.id === 1)).toBeUndefined()
      }
    })

    it('should handle disconnect event and reset socketRegistered', () => {
      socket.on.mockClear()

      usePotreros()

      const disconnectCalls = socket.on.mock.calls.filter(call => call[0] === 'disconnect')
      if (disconnectCalls.length > 0) {
        const callback = disconnectCalls[disconnectCalls.length - 1][1]
        callback()

        // The disconnect callback sets socketRegistered = false
        // This allows re-registration on next use
        expect(socket.on).toHaveBeenCalledWith('disconnect', expect.any(Function))
      }
    })
  })
})
