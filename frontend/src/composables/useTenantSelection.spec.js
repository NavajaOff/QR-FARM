import { useTenantSelection } from './useTenantSelection'

describe('useTenantSelection', () => {
  it('should export useTenantSelection composable', () => {
    expect(useTenantSelection).toBeDefined()
    expect(typeof useTenantSelection).toBe('function')
  })
})