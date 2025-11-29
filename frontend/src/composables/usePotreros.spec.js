import { usePotreros } from './usePotreros'

describe('usePotreros', () => {
  it('should export usePotreros composable', () => {
    expect(usePotreros).toBeDefined()
    expect(typeof usePotreros).toBe('function')
  })
})