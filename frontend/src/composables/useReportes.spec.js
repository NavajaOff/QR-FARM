import { useReportes } from './useReportes'

describe('useReportes', () => {
  it('should export useReportes composable', () => {
    expect(useReportes).toBeDefined()
    expect(typeof useReportes).toBe('function')
  })
})