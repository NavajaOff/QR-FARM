import api, { authAPI, userAPI } from './api'

describe('api', () => {
  it('should export api service', () => {
    expect(api).toBeDefined()
    expect(typeof api).toBe('function')
  })

  it('should have expected methods', () => {
    expect(api.get).toBeDefined()
    expect(api.post).toBeDefined()
    expect(api.put).toBeDefined()
    expect(api.delete).toBeDefined()
  })

  it('should export API modules', () => {
    expect(authAPI).toBeDefined()
    expect(userAPI).toBeDefined()
    expect(typeof authAPI.login).toBe('function')
    expect(typeof userAPI.getAll).toBe('function')
  })
})