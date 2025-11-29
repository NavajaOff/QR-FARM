import authService from './authService'

describe('authService', () => {
  it('should export authService', () => {
    expect(authService).toBeDefined()
    expect(typeof authService).toBe('object')
  })

  it('should have login method', () => {
    expect(authService.login).toBeDefined()
    expect(typeof authService.login).toBe('function')
  })

  it('should have logout method', () => {
    expect(authService.logout).toBeDefined()
    expect(typeof authService.logout).toBe('function')
  })
})