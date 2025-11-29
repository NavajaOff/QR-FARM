import { useTenants } from './useTenants'

describe('useTenants', () => {
  it('should export useTenants composable', () => {
    expect(useTenants).toBeDefined()
    expect(typeof useTenants).toBe('function')
  })
})