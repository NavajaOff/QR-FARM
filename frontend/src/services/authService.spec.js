import authService from './authService'
import api from './api.js'

jest.mock('./api.js', () => ({
  __esModule: true,
  default: {
    post: jest.fn()
  }
}))

describe('authService', () => {
  beforeEach(() => {
    localStorage.clear()
    sessionStorage.clear()
    jest.clearAllMocks()
  })

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

  it('should return false when not authenticated', () => {
    expect(authService.isAuthenticated()).toBe(false)
  })

  it('should return true when token is valid', () => {
    const payload = { exp: Math.floor(Date.now() / 1000) + 3600 }
    const token = `header.${btoa(JSON.stringify(payload))}.signature`
    localStorage.setItem('token', token)
    expect(authService.isAuthenticated()).toBe(true)
  })

  it('should return false when token is expired', () => {
    const payload = { exp: Math.floor(Date.now() / 1000) - 3600 }
    const token = `header.${btoa(JSON.stringify(payload))}.signature`
    localStorage.setItem('token', token)
    expect(authService.isAuthenticated()).toBe(false)
  })

  it('should get token from localStorage', () => {
    localStorage.setItem('token', 'test-token')
    expect(authService.getToken()).toBe('test-token')
  })

  it('should get user from localStorage', () => {
    const userData = { id: 1, email: 'test@example.com' }
    localStorage.setItem('user', JSON.stringify(userData))
    expect(authService.getUser()).toEqual(userData)
  })

  it('should return null for invalid user data', () => {
    localStorage.setItem('user', 'invalid-json')
    expect(authService.getUser()).toBeNull()
  })

  it('should login successfully', async () => {
    const mockResponse = {
      data: {
        status: 'success',
        token: 'test-token',
        user: { id: 1, email: 'test@example.com' }
      }
    }
    api.post.mockResolvedValue(mockResponse)

    const result = await authService.login('test@example.com', 'password')

    expect(result.success).toBe(true)
    expect(localStorage.getItem('token')).toBe('test-token')
  })

  it('should handle login error', async () => {
    api.post.mockRejectedValue(new Error('Invalid credentials'))

    const result = await authService.login('test@example.com', 'wrong-password')

    expect(result.success).toBe(false)
  })

  it('should logout and clear storage', () => {
    localStorage.setItem('token', 'test-token')
    localStorage.setItem('user', '{"id": 1}')
    sessionStorage.setItem('lastLoginEmail', 'test@example.com')

    authService.logout()

    expect(localStorage.getItem('token')).toBeNull()
    expect(localStorage.getItem('user')).toBeNull()
    expect(sessionStorage.getItem('lastLoginEmail')).toBeNull()
  })

  it('should get role from user', () => {
    const userData = { id: 1, rol: { nombre_rol: 'admin' } }
    localStorage.setItem('user', JSON.stringify(userData))
    expect(authService.getRole()).toBe('admin')
  })

  it('should return null role when no user', () => {
    expect(authService.getRole()).toBeNull()
  })

  it('should check if user is super admin', () => {
    const userData = { id: 1, rol: { nombre_rol: 'super_admin' } }
    localStorage.setItem('user', JSON.stringify(userData))
    expect(authService.isSuperAdmin()).toBe(true)
  })

  it('should return false when not super admin', () => {
    const userData = { id: 1, rol: { nombre_rol: 'usuario' } }
    localStorage.setItem('user', JSON.stringify(userData))
    expect(authService.isSuperAdmin()).toBe(false)
  })
})