import { useTenantSelection } from './useTenantSelection'

describe('useTenantSelection', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('should export useTenantSelection composable', () => {
    expect(useTenantSelection).toBeDefined()
    expect(typeof useTenantSelection).toBe('function')
  })

  it('should initialize with null if no stored value', () => {
    const { selectedTenantId } = useTenantSelection()
    expect(selectedTenantId.value).toBeNull()
  })

  it('should load tenant from localStorage', () => {
    localStorage.setItem('qr_farm_selected_tenant_id', '123')
    const { selectedTenantId } = useTenantSelection()
    expect(selectedTenantId.value).toBe(123)
  })

  it('should set selected tenant id', () => {
    const { setSelectedTenantId, selectedTenantId } = useTenantSelection()
    setSelectedTenantId(456)
    expect(selectedTenantId.value).toBe(456)
    expect(localStorage.getItem('qr_farm_selected_tenant_id')).toBe('456')
  })

  it('should clear selected tenant', () => {
    localStorage.setItem('qr_farm_selected_tenant_id', '123')
    const { clearSelectedTenant, selectedTenantId } = useTenantSelection()
    clearSelectedTenant()
    expect(selectedTenantId.value).toBeNull()
    expect(localStorage.getItem('qr_farm_selected_tenant_id')).toBeNull()
  })

  it('should handle invalid stored value', () => {
    localStorage.setItem('qr_farm_selected_tenant_id', 'invalid')
    const { selectedTenantId } = useTenantSelection()
    expect(selectedTenantId.value).toBeNull()
  })

  it('should handle localStorage errors gracefully', () => {
    const originalGetItem = localStorage.getItem
    localStorage.getItem = jest.fn(() => {
      throw new Error('Storage error')
    })

    const { selectedTenantId } = useTenantSelection()
    expect(selectedTenantId.value).toBeNull()

    localStorage.getItem = originalGetItem
  })
})