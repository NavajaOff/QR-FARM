import { useGanado } from './useGanado'

describe('useGanado', () => {
  it('should export useGanado composable', () => {
    expect(useGanado).toBeDefined()
    expect(typeof useGanado).toBe('function')
  })
})