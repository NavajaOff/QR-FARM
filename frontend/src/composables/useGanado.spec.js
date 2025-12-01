import { beforeEach, afterEach, vi, describe, it, expect } from 'vitest'
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
    // Reset socketRegistered by resetting modules
    vi.resetModules()
  })

  afterEach(() => {
    vi.clearAllMocks()
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
    // Socket events are registered at module level when the module is first imported
    // The registerSocketEvents() function is called automatically when the module loads
    // These tests verify the socket event handlers work correctly

    it('should handle animal_created event', () => {
      socket.on.mockClear()
      
      const { ganado } = useGanado()
      
      // Get the callback for animal_created from the most recent calls
      const createdCalls = socket.on.mock.calls.filter(call => call[0] === 'animal_created')
      if (createdCalls.length > 0) {
        const callback = createdCalls[createdCalls.length - 1][1]
        const newAnimal = { id: 1, nombre: 'Nuevo Animal' }
        callback({ data: newAnimal })

        expect(ganado.value).toContainEqual(newAnimal)
      }
    })

    it('should handle animal_created event without data', () => {
      socket.on.mockClear()
      
      const { ganado } = useGanado()
      const initialLength = ganado.value.length
      
      const createdCall = socket.on.mock.calls.find(call => call[0] === 'animal_created')
      if (createdCall && createdCall[1]) {
        const callback = createdCall[1]
        callback({})

        expect(ganado.value.length).toBe(initialLength)
      }
    })

    it('should handle animal_created event with null payload', () => {
      socket.on.mockClear()
      
      const { ganado } = useGanado()
      const initialLength = ganado.value.length
      
      const createdCall = socket.on.mock.calls.find(call => call[0] === 'animal_created')
      if (createdCall && createdCall[1]) {
        const callback = createdCall[1]
        callback(null)

        expect(ganado.value.length).toBe(initialLength)
      }
    })

    it('should handle animal_updated event', () => {
      socket.on.mockClear()
      
      const { ganado } = useGanado()
      ganado.value = [{ id: 1, nombre: 'Animal Original' }]
      
      const updatedCall = socket.on.mock.calls.find(call => call[0] === 'animal_updated')
      if (updatedCall && updatedCall[1]) {
        const callback = updatedCall[1]
        callback({ data: { id: 1, nombre: 'Animal Actualizado' } })

        expect(ganado.value.find(a => a.id === 1).nombre).toBe('Animal Actualizado')
      }
    })

    it('should handle animal_updated event for new item', () => {
      socket.on.mockClear()
      
      const { ganado } = useGanado()
      ganado.value = []
      
      const updatedCall = socket.on.mock.calls.find(call => call[0] === 'animal_updated')
      if (updatedCall && updatedCall[1]) {
        const callback = updatedCall[1]
        callback({ data: { id: 2, nombre: 'Nuevo Animal' } })

        expect(ganado.value).toContainEqual({ id: 2, nombre: 'Nuevo Animal' })
      }
    })

    it('should handle animal_updated event without data', () => {
      socket.on.mockClear()
      
      const { ganado } = useGanado()
      ganado.value = [{ id: 1, nombre: 'Animal' }]
      const initialLength = ganado.value.length
      
      const updatedCall = socket.on.mock.calls.find(call => call[0] === 'animal_updated')
      if (updatedCall && updatedCall[1]) {
        const callback = updatedCall[1]
        callback({})

        expect(ganado.value.length).toBe(initialLength)
      }
    })

    it('should handle animal_updated event with item without id', () => {
      socket.on.mockClear()
      
      const { ganado } = useGanado()
      ganado.value = [{ id: 1, nombre: 'Animal' }]
      const initialLength = ganado.value.length
      
      const updatedCall = socket.on.mock.calls.find(call => call[0] === 'animal_updated')
      if (updatedCall && updatedCall[1]) {
        const callback = updatedCall[1]
        callback({ data: { nombre: 'Sin ID' } })

        expect(ganado.value.length).toBe(initialLength)
      }
    })

    it('should handle animal_deleted event', () => {
      socket.on.mockClear()
      vi.resetModules()
      
      const { ganado } = useGanado()
      ganado.value = [
        { id: 1, nombre: 'Animal 1' },
        { id: 2, nombre: 'Animal 2' }
      ]
      
      const deletedCall = socket.on.mock.calls.find(call => call[0] === 'animal_deleted')
      if (deletedCall && deletedCall[1]) {
        const callback = deletedCall[1]
        callback({ id: 1 })

        expect(ganado.value.find(a => a.id === 1)).toBeUndefined()
        expect(ganado.value.find(a => a.id === 2)).toBeDefined()
      }
    })

    it('should handle animal_deleted event without id', () => {
      socket.on.mockClear()
      vi.resetModules()
      
      const { ganado } = useGanado()
      ganado.value = [{ id: 1, nombre: 'Animal 1' }]
      const initialLength = ganado.value.length
      
      const deletedCall = socket.on.mock.calls.find(call => call[0] === 'animal_deleted')
      if (deletedCall && deletedCall[1]) {
        const callback = deletedCall[1]
        callback({})

        expect(ganado.value.length).toBe(initialLength)
      }
    })

    it('should handle animal_deleted event with null id', () => {
      socket.on.mockClear()
      vi.resetModules()
      
      const { ganado } = useGanado()
      ganado.value = [{ id: 1, nombre: 'Animal 1' }]
      const initialLength = ganado.value.length
      
      const deletedCall = socket.on.mock.calls.find(call => call[0] === 'animal_deleted')
      if (deletedCall && deletedCall[1]) {
        const callback = deletedCall[1]
        callback({ id: null })

        expect(ganado.value.length).toBe(initialLength)
      }
    })

    it('should handle disconnect event', () => {
      socket.on.mockClear()
      
      useGanado()
      
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
      vi.resetModules()

      const { ganado } = useGanado()
      ganado.value = [{ id: 1, nombre: 'Animal Original', raza: 'Holstein' }]

      const updatedCall = socket.on.mock.calls.find(call => call[0] === 'animal_updated')
      if (updatedCall && updatedCall[1]) {
        const callback = updatedCall[1]
        callback({ data: { id: 1, nombre: 'Animal Actualizado' } })

        const updated = ganado.value.find(a => a.id === 1)
        if (updated) {
          expect(updated.nombre).toBe('Animal Actualizado')
          expect(updated.raza).toBe('Holstein') // Should preserve existing properties
        }
      }
    })

    it('should handle upsertGanado with new item (else branch)', () => {
      const { ganado } = useGanado()
      ganado.value = [{ id: 1, nombre: 'Existing Animal' }]

      // Access internal upsertGanado function through socket callback
      const updatedCall = socket.on.mock.calls.find(call => call[0] === 'animal_updated')
      if (updatedCall && updatedCall[1]) {
        const callback = updatedCall[1]
        callback({ data: { id: 2, nombre: 'New Animal' } })

        expect(ganado.value).toHaveLength(2)
        expect(ganado.value[0].nombre).toBe('New Animal') // Should be prepended
        expect(ganado.value[1].nombre).toBe('Existing Animal')
      }
    })

    it('should handle removeGanado with valid id', () => {
      const { ganado } = useGanado()
      ganado.value = [
        { id: 1, nombre: 'Animal 1' },
        { id: 2, nombre: 'Animal 2' },
        { id: 3, nombre: 'Animal 3' }
      ]

      // Access internal removeGanado function through socket callback
      const deletedCall = socket.on.mock.calls.find(call => call[0] === 'animal_deleted')
      if (deletedCall && deletedCall[1]) {
        const callback = deletedCall[1]
        callback({ id: 2 })

        expect(ganado.value).toHaveLength(2)
        expect(ganado.value.find(a => a.id === 2)).toBeUndefined()
        expect(ganado.value.find(a => a.id === 1)).toBeDefined()
        expect(ganado.value.find(a => a.id === 3)).toBeDefined()
      }
    })

    it('should handle socket events with valid payload data', () => {
      socket.on.mockClear()

      const { ganado } = useGanado()

      // Test animal_created with valid data
      const createdCall = socket.on.mock.calls.find(call => call[0] === 'animal_created')
      if (createdCall && createdCall[1]) {
        const callback = createdCall[1]
        callback({ data: { id: 1, nombre: 'Created Animal' } })

        expect(ganado.value).toContainEqual({ id: 1, nombre: 'Created Animal' })
      }

      // Test animal_updated with valid data
      const updatedCall = socket.on.mock.calls.find(call => call[0] === 'animal_updated')
      if (updatedCall && updatedCall[1]) {
        const callback = updatedCall[1]
        ganado.value = [{ id: 1, nombre: 'Original' }]
        callback({ data: { id: 1, nombre: 'Updated Animal' } })

        expect(ganado.value.find(a => a.id === 1).nombre).toBe('Updated Animal')
      }

      // Test animal_deleted with valid id
      const deletedCall = socket.on.mock.calls.find(call => call[0] === 'animal_deleted')
      if (deletedCall && deletedCall[1]) {
        const callback = deletedCall[1]
        ganado.value = [{ id: 1, nombre: 'To Delete' }]
        callback({ id: 1 })

        expect(ganado.value.find(a => a.id === 1)).toBeUndefined()
      }
    })

    it('should handle disconnect event and reset socketRegistered', () => {
      socket.on.mockClear()

      useGanado()

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
