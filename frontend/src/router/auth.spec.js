import { beforeEach, describe, it, expect, vi } from 'vitest'
import { auth, requireAuth, requireAdmin } from './auth.js'

describe('auth utilities', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.clearAllMocks()
  })

  describe('auth.isAuthenticated', () => {
    it('should return false when no token', () => {
      expect(auth.isAuthenticated()).toBe(false)
    })

    it('should return true when token exists', () => {
      localStorage.setItem('token', 'test-token')
      expect(auth.isAuthenticated()).toBe(true)
    })
  })

  describe('auth.getUserRole', () => {
    it('should return default role when no role set', () => {
      expect(auth.getUserRole()).toBe('usuario')
    })

    it('should return stored role', () => {
      localStorage.setItem('userRole', 'admin')
      expect(auth.getUserRole()).toBe('admin')
    })
  })

  describe('auth.isAdmin', () => {
    it('should return true for administrador role', () => {
      localStorage.setItem('userRole', 'administrador')
      expect(auth.isAdmin()).toBe(true)
    })

    it('should return false for other roles', () => {
      localStorage.setItem('userRole', 'usuario')
      expect(auth.isAdmin()).toBe(false)
    })
  })

  describe('auth.isUser', () => {
    it('should return true for usuario role', () => {
      localStorage.setItem('userRole', 'usuario')
      expect(auth.isUser()).toBe(true)
    })

    it('should return false for other roles', () => {
      localStorage.setItem('userRole', 'admin')
      expect(auth.isUser()).toBe(false)
    })
  })

  describe('auth.logout', () => {
    it('should clear all auth data', () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('user', '{"id": 1}')
      localStorage.setItem('userRole', 'admin')

      auth.logout()

      expect(localStorage.getItem('token')).toBeNull()
      expect(localStorage.getItem('user')).toBeNull()
      expect(localStorage.getItem('userRole')).toBeNull()
    })
  })

  describe('auth.getToken', () => {
    it('should return token when exists', () => {
      localStorage.setItem('token', 'test-token')
      expect(auth.getToken()).toBe('test-token')
    })

    it('should return null when no token', () => {
      expect(auth.getToken()).toBeNull()
    })
  })

  describe('auth.getUser', () => {
    it('should return parsed user when exists', () => {
      const userData = { id: 1, nombre: 'Test' }
      localStorage.setItem('user', JSON.stringify(userData))
      expect(auth.getUser()).toEqual(userData)
    })

    it('should return null when no user', () => {
      expect(auth.getUser()).toBeNull()
    })

    it('should handle invalid JSON gracefully', () => {
      localStorage.setItem('user', 'invalid-json')
      expect(() => auth.getUser()).toThrow()
    })
  })

  describe('requireAuth guard', () => {
    it('should redirect to login when not authenticated', () => {
      const next = vi.fn()
      requireAuth({}, {}, next)
      expect(next).toHaveBeenCalledWith('/login')
    })

    it('should allow navigation when authenticated', () => {
      localStorage.setItem('token', 'test-token')
      const next = vi.fn()
      requireAuth({}, {}, next)
      expect(next).toHaveBeenCalled()
      expect(next).not.toHaveBeenCalledWith('/login')
    })
  })

  describe('requireAdmin guard', () => {
    it('should redirect to login when not authenticated', () => {
      const next = vi.fn()
      requireAdmin({}, {}, next)
      expect(next).toHaveBeenCalledWith('/login')
    })

    it('should redirect to menu when authenticated but not admin', () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'usuario')
      const next = vi.fn()
      requireAdmin({}, {}, next)
      expect(next).toHaveBeenCalledWith('/menu')
    })

    it('should allow navigation when admin', () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'administrador')
      const next = vi.fn()
      requireAdmin({}, {}, next)
      expect(next).toHaveBeenCalled()
      expect(next).not.toHaveBeenCalledWith('/login')
      expect(next).not.toHaveBeenCalledWith('/menu')
    })
  })
})

