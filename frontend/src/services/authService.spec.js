import { beforeEach, vi } from 'vitest'
import authService from './authService'
import api from './api.js'

// Test constants to avoid hardcoded credentials
const TEST_EMAIL = 'test@example.com'
const TEST_PASSWORD = 'test-password-123'
const TEST_WRONG_PASSWORD = 'wrong-password-456'

// Mock de api
vi.mock('./api.js', () => ({
  default: {
    post: vi.fn()
  }
}))

describe('authService', () => {
  beforeEach(() => {
    localStorage.clear()
    sessionStorage.clear()
    vi.clearAllMocks()
    console.log = vi.fn()
    console.error = vi.fn()
    console.warn = vi.fn()
    
    // Resetear estado interno del servicio
    authService.token = null
    authService.user = null
    authService.role = null
  })

  describe('Service Instance', () => {
  it('should export authService', () => {
    expect(authService).toBeDefined()
    expect(typeof authService).toBe('object')
  })

    it('should have all required methods', () => {
    expect(typeof authService.login).toBe('function')
      expect(typeof authService.logout).toBe('function')
      expect(typeof authService.isAuthenticated).toBe('function')
      expect(typeof authService.getToken).toBe('function')
      expect(typeof authService.getUser).toBe('function')
      expect(typeof authService.getRole).toBe('function')
      expect(typeof authService.isAdmin).toBe('function')
      expect(typeof authService.isSuperAdmin).toBe('function')
      expect(typeof authService.isUser).toBe('function')
      expect(typeof authService.saveCredentialsForRenewal).toBe('function')
      expect(typeof authService.hasPermission).toBe('function')
      expect(typeof authService.getRedirectPath).toBe('function')
    })
  })

  describe('isAuthenticated', () => {
    it('should return false when not authenticated', () => {
      expect(authService.isAuthenticated()).toBe(false)
    })

    it('should return false when token is null', () => {
      localStorage.removeItem('token')
      expect(authService.isAuthenticated()).toBe(false)
    })

    it('should return true when token is valid', () => {
      const payload = { exp: Math.floor(Date.now() / 1000) + 3600 }
      const token = `header.${btoa(JSON.stringify(payload))}.signature`
      localStorage.setItem('token', token)
      authService.token = null // Reset cache
      expect(authService.isAuthenticated()).toBe(true)
    })

    it('should return false when token is expired', () => {
      const payload = { exp: Math.floor(Date.now() / 1000) - 3600 }
      const token = `header.${btoa(JSON.stringify(payload))}.signature`
      localStorage.setItem('token', token)
      authService.token = null // Reset cache
      expect(authService.isAuthenticated()).toBe(false)
    })

    it('should return false when token is invalid format', () => {
      localStorage.setItem('token', 'invalid-token')
      authService.token = null // Reset cache
      expect(authService.isAuthenticated()).toBe(false)
    })

    it('should return false when token payload is invalid JSON', () => {
      const token = `header.${btoa('invalid-json')}.signature`
      localStorage.setItem('token', token)
      authService.token = null // Reset cache
      expect(authService.isAuthenticated()).toBe(false)
    })

    it('should return false when token has no exp field', () => {
      const payload = { role: 'admin' }
      const token = `header.${btoa(JSON.stringify(payload))}.signature`
      localStorage.setItem('token', token)
      authService.token = null // Reset cache
      expect(authService.isAuthenticated()).toBe(false)
    })
  })

  describe('getToken', () => {
    it('should get token from localStorage', () => {
      localStorage.setItem('token', 'test-token')
      authService.token = null // Reset cache
      expect(authService.getToken()).toBe('test-token')
    })

    it('should return cached token if available', () => {
      authService.token = 'cached-token'
      expect(authService.getToken()).toBe('cached-token')
    })

    it('should return null when token is not in localStorage', () => {
      localStorage.removeItem('token')
      authService.token = null // Reset cache
      expect(authService.getToken()).toBeNull()
    })
  })

  describe('getUser', () => {
    it('should get user from localStorage', () => {
      const userData = { id: 1, email: 'test@example.com' }
      localStorage.setItem('user', JSON.stringify(userData))
      authService.user = null // Reset cache
      expect(authService.getUser()).toEqual(userData)
    })

    it('should return cached user if available', () => {
      const cachedUser = { id: 1, email: 'cached@example.com' }
      authService.user = cachedUser
      expect(authService.getUser()).toEqual(cachedUser)
    })

    it('should return null for invalid user data', () => {
      localStorage.setItem('user', 'invalid-json')
      authService.user = null // Reset cache
      expect(authService.getUser()).toBeNull()
      expect(localStorage.getItem('user')).toBeNull() // Should be removed
    })

    it('should return null when user is undefined string', () => {
      localStorage.setItem('user', 'undefined')
      authService.user = null // Reset cache
      expect(authService.getUser()).toBeNull()
    })

    it('should return null when user is null string', () => {
      localStorage.setItem('user', 'null')
      authService.user = null // Reset cache
      expect(authService.getUser()).toBeNull()
    })

    it('should return null when user is empty string', () => {
      localStorage.setItem('user', '')
      authService.user = null // Reset cache
      expect(authService.getUser()).toBeNull()
    })

    it('should return null when user is whitespace only', () => {
      localStorage.setItem('user', '   ')
      authService.user = null // Reset cache
      expect(authService.getUser()).toBeNull()
    })

    it('should handle parsing error and log it', () => {
      localStorage.setItem('user', '{invalid json}')
      authService.user = null // Reset cache
      const result = authService.getUser()
      expect(result).toBeNull()
      expect(console.error).toHaveBeenCalled()
      expect(console.log).toHaveBeenCalled()
    })
  })

  describe('getRole', () => {
    it('should get role from localStorage', () => {
      localStorage.setItem('userRole', 'admin')
      authService.role = null // Reset cache
      const role = authService.getRole()
      expect(role).toBe('admin')
    })

    it('should return null when role is not in localStorage', () => {
      localStorage.removeItem('userRole')
      authService.role = null // Reset cache
      expect(authService.getRole()).toBeNull()
    })

    it('should update internal state when role changes', () => {
      localStorage.setItem('userRole', 'admin')
      authService.role = null // Reset cache
      authService.getRole()
      expect(authService.role).toBe('admin')
      expect(console.log).toHaveBeenCalled()
    })

    it('should not update internal state when role is the same', () => {
      authService.role = 'admin'
      localStorage.setItem('userRole', 'admin')
      authService.getRole()
      // Should not log if role hasn't changed
      expect(authService.role).toBe('admin')
    })
  })

  describe('isAdmin', () => {
    it('should return true for admin role', () => {
      localStorage.setItem('userRole', 'admin')
      authService.role = null // Reset cache
      expect(authService.isAdmin()).toBe(true)
      expect(console.log).toHaveBeenCalled()
    })

    it('should return true for administrador role', () => {
      localStorage.setItem('userRole', 'administrador')
      authService.role = null // Reset cache
      expect(authService.isAdmin()).toBe(true)
    })

    it('should return true for super_admin role', () => {
      localStorage.setItem('userRole', 'super_admin')
      authService.role = null // Reset cache
      expect(authService.isAdmin()).toBe(true)
    })

    it('should return false for user role', () => {
      localStorage.setItem('userRole', 'user')
      authService.role = null // Reset cache
      expect(authService.isAdmin()).toBe(false)
    })

    it('should return false when role is null', () => {
      localStorage.removeItem('userRole')
      authService.role = null // Reset cache
      expect(authService.isAdmin()).toBe(false)
    })
  })

  describe('isSuperAdmin', () => {
    it('should return true for super_admin role', () => {
      localStorage.setItem('userRole', 'super_admin')
      authService.role = null // Reset cache
      expect(authService.isSuperAdmin()).toBe(true)
    })

    it('should return false for admin role', () => {
      localStorage.setItem('userRole', 'admin')
      authService.role = null // Reset cache
      expect(authService.isSuperAdmin()).toBe(false)
    })

    it('should return false when role is null', () => {
      localStorage.removeItem('userRole')
      authService.role = null // Reset cache
      expect(authService.isSuperAdmin()).toBe(false)
    })
  })

  describe('isUser', () => {
    it('should return true for user role', () => {
      localStorage.setItem('userRole', 'user')
      authService.role = null // Reset cache
      expect(authService.isUser()).toBe(true)
      expect(console.log).toHaveBeenCalled()
    })

    it('should return true for usuario role', () => {
      localStorage.setItem('userRole', 'usuario')
      authService.role = null // Reset cache
      expect(authService.isUser()).toBe(true)
    })

    it('should return false for admin role', () => {
      localStorage.setItem('userRole', 'admin')
      authService.role = null // Reset cache
      expect(authService.isUser()).toBe(false)
    })

    it('should return false when role is null', () => {
      localStorage.removeItem('userRole')
      authService.role = null // Reset cache
      expect(authService.isUser()).toBe(false)
    })
  })

  describe('saveCredentialsForRenewal', () => {
    it('should save email to sessionStorage when email is valid string', () => {
      authService.saveCredentialsForRenewal('test@example.com')
      expect(sessionStorage.getItem('lastLoginEmail')).toBe('test@example.com')
    })

    it('should not save email when email is not a string', () => {
      authService.saveCredentialsForRenewal(123)
      expect(sessionStorage.getItem('lastLoginEmail')).toBeNull()
    })

    it('should not save email when email is null', () => {
      authService.saveCredentialsForRenewal(null)
      expect(sessionStorage.getItem('lastLoginEmail')).toBeNull()
    })

    it('should not save email when email is undefined', () => {
      authService.saveCredentialsForRenewal(undefined)
      expect(sessionStorage.getItem('lastLoginEmail')).toBeNull()
    })

    it('should not save email when email is empty string', () => {
      authService.saveCredentialsForRenewal('')
      expect(sessionStorage.getItem('lastLoginEmail')).toBeNull()
    })
  })

  describe('login', () => {
    it('should login successfully', async () => {
      const payload = { role: 'admin', exp: Math.floor(Date.now() / 1000) + 3600 }
      const token = `header.${btoa(JSON.stringify(payload))}.signature`
      const mockResponse = {
        data: {
          status: 'success',
          token: token,
          user: { id: 1, email: 'test@example.com' }
        }
      }
      api.post.mockResolvedValue(mockResponse)

      const credentials = { email: TEST_EMAIL, password: TEST_PASSWORD }
      const result = await authService.login(credentials)

      expect(result.success).toBe(true)
      expect(result.user).toEqual(mockResponse.data.user)
      expect(result.role).toBe('admin')
      expect(localStorage.getItem('token')).toBe(token)
      expect(localStorage.getItem('user')).toBe(JSON.stringify(mockResponse.data.user))
      expect(localStorage.getItem('userRole')).toBe('admin')
      expect(sessionStorage.getItem('lastLoginEmail')).toBe('test@example.com')
      expect(authService.token).toBe(token)
      expect(authService.user).toEqual(mockResponse.data.user)
      expect(authService.role).toBe('admin')
      expect(console.log).toHaveBeenCalled()
    })

    it('should handle login failure when status is not success', async () => {
      const mockResponse = {
        data: {
          status: 'error',
          message: 'Invalid credentials'
        }
      }
      api.post.mockResolvedValue(mockResponse)

      const credentials = { email: TEST_EMAIL, password: TEST_WRONG_PASSWORD }
      const result = await authService.login(credentials)

      expect(result.success).toBe(false)
      expect(result.message).toBe('Invalid credentials')
    })

    it('should handle login error with response data', async () => {
      const error = {
        response: {
          data: {
            message: 'Network error'
          }
        }
      }
      api.post.mockRejectedValue(error)

      const credentials = { email: TEST_EMAIL, password: TEST_PASSWORD }
      const result = await authService.login(credentials)

      expect(result.success).toBe(false)
      expect(result.message).toBe('Network error')
    })

    it('should handle login error without response data', async () => {
      const error = new Error('Connection failed')
      api.post.mockRejectedValue(error)

      const credentials = { email: TEST_EMAIL, password: TEST_PASSWORD }
      const result = await authService.login(credentials)

      expect(result.success).toBe(false)
      expect(result.message).toBe('Error al iniciar sesión')
    })

    it('should not save email when credentials do not have email', async () => {
      const payload = { role: 'admin', exp: Math.floor(Date.now() / 1000) + 3600 }
      const token = `header.${btoa(JSON.stringify(payload))}.signature`
      const mockResponse = {
        data: {
          status: 'success',
          token: token,
          user: { id: 1 }
        }
      }
      api.post.mockResolvedValue(mockResponse)

      const credentials = { password: TEST_PASSWORD }
      await authService.login(credentials)

      expect(sessionStorage.getItem('lastLoginEmail')).toBeNull()
    })
  })

  describe('logout', () => {
    it('should logout and clear all storage', () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('user', '{"id": 1}')
      localStorage.setItem('userRole', 'admin')
      localStorage.setItem('qr_farm_selected_tenant_id', '123')
      sessionStorage.setItem('lastLoginEmail', 'test@example.com')
      authService.token = 'test-token'
      authService.user = { id: 1 }
      authService.role = 'admin'

      authService.logout()

      expect(localStorage.getItem('token')).toBeNull()
      expect(localStorage.getItem('user')).toBeNull()
      expect(localStorage.getItem('userRole')).toBeNull()
      expect(localStorage.getItem('qr_farm_selected_tenant_id')).toBeNull()
      expect(sessionStorage.getItem('lastLoginEmail')).toBeNull()
      expect(authService.token).toBeNull()
      expect(authService.user).toBeNull()
      expect(authService.role).toBeNull()
      expect(console.log).toHaveBeenCalled()
    })
  })

  describe('hasPermission', () => {
    it('should return false when not authenticated', () => {
      localStorage.removeItem('token')
      authService.token = null
      expect(authService.hasPermission('admin')).toBe(false)
    })

    it('should return true for super_admin regardless of required role', () => {
      const payload = { role: 'super_admin', exp: Math.floor(Date.now() / 1000) + 3600 }
      const token = `header.${btoa(JSON.stringify(payload))}.signature`
      localStorage.setItem('token', token)
      localStorage.setItem('userRole', 'super_admin')
      authService.token = null
      authService.role = null

      expect(authService.hasPermission('admin')).toBe(true)
      expect(authService.hasPermission('user')).toBe(true)
      expect(authService.hasPermission('any')).toBe(true)
    })

    it('should return true for admin when required role is admin', () => {
      const payload = { role: 'admin', exp: Math.floor(Date.now() / 1000) + 3600 }
      const token = `header.${btoa(JSON.stringify(payload))}.signature`
      localStorage.setItem('token', token)
      localStorage.setItem('userRole', 'admin')
      authService.token = null
      authService.role = null

      expect(authService.hasPermission('admin')).toBe(true)
    })

    it('should return true for administrador when required role is admin', () => {
      const payload = { role: 'administrador', exp: Math.floor(Date.now() / 1000) + 3600 }
      const token = `header.${btoa(JSON.stringify(payload))}.signature`
      localStorage.setItem('token', token)
      localStorage.setItem('userRole', 'administrador')
      authService.token = null
      authService.role = null

      expect(authService.hasPermission('admin')).toBe(true)
    })

    it('should return true for admin when required role is user', () => {
      const payload = { role: 'admin', exp: Math.floor(Date.now() / 1000) + 3600 }
      const token = `header.${btoa(JSON.stringify(payload))}.signature`
      localStorage.setItem('token', token)
      localStorage.setItem('userRole', 'admin')
      authService.token = null
      authService.role = null

      expect(authService.hasPermission('user')).toBe(true)
    })

    it('should return true for user when required role is user', () => {
      const payload = { role: 'user', exp: Math.floor(Date.now() / 1000) + 3600 }
      const token = `header.${btoa(JSON.stringify(payload))}.signature`
      localStorage.setItem('token', token)
      localStorage.setItem('userRole', 'user')
      authService.token = null
      authService.role = null

      expect(authService.hasPermission('user')).toBe(true)
    })

    it('should return true for usuario when required role is user', () => {
      const payload = { role: 'usuario', exp: Math.floor(Date.now() / 1000) + 3600 }
      const token = `header.${btoa(JSON.stringify(payload))}.signature`
      localStorage.setItem('token', token)
      localStorage.setItem('userRole', 'usuario')
      authService.token = null
      authService.role = null

      expect(authService.hasPermission('user')).toBe(true)
    })

    it('should return false for user when required role is admin', () => {
      const payload = { role: 'user', exp: Math.floor(Date.now() / 1000) + 3600 }
      const token = `header.${btoa(JSON.stringify(payload))}.signature`
      localStorage.setItem('token', token)
      localStorage.setItem('userRole', 'user')
      authService.token = null
      authService.role = null

      expect(authService.hasPermission('admin')).toBe(false)
    })

    it('should return false for unknown role', () => {
      const payload = { role: 'unknown', exp: Math.floor(Date.now() / 1000) + 3600 }
      const token = `header.${btoa(JSON.stringify(payload))}.signature`
      localStorage.setItem('token', token)
      localStorage.setItem('userRole', 'unknown')
      authService.token = null
      authService.role = null

      expect(authService.hasPermission('admin')).toBe(false)
      expect(authService.hasPermission('user')).toBe(false)
    })
  })

  describe('getRedirectPath', () => {
    it('should return /admin/dashboard for super_admin', () => {
      localStorage.setItem('userRole', 'super_admin')
      authService.role = null
      expect(authService.getRedirectPath()).toBe('/admin/dashboard')
    })

    it('should return /admin/dashboard for admin', () => {
      localStorage.setItem('userRole', 'admin')
      authService.role = null
      expect(authService.getRedirectPath()).toBe('/admin/dashboard')
    })

    it('should return /admin/dashboard for administrador', () => {
      localStorage.setItem('userRole', 'administrador')
      authService.role = null
      expect(authService.getRedirectPath()).toBe('/admin/dashboard')
    })

    it('should return /user/inicio for user', () => {
      localStorage.setItem('userRole', 'user')
      authService.role = null
      expect(authService.getRedirectPath()).toBe('/user/inicio')
    })

    it('should return /user/inicio for usuario', () => {
      localStorage.setItem('userRole', 'usuario')
      authService.role = null
      expect(authService.getRedirectPath()).toBe('/user/inicio')
    })

    it('should return /login for unknown role', () => {
      localStorage.setItem('userRole', 'unknown')
      authService.role = null
      expect(authService.getRedirectPath()).toBe('/login')
    })

    it('should return /login when role is null', () => {
      localStorage.removeItem('userRole')
      authService.role = null
      expect(authService.getRedirectPath()).toBe('/login')
    })
  })
})
