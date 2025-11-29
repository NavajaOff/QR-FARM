import { useTenants } from './useTenants'
import { tenantAPI } from '../services/api.js'

jest.mock('../services/api.js', () => ({
  tenantAPI: {
    getAll: jest.fn(),
    create: jest.fn(),
    update: jest.fn(),
    delete: jest.fn(),
    getById: jest.fn()
  }
}))

describe('useTenants', () => {
  beforeEach(() => {
    jest.clearAllMocks()
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
})