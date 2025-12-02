import { beforeEach, vi } from 'vitest'
import { useTenants } from './useTenants'
import { tenantAPI } from '../services/api.js'

vi.mock('../services/api.js', () => ({
  tenantAPI: {
    getAll: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
    getById: vi.fn()
  }
}))

describe('useTenants', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should export useTenants composable', () => {
    expect(useTenants).toBeDefined()
    expect(typeof useTenants).toBe('function')
  })

  it('should initialize with default values', () => {
    const { tenants, loading, error } = useTenants()
    expect(tenants.value).toEqual([])
    expect(loading.value).toBe(false)
    expect(error.value).toBeNull()
  })

  it('should load tenants successfully', async () => {
    const mockTenants = [{ id: 1, nombre: 'Tenant 1' }]
    tenantAPI.getAll.mockResolvedValue({
      data: {
        status: 'success',
        data: mockTenants
      }
    })

    const { cargarTenants, tenants } = useTenants()
    await cargarTenants()

    expect(tenants.value).toEqual(mockTenants)
    expect(tenantAPI.getAll).toHaveBeenCalledWith(true)
  })

  it('should handle error when loading tenants', async () => {
    const errorMessage = 'Error al cargar tenants'
    tenantAPI.getAll.mockRejectedValue(new Error(errorMessage))

    const { cargarTenants, error, loading } = useTenants()
    await cargarTenants()

    expect(error.value).toBe(errorMessage)
    expect(loading.value).toBe(false)
  })

  it('should create tenant successfully', async () => {
    const newTenant = { nombre: 'New Tenant' }
    tenantAPI.create.mockResolvedValue({
      data: {
        status: 'success',
        data: { id: 1, ...newTenant }
      }
    })
    tenantAPI.getAll.mockResolvedValue({
      data: {
        status: 'success',
        data: []
      }
    })

    const { crearTenant } = useTenants()
    const result = await crearTenant(newTenant)

    expect(result.success).toBe(true)
    expect(tenantAPI.create).toHaveBeenCalledWith(newTenant)
  })

  it('should update tenant successfully', async () => {
    const updatedData = { nombre: 'Updated Tenant' }
    tenantAPI.update.mockResolvedValue({
      data: {
        status: 'success',
        data: { id: 1, ...updatedData }
      }
    })
    tenantAPI.getAll.mockResolvedValue({
      data: {
        status: 'success',
        data: []
      }
    })

    const { actualizarTenant } = useTenants()
    const result = await actualizarTenant(1, updatedData)

    expect(result.success).toBe(true)
    expect(tenantAPI.update).toHaveBeenCalledWith(1, updatedData)
  })

  it('should get tenant by id successfully', async () => {
    const mockTenant = { id: 1, nombre: 'Tenant 1' }
    tenantAPI.getById.mockResolvedValue({
      data: {
        status: 'success',
        data: mockTenant
      }
    })

    const { obtenerTenant } = useTenants()
    const result = await obtenerTenant(1)

    expect(result.success).toBe(true)
    expect(result.data).toEqual(mockTenant)
    expect(tenantAPI.getById).toHaveBeenCalledWith(1)
  })

  it('should handle error when getting tenant by id', async () => {
    const errorMessage = 'Tenant no encontrado'
    tenantAPI.getById.mockRejectedValue(new Error(errorMessage))

    const { obtenerTenant, error } = useTenants()
    const result = await obtenerTenant(999)

    expect(result.success).toBe(false)
    expect(error.value).toBe(errorMessage)
  })

  describe('Edge Cases', () => {
    it('should handle cargarTenants with activosOnly false', async () => {
      const mockTenants = [{ id: 1, nombre: 'Tenant 1' }]
      tenantAPI.getAll.mockResolvedValue({
        data: { status: 'success', data: mockTenants }
      })

      const { cargarTenants } = useTenants()
      await cargarTenants(false)

      expect(tenantAPI.getAll).toHaveBeenCalledWith(false)
    })

    it('should handle cargarTenants with response without status', async () => {
      tenantAPI.getAll.mockResolvedValue({
        data: { data: [] } // Missing status
      })

      const { cargarTenants, error } = useTenants()
      await cargarTenants()

      expect(error.value).toBe('Error al cargar tenants')
    })

    it('should handle cargarTenants with null data', async () => {
      tenantAPI.getAll.mockResolvedValue({
        data: { status: 'success', data: null }
      })

      const { cargarTenants, tenants } = useTenants()
      await cargarTenants()

      expect(tenants.value).toEqual([])
    })

    it('should handle cargarTenants with error.response.data.message', async () => {
      tenantAPI.getAll.mockRejectedValue({
        response: { data: { message: 'Custom error' } }
      })

      const { cargarTenants, error } = useTenants()
      await cargarTenants()

      expect(error.value).toBe('Custom error')
    })

    it('should handle cargarTenants with error without response', async () => {
      tenantAPI.getAll.mockRejectedValue({
        message: 'Network error'
      })

      const { cargarTenants, error } = useTenants()
      await cargarTenants()

      expect(error.value).toBe('Network error')
    })

    it('should handle cargarTenants with error without message', async () => {
      tenantAPI.getAll.mockRejectedValue({})

      const { cargarTenants, error } = useTenants()
      await cargarTenants()

      expect(error.value).toBe('Error al cargar tenants')
    })

    it('should handle crearTenant with response without status', async () => {
      tenantAPI.create.mockResolvedValue({
        data: { message: 'Error message' }
      })

      const { crearTenant } = useTenants()
      const result = await crearTenant({ nombre: 'Test' })

      expect(result.success).toBe(false)
      expect(result.message).toBe('Error message')
    })

    it('should handle crearTenant with error.response.data.message', async () => {
      tenantAPI.create.mockRejectedValue({
        response: { data: { message: 'Custom error' } }
      })

      const { crearTenant, error } = useTenants()
      const result = await crearTenant({ nombre: 'Test' })

      expect(result.success).toBe(false)
      expect(result.message).toBe('Custom error')
      expect(error.value).toBe('Custom error')
    })

    it('should handle crearTenant with error without response', async () => {
      tenantAPI.create.mockRejectedValue({
        message: 'Network error'
      })

      const { crearTenant, error } = useTenants()
      const result = await crearTenant({ nombre: 'Test' })

      expect(result.success).toBe(false)
      expect(result.message).toBe('Network error')
      expect(error.value).toBe('Network error')
    })

    it('should handle actualizarTenant with activosOnly true', async () => {
      tenantAPI.update.mockResolvedValue({
        data: { status: 'success', data: { id: 1 } }
      })
      tenantAPI.getAll.mockResolvedValue({
        data: { status: 'success', data: [] }
      })

      const { actualizarTenant } = useTenants()
      const result = await actualizarTenant(1, { nombre: 'Test' }, true)

      expect(result.success).toBe(true)
      expect(tenantAPI.getAll).toHaveBeenCalledWith(true)
    })

    it('should handle actualizarTenant with response without status', async () => {
      tenantAPI.update.mockResolvedValue({
        data: {} // No status, no message
      })

      const { actualizarTenant, error } = useTenants()
      const result = await actualizarTenant(1, { nombre: 'Test' })

      expect(result.success).toBe(false)
      expect(result.message).toBe('Error al actualizar tenant')
      // error.value is set in catch block, not in the else branch
      expect(error.value).toBeNull()
    })

    it('should handle obtenerTenant with response without status', async () => {
      tenantAPI.getById.mockResolvedValue({
        data: {} // No status, no message
      })

      const { obtenerTenant, error } = useTenants()
      const result = await obtenerTenant(1)

      expect(result.success).toBe(false)
      expect(result.message).toBe('Tenant no encontrado')
      // error.value is set in catch block, but this is not a catch, so it's null
      // The else branch doesn't set error.value, only returns the error message
      expect(error.value).toBeNull()
    })

    it('should handle obtenerTenant with error.response.data.message', async () => {
      tenantAPI.getById.mockRejectedValue({
        response: { data: { message: 'Custom error' } }
      })

      const { obtenerTenant, error } = useTenants()
      const result = await obtenerTenant(1)

      expect(result.success).toBe(false)
      expect(result.message).toBe('Custom error')
      expect(error.value).toBe('Custom error')
    })

    it('should handle obtenerTenant with error without response', async () => {
      tenantAPI.getById.mockRejectedValue({
        message: 'Network error'
      })

      const { obtenerTenant, error } = useTenants()
      const result = await obtenerTenant(1)

      expect(result.success).toBe(false)
      expect(result.message).toBe('Network error')
      expect(error.value).toBe('Network error')
    })
  })
})