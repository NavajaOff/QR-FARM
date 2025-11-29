import { useUsuarios } from './useUsuarios'

describe('useUsuarios', () => {
  it('should export useUsuarios composable', () => {
    expect(useUsuarios).toBeDefined()
    expect(typeof useUsuarios).toBe('function')
  })
})