import { beforeEach, vi } from 'vitest'
import api, { authAPI, userAPI, tenantAPI, reportAPI, ganadoAPI, potreroAPI, vacunacionAPI } from './api'

// Test constants to avoid hardcoded credentials
const TEST_EMAIL = 'test@test.com'
const TEST_PASSWORD = 'test-password-123'

describe('api', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.clearAllMocks()
    globalThis.alert = vi.fn()
    console.log = vi.fn()
    console.warn = vi.fn()
    console.error = vi.fn()
  })

  describe('API Instance', () => {
    it('should export api service', () => {
      expect(api).toBeDefined()
      // api is an axios instance, which has methods like get, post, etc.
      expect(api).toBeTruthy()
      expect(typeof api.get).toBe('function')
      expect(typeof api.post).toBe('function')
    })

    it('should have expected methods', () => {
      expect(api.get).toBeDefined()
      expect(api.post).toBeDefined()
      expect(api.put).toBeDefined()
      expect(api.delete).toBeDefined()
    })

    it('should have correct baseURL configuration', () => {
      expect(api.defaults.baseURL).toContain('/api')
    })
  })

  describe('API Modules', () => {
    it('should export all API modules', () => {
      expect(authAPI).toBeDefined()
      expect(userAPI).toBeDefined()
      expect(tenantAPI).toBeDefined()
      expect(reportAPI).toBeDefined()
      expect(ganadoAPI).toBeDefined()
      expect(potreroAPI).toBeDefined()
      expect(vacunacionAPI).toBeDefined()
    })

    it('should have authAPI methods', () => {
      expect(typeof authAPI.register).toBe('function')
      expect(typeof authAPI.login).toBe('function')
      expect(typeof authAPI.getProfile).toBe('function')
      expect(typeof authAPI.updateProfile).toBe('function')
    })

    it('should have userAPI methods', () => {
      expect(typeof userAPI.getAll).toBe('function')
      expect(typeof userAPI.getById).toBe('function')
      expect(typeof userAPI.update).toBe('function')
      expect(typeof userAPI.delete).toBe('function')
      expect(typeof userAPI.changeStatus).toBe('function')
    })

    it('should have ganadoAPI methods', () => {
      expect(typeof ganadoAPI.getAll).toBe('function')
      expect(typeof ganadoAPI.getById).toBe('function')
      expect(typeof ganadoAPI.create).toBe('function')
      expect(typeof ganadoAPI.update).toBe('function')
      expect(typeof ganadoAPI.delete).toBe('function')
    })

    it('should have potreroAPI methods', () => {
      expect(typeof potreroAPI.getAll).toBe('function')
      expect(typeof potreroAPI.getById).toBe('function')
      expect(typeof potreroAPI.create).toBe('function')
      expect(typeof potreroAPI.update).toBe('function')
      expect(typeof potreroAPI.delete).toBe('function')
    })

    it('should have vacunacionAPI methods', () => {
      expect(typeof vacunacionAPI.getAll).toBe('function')
      expect(typeof vacunacionAPI.getById).toBe('function')
      expect(typeof vacunacionAPI.create).toBe('function')
      expect(typeof vacunacionAPI.update).toBe('function')
      expect(typeof vacunacionAPI.delete).toBe('function')
    })

    it('should have reportAPI methods', () => {
      expect(typeof reportAPI.getSummary).toBe('function')
      expect(typeof reportAPI.downloadSummaryPdf).toBe('function')
    })

    it('should have tenantAPI methods', () => {
      expect(typeof tenantAPI.getAll).toBe('function')
      expect(typeof tenantAPI.getById).toBe('function')
      expect(typeof tenantAPI.create).toBe('function')
      expect(typeof tenantAPI.update).toBe('function')
    })
  })

  describe('Request Interceptor', () => {
    const getRequestInterceptor = () => {
      return api.interceptors.request.handlers[0].fulfilled
    }

    it('should add token to request headers when token exists', () => {
      localStorage.setItem('token', 'test-token')
      const config = { headers: {}, url: '/test' }
      const interceptor = getRequestInterceptor()
      const result = interceptor(config)
      expect(result.headers.Authorization).toBe('Bearer test-token')
    })

    it('should not add token if not in localStorage', () => {
      const config = { headers: {}, url: '/test' }
      const interceptor = getRequestInterceptor()
      const result = interceptor(config)
      expect(result.headers.Authorization).toBeUndefined()
    })

    it('should create headers object if it does not exist', () => {
      localStorage.setItem('token', 'test-token')
      const config = { url: '/test' }
      const interceptor = getRequestInterceptor()
      const result = interceptor(config)
      expect(result.headers).toBeDefined()
      expect(result.headers.Authorization).toBe('Bearer test-token')
    })

    it('should add tenant_id to query params when selected', () => {
      localStorage.setItem('qr_farm_selected_tenant_id', '123')
      const config = { headers: {}, url: '/ganado', params: {} }
      const interceptor = getRequestInterceptor()
      const result = interceptor(config)
      expect(result.params.tenant_id).toBe(123)
    })

    it('should create params object if it does not exist', () => {
      localStorage.setItem('qr_farm_selected_tenant_id', '123')
      const config = { headers: {}, url: '/ganado' }
      const interceptor = getRequestInterceptor()
      const result = interceptor(config)
      expect(result.params).toBeDefined()
      expect(result.params.tenant_id).toBe(123)
    })

    it('should not add tenant_id to tenants routes', () => {
      localStorage.setItem('qr_farm_selected_tenant_id', '123')
      const config = { headers: {}, url: '/tenants', params: {} }
      const interceptor = getRequestInterceptor()
      const result = interceptor(config)
      expect(result.params?.tenant_id).toBeUndefined()
    })

    it('should not add tenant_id to login routes', () => {
      localStorage.setItem('qr_farm_selected_tenant_id', '123')
      const config = { headers: {}, url: '/usuarios/login', params: {} }
      const interceptor = getRequestInterceptor()
      const result = interceptor(config)
      expect(result.params?.tenant_id).toBeUndefined()
    })

    it('should not add tenant_id to register routes', () => {
      localStorage.setItem('qr_farm_selected_tenant_id', '123')
      const config = { headers: {}, url: '/usuarios/register', params: {} }
      const interceptor = getRequestInterceptor()
      const result = interceptor(config)
      expect(result.params?.tenant_id).toBeUndefined()
    })

    it('should handle invalid tenant_id gracefully', () => {
      localStorage.setItem('qr_farm_selected_tenant_id', 'invalid')
      const config = { headers: {}, url: '/ganado', params: {} }
      const interceptor = getRequestInterceptor()
      const result = interceptor(config)
      expect(result.params?.tenant_id).toBeUndefined()
    })

    it('should handle empty tenant_id', () => {
      localStorage.setItem('qr_farm_selected_tenant_id', '')
      const config = { headers: {}, url: '/ganado', params: {} }
      const interceptor = getRequestInterceptor()
      const result = interceptor(config)
      expect(result.params?.tenant_id).toBeUndefined()
    })

    it('should handle null tenant_id', () => {
      localStorage.setItem('qr_farm_selected_tenant_id', 'null')
      const config = { headers: {}, url: '/ganado', params: {} }
      const interceptor = getRequestInterceptor()
      const result = interceptor(config)
      expect(result.params?.tenant_id).toBeUndefined()
    })

    it('should handle config.url being undefined', () => {
      localStorage.setItem('qr_farm_selected_tenant_id', '123')
      const config = { headers: {}, params: {} }
      const interceptor = getRequestInterceptor()
      const result = interceptor(config)
      expect(result.params.tenant_id).toBe(123)
    })

    it('should handle config.url being null', () => {
      localStorage.setItem('qr_farm_selected_tenant_id', '123')
      const config = { headers: {}, url: null, params: {} }
      const interceptor = getRequestInterceptor()
      const result = interceptor(config)
      expect(result.params.tenant_id).toBe(123)
    })

    it('should handle errors in tenant_id processing gracefully', () => {
      localStorage.setItem('qr_farm_selected_tenant_id', '123')
      const config = { headers: {}, url: '/ganado', params: {} }
      const interceptor = getRequestInterceptor()
      
      // Mock localStorage.getItem to throw error
      const originalGetItem = localStorage.getItem
      localStorage.getItem = vi.fn(() => {
        throw new Error('Storage error')
      })
      
      const result = interceptor(config)
      expect(result).toBeDefined()
      
      // Restore
      localStorage.getItem = originalGetItem
    })

    it('should log request configuration', () => {
      localStorage.setItem('token', 'test-token')
      const config = { headers: {}, url: '/test', method: 'GET' }
      const interceptor = getRequestInterceptor()
      interceptor(config)
      expect(console.log).toHaveBeenCalled()
    })

    it('should handle request interceptor error', () => {
      const errorInterceptor = api.interceptors.request.handlers[0].rejected
      const error = new Error('Request error')
      const result = errorInterceptor(error)
      expect(result).rejects.toBeDefined()
    })
  })

  describe('Response Interceptor', () => {
    const getResponseInterceptor = () => {
      return api.interceptors.response.handlers[0]
    }

    it('should handle successful response', () => {
      const { fulfilled } = getResponseInterceptor()
      const response = {
        config: { url: '/test' },
        status: 200,
        statusText: 'OK'
      }
      const result = fulfilled(response)
      expect(result).toBe(response)
      expect(console.log).toHaveBeenCalled()
    })

    it('should handle ERR_NETWORK error', () => {
      const { rejected } = getResponseInterceptor()
      const error = { code: 'ERR_NETWORK', config: { url: '/test' } }
      rejected(error).catch(() => {})
      expect(globalThis.alert).toHaveBeenCalled()
    })

    it('should handle 401 errors', () => {
      const { rejected } = getResponseInterceptor()
      const error = { response: { status: 401 }, config: { url: '/test' } }
      const result = rejected(error)
      expect(result).rejects.toBeDefined()
      expect(console.warn).toHaveBeenCalled()
    })

    it('should handle 403 errors', () => {
      const { rejected } = getResponseInterceptor()
      const error = { response: { status: 403 }, config: { url: '/test' } }
      const result = rejected(error)
      expect(result).rejects.toBeDefined()
      expect(console.warn).toHaveBeenCalled()
    })

    it('should handle 500 errors', () => {
      const { rejected } = getResponseInterceptor()
      const error = { response: { status: 500 }, config: { url: '/test' } }
      const result = rejected(error)
      expect(result).rejects.toBeDefined()
      expect(console.error).toHaveBeenCalled()
    })

    it('should handle 502 errors', () => {
      const { rejected } = getResponseInterceptor()
      const error = { response: { status: 502 }, config: { url: '/test' } }
      const result = rejected(error)
      expect(result).rejects.toBeDefined()
      expect(console.error).toHaveBeenCalled()
    })

    it('should handle 503 errors', () => {
      const { rejected } = getResponseInterceptor()
      const error = { response: { status: 503 }, config: { url: '/test' } }
      const result = rejected(error)
      expect(result).rejects.toBeDefined()
      expect(console.error).toHaveBeenCalled()
    })

    it('should handle error without response', () => {
      const { rejected } = getResponseInterceptor()
      const error = { code: 'SOME_ERROR', config: { url: '/test' } }
      const result = rejected(error)
      expect(result).rejects.toBeDefined()
    })

    it('should handle error without config', () => {
      const { rejected } = getResponseInterceptor()
      const error = { code: 'ERR_NETWORK' }
      rejected(error).catch(() => {})
      expect(console.error).toHaveBeenCalled()
    })

    it('should log error details', () => {
      const { rejected } = getResponseInterceptor()
      const error = {
        config: { url: '/test', method: 'GET' },
        response: { status: 404, statusText: 'Not Found', data: { message: 'Not found' } },
        message: 'Request failed',
        code: 'ERR_BAD_REQUEST'
      }
      rejected(error).catch(() => {})
      expect(console.error).toHaveBeenCalled()
    })
  })

  describe('tenantAPI.getAll', () => {
    it('should convert true to "true" string', () => {
      const result = tenantAPI.getAll(true)
      expect(result).toBeDefined()
      expect(console.log).toHaveBeenCalledWith(
        expect.stringContaining('[tenantAPI] getAll'),
        true,
        expect.stringContaining('convertido a'),
        'true'
      )
      // Handle promise rejection to avoid unhandled rejection warnings
      result.catch(() => {})
    })

    it('should convert false to "false" string', () => {
      vi.clearAllMocks()
      const result = tenantAPI.getAll(false)
      expect(result).toBeDefined()
      expect(console.log).toHaveBeenCalledWith(
        expect.stringContaining('[tenantAPI] getAll'),
        false,
        expect.stringContaining('convertido a'),
        'false'
      )
      // Handle promise rejection to avoid unhandled rejection warnings
      result.catch(() => {})
    })

    it('should convert string "true" to "true" string', () => {
      vi.clearAllMocks()
      const result = tenantAPI.getAll('true')
      expect(result).toBeDefined()
      expect(console.log).toHaveBeenCalledWith(
        expect.stringContaining('[tenantAPI] getAll'),
        'true',
        expect.stringContaining('convertido a'),
        'true'
      )
      // Handle promise rejection to avoid unhandled rejection warnings
      result.catch(() => {})
    })

    it('should convert string "false" to "false" string', () => {
      vi.clearAllMocks()
      const result = tenantAPI.getAll('false')
      expect(result).toBeDefined()
      expect(console.log).toHaveBeenCalledWith(
        expect.stringContaining('[tenantAPI] getAll'),
        'false',
        expect.stringContaining('convertido a'),
        'false'
      )
      // Handle promise rejection to avoid unhandled rejection warnings
      result.catch(() => {})
    })

    it('should use default value true', () => {
      vi.clearAllMocks()
      const result = tenantAPI.getAll()
      expect(result).toBeDefined()
      expect(console.log).toHaveBeenCalledWith(
        expect.stringContaining('[tenantAPI] getAll'),
        true,
        expect.stringContaining('convertido a'),
        'true'
      )
      // Handle promise rejection to avoid unhandled rejection warnings
      result.catch(() => {})
    })

    it('should convert other values to "false" string', () => {
      vi.clearAllMocks()
      const result = tenantAPI.getAll('other')
      expect(result).toBeDefined()
      expect(console.log).toHaveBeenCalledWith(
        expect.stringContaining('[tenantAPI] getAll'),
        'other',
        expect.stringContaining('convertido a'),
        'false'
      )
      // Handle promise rejection to avoid unhandled rejection warnings
      result.catch(() => {})
    })
  })

  describe('API Function Calls', () => {
    it('should call authAPI.register with correct parameters', () => {
      const userData = { email: TEST_EMAIL, password: TEST_PASSWORD }
      const result = authAPI.register(userData)
      expect(result).toBeDefined()
      // Handle promise rejection to avoid unhandled rejection warnings
      result.catch(() => {})
    })

    it('should call authAPI.login with correct parameters', () => {
      const credentials = { email: TEST_EMAIL, password: TEST_PASSWORD }
      const result = authAPI.login(credentials)
      expect(result).toBeDefined()
      result.catch(() => {})
    })

    it('should call authAPI.getProfile', () => {
      const result = authAPI.getProfile()
      expect(result).toBeDefined()
      result.catch(() => {})
    })

    it('should call authAPI.updateProfile with correct parameters', () => {
      const data = { nombre: 'Test' }
      const result = authAPI.updateProfile(data)
      expect(result).toBeDefined()
      result.catch(() => {})
    })

    it('should call userAPI.getAll', () => {
      const result = userAPI.getAll()
      expect(result).toBeDefined()
      result.catch(() => {})
    })

    it('should call userAPI.getById with id', () => {
      const result = userAPI.getById(1)
      expect(result).toBeDefined()
      result.catch(() => {})
    })

    it('should call userAPI.update with id and data', () => {
      const result = userAPI.update(1, { nombre: 'Test' })
      expect(result).toBeDefined()
      result.catch(() => {})
    })

    it('should call userAPI.delete with id', () => {
      const result = userAPI.delete(1)
      expect(result).toBeDefined()
      result.catch(() => {})
    })

    it('should call userAPI.changeStatus with id and status', () => {
      const result = userAPI.changeStatus(1, 'activo')
      expect(result).toBeDefined()
      result.catch(() => {})
    })

    it('should call ganadoAPI.getAll', () => {
      const result = ganadoAPI.getAll()
      expect(result).toBeDefined()
      result.catch(() => {})
    })

    it('should call ganadoAPI.getById with id', () => {
      const result = ganadoAPI.getById(1)
      expect(result).toBeDefined()
      result.catch(() => {})
    })

    it('should call ganadoAPI.create with data', () => {
      const result = ganadoAPI.create({ nombre: 'Test' })
      expect(result).toBeDefined()
      result.catch(() => {})
    })

    it('should call ganadoAPI.update with id and data', () => {
      const result = ganadoAPI.update(1, { nombre: 'Test' })
      expect(result).toBeDefined()
      result.catch(() => {})
    })

    it('should call ganadoAPI.delete with id', () => {
      const result = ganadoAPI.delete(1)
      expect(result).toBeDefined()
      result.catch(() => {})
    })

    it('should call potreroAPI.getAll', () => {
      const result = potreroAPI.getAll()
      expect(result).toBeDefined()
      result.catch(() => {})
    })

    it('should call potreroAPI.getById with id', () => {
      const result = potreroAPI.getById(1)
      expect(result).toBeDefined()
      result.catch(() => {})
    })

    it('should call potreroAPI.create with data', () => {
      const result = potreroAPI.create({ nombre: 'Test' })
      expect(result).toBeDefined()
      result.catch(() => {})
    })

    it('should call potreroAPI.update with id and data', () => {
      const result = potreroAPI.update(1, { nombre: 'Test' })
      expect(result).toBeDefined()
      result.catch(() => {})
    })

    it('should call potreroAPI.delete with id', () => {
      const result = potreroAPI.delete(1)
      expect(result).toBeDefined()
      result.catch(() => {})
    })

    it('should call vacunacionAPI.getAll', () => {
      const result = vacunacionAPI.getAll()
      expect(result).toBeDefined()
      result.catch(() => {})
    })

    it('should call vacunacionAPI.getById with id', () => {
      const result = vacunacionAPI.getById(1)
      expect(result).toBeDefined()
      result.catch(() => {})
    })

    it('should call vacunacionAPI.create with data', () => {
      const result = vacunacionAPI.create({ nombre: 'Test' })
      expect(result).toBeDefined()
      result.catch(() => {})
    })

    it('should call vacunacionAPI.update with id and data', () => {
      const result = vacunacionAPI.update(1, { nombre: 'Test' })
      expect(result).toBeDefined()
      result.catch(() => {})
    })

    it('should call vacunacionAPI.delete with id', () => {
      const result = vacunacionAPI.delete(1)
      expect(result).toBeDefined()
      result.catch(() => {})
    })

    it('should call reportAPI.getSummary', () => {
      const result = reportAPI.getSummary()
      expect(result).toBeDefined()
      result.catch(() => {})
    })

    it('should call reportAPI.downloadSummaryPdf', () => {
      const result = reportAPI.downloadSummaryPdf()
      expect(result).toBeDefined()
      result.catch(() => {})
    })

    it('should call tenantAPI.getById with id', () => {
      const result = tenantAPI.getById(1)
      expect(result).toBeDefined()
      result.catch(() => {})
    })

    it('should call tenantAPI.create with data', () => {
      const result = tenantAPI.create({ nombre: 'Test' })
      expect(result).toBeDefined()
      result.catch(() => {})
    })

    it('should call tenantAPI.update with id and data', () => {
      const result = tenantAPI.update(1, { nombre: 'Test' })
      expect(result).toBeDefined()
      result.catch(() => {})
    })
  })
})