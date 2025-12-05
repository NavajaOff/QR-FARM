import { beforeEach, afterEach, vi, describe, it, expect } from 'vitest'
import { useTenantSelector } from './useTenantSelector.js'
import { useTenants } from './useTenants.js'
import authService from '../services/authService.js'

vi.mock('./useTenants.js', () => ({
  useTenants: vi.fn()
}))

vi.mock('../services/authService.js', () => ({
  default: {
    getRole: vi.fn()
  }
}))

describe('useTenantSelector', () => {
  let mockTenants
  let mockLoading
  let mockError
  let mockCargarTenants

  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()

    mockTenants = { value: [] }
    mockLoading = { value: false }
    mockError = { value: null }
    mockCargarTenants = vi.fn()

    useTenants.mockReturnValue({
      tenants: mockTenants,
      loading: mockLoading,
      error: mockError,
      cargarTenants: mockCargarTenants
    })

    authService.getRole.mockReturnValue('user')
  })

  afterEach(() => {
    localStorage.clear()
  })

  it('should export useTenantSelector function', () => {
    expect(useTenantSelector).toBeDefined()
    expect(typeof useTenantSelector).toBe('function')
  })

  it('should initialize with null selected tenant', () => {
    const result = useTenantSelector()

    expect(result.selectedTenantId.value).toBeNull()
    expect(result.selectedTenantName.value).toBeNull()
  })

  it('should load selected tenant from localStorage', () => {
    localStorage.setItem('qr_farm_selected_tenant_id', '123')
    localStorage.setItem('qr_farm_selected_tenant_name', 'Test Tenant')

    const result = useTenantSelector()

    expect(result.selectedTenantId.value).toBe(123)
    expect(result.selectedTenantName.value).toBe('Test Tenant')
  })

  it('should handle invalid tenant ID in localStorage', () => {
    localStorage.setItem('qr_farm_selected_tenant_id', 'invalid')

    const result = useTenantSelector()

    expect(result.selectedTenantId.value).toBeNull()
  })

  it('should handle missing tenant name in localStorage', () => {
    localStorage.setItem('qr_farm_selected_tenant_id', '123')

    const result = useTenantSelector()

    expect(result.selectedTenantId.value).toBe(123)
    expect(result.selectedTenantName.value).toBeNull()
  })

  it('should handle localStorage errors gracefully', () => {
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    const getItemSpy = vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
      throw new Error('Storage error')
    })

    const result = useTenantSelector()

    expect(result.selectedTenantId.value).toBeNull()
    expect(consoleErrorSpy).toHaveBeenCalled()

    getItemSpy.mockRestore()
    consoleErrorSpy.mockRestore()
  })

  describe('isSuperAdmin', () => {
    it('should return true for super_admin role', () => {
      authService.getRole.mockReturnValue('super_admin')

      const result = useTenantSelector()

      expect(result.isSuperAdmin.value).toBe(true)
    })

    it('should return false for non-super_admin roles', () => {
      authService.getRole.mockReturnValue('admin')

      const result = useTenantSelector()

      expect(result.isSuperAdmin.value).toBe(false)
    })

    it('should return false for user role', () => {
      authService.getRole.mockReturnValue('user')

      const result = useTenantSelector()

      expect(result.isSuperAdmin.value).toBe(false)
    })
  })

  describe('shouldShowSelector', () => {
    it('should return true for super_admin', () => {
      authService.getRole.mockReturnValue('super_admin')

      const result = useTenantSelector()

      expect(result.shouldShowSelector.value).toBe(true)
    })

    it('should return false for non-super_admin', () => {
      authService.getRole.mockReturnValue('admin')

      const result = useTenantSelector()

      expect(result.shouldShowSelector.value).toBe(false)
    })
  })

  describe('currentTenant', () => {
    it('should return null when no tenant selected', () => {
      mockTenants.value = [
        { id: 1, nombre: 'Tenant 1' },
        { id: 2, nombre: 'Tenant 2' }
      ]

      const result = useTenantSelector()

      expect(result.currentTenant.value).toBeNull()
    })

    it('should return tenant when selected', () => {
      mockTenants.value = [
        { id: 1, nombre: 'Tenant 1' },
        { id: 2, nombre: 'Tenant 2' }
      ]

      const result = useTenantSelector()
      result.selectTenant(1, 'Tenant 1')

      expect(result.currentTenant.value).toEqual({ id: 1, nombre: 'Tenant 1' })
    })

    it('should return null when selected tenant not in list', () => {
      mockTenants.value = [
        { id: 1, nombre: 'Tenant 1' }
      ]

      const result = useTenantSelector()
      result.selectTenant(999, 'Missing Tenant')

      expect(result.currentTenant.value).toBeNull()
    })
  })

  describe('selectTenant', () => {
    it('should select tenant and save to localStorage', () => {
      const result = useTenantSelector()

      result.selectTenant(123, 'Test Tenant')

      expect(result.selectedTenantId.value).toBe(123)
      expect(result.selectedTenantName.value).toBe('Test Tenant')
      expect(localStorage.getItem('qr_farm_selected_tenant_id')).toBe('123')
      expect(localStorage.getItem('qr_farm_selected_tenant_name')).toBe('Test Tenant')
    })

    it('should clear selection when null is passed', () => {
      localStorage.setItem('qr_farm_selected_tenant_id', '123')
      localStorage.setItem('qr_farm_selected_tenant_name', 'Test Tenant')

      const result = useTenantSelector()
      result.selectTenant(null)

      expect(result.selectedTenantId.value).toBeNull()
      expect(result.selectedTenantName.value).toBeNull()
      expect(localStorage.getItem('qr_farm_selected_tenant_id')).toBeNull()
      expect(localStorage.getItem('qr_farm_selected_tenant_name')).toBeNull()
    })

    it('should handle invalid tenant ID', () => {
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      const result = useTenantSelector()

      result.selectTenant('invalid')

      expect(result.selectedTenantId.value).toBeNull()
      expect(consoleErrorSpy).toHaveBeenCalled()

      consoleErrorSpy.mockRestore()
    })

    it('should handle errors during selection', () => {
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      const setItemSpy = vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
        throw new Error('Storage error')
      })

      const result = useTenantSelector()

      result.selectTenant(123, 'Test')

      expect(consoleErrorSpy).toHaveBeenCalled()

      setItemSpy.mockRestore()
      consoleErrorSpy.mockRestore()
    })

    it('should work without tenant name', () => {
      const result = useTenantSelector()

      result.selectTenant(123)

      expect(result.selectedTenantId.value).toBe(123)
      expect(result.selectedTenantName.value).toBeNull()
      expect(localStorage.getItem('qr_farm_selected_tenant_id')).toBe('123')
    })
  })

  describe('clearTenant', () => {
    it('should clear tenant selection', () => {
      localStorage.setItem('qr_farm_selected_tenant_id', '123')
      localStorage.setItem('qr_farm_selected_tenant_name', 'Test Tenant')

      const result = useTenantSelector()
      result.clearTenant()

      expect(result.selectedTenantId.value).toBeNull()
      expect(result.selectedTenantName.value).toBeNull()
    })
  })

  describe('loadTenants', () => {
    it('should load tenants for super_admin', async () => {
      authService.getRole.mockReturnValue('super_admin')

      const result = useTenantSelector()
      await result.loadTenants()

      expect(mockCargarTenants).toHaveBeenCalledWith(true)
    })

    it('should not load tenants for non-super_admin', async () => {
      authService.getRole.mockReturnValue('admin')

      const result = useTenantSelector()
      await result.loadTenants()

      expect(mockCargarTenants).not.toHaveBeenCalled()
    })
  })

  describe('return values', () => {
    it('should return all expected properties', () => {
      const result = useTenantSelector()

      expect(result).toHaveProperty('selectedTenantId')
      expect(result).toHaveProperty('selectedTenantName')
      expect(result).toHaveProperty('tenants')
      expect(result).toHaveProperty('loading')
      expect(result).toHaveProperty('error')
      expect(result).toHaveProperty('isSuperAdmin')
      expect(result).toHaveProperty('shouldShowSelector')
      expect(result).toHaveProperty('currentTenant')
      expect(result).toHaveProperty('selectTenant')
      expect(result).toHaveProperty('clearTenant')
      expect(result).toHaveProperty('loadTenants')
    })
  })
})

