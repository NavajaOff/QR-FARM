import api, { authAPI, userAPI, tenantAPI, reportAPI, ganadoAPI, potreroAPI, vacunacionAPI } from './api'

describe('api', () => {
  beforeEach(() => {
    localStorage.clear()
    jest.clearAllMocks()
  })

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
    expect(tenantAPI).toBeDefined()
    expect(reportAPI).toBeDefined()
    expect(ganadoAPI).toBeDefined()
    expect(potreroAPI).toBeDefined()
    expect(vacunacionAPI).toBeDefined()
    expect(typeof authAPI.login).toBe('function')
    expect(typeof userAPI.getAll).toBe('function')
  })

  it('should add token to request headers', () => {
    localStorage.setItem('token', 'test-token')
    const config = { headers: {}, url: '/test' }
    const interceptor = api.interceptors.request.handlers[0].fulfilled
    const result = interceptor(config)
    expect(result.headers.Authorization).toBe('Bearer test-token')
  })

  it('should not add token if not in localStorage', () => {
    const config = { headers: {}, url: '/test' }
    const interceptor = api.interceptors.request.handlers[0].fulfilled
    const result = interceptor(config)
    expect(result.headers.Authorization).toBeUndefined()
  })

  it('should add tenant_id to query params when selected', () => {
    localStorage.setItem('qr_farm_selected_tenant_id', '123')
    const config = { headers: {}, url: '/ganado', params: {} }
    const interceptor = api.interceptors.request.handlers[0].fulfilled
    const result = interceptor(config)
    expect(result.params.tenant_id).toBe(123)
  })

  it('should not add tenant_id to tenants routes', () => {
    localStorage.setItem('qr_farm_selected_tenant_id', '123')
    const config = { headers: {}, url: '/tenants', params: {} }
    const interceptor = api.interceptors.request.handlers[0].fulfilled
    const result = interceptor(config)
    expect(result.params?.tenant_id).toBeUndefined()
  })

  it('should not add tenant_id to login routes', () => {
    localStorage.setItem('qr_farm_selected_tenant_id', '123')
    const config = { headers: {}, url: '/usuarios/login', params: {} }
    const interceptor = api.interceptors.request.handlers[0].fulfilled
    const result = interceptor(config)
    expect(result.params?.tenant_id).toBeUndefined()
  })

  it('should handle invalid tenant_id gracefully', () => {
    localStorage.setItem('qr_farm_selected_tenant_id', 'invalid')
    const config = { headers: {}, url: '/ganado', params: {} }
    const interceptor = api.interceptors.request.handlers[0].fulfilled
    const result = interceptor(config)
    expect(result.params?.tenant_id).toBeUndefined()
  })

  it('should handle network errors', () => {
    const error = { code: 'ERR_NETWORK', config: { url: '/test' } }
    const interceptor = api.interceptors.response.handlers[0].rejected
    globalThis.alert = jest.fn()
    interceptor(error)
    expect(globalThis.alert).toHaveBeenCalled()
  })

  it('should handle 401 errors', () => {
    const error = { response: { status: 401 }, config: { url: '/test' } }
    const interceptor = api.interceptors.response.handlers[0].rejected
    const result = interceptor(error)
    expect(result).rejects.toBeDefined()
  })

  it('should handle 403 errors', () => {
    const error = { response: { status: 403 }, config: { url: '/test' } }
    const interceptor = api.interceptors.response.handlers[0].rejected
    const result = interceptor(error)
    expect(result).rejects.toBeDefined()
  })

  it('should handle 500 errors', () => {
    const error = { response: { status: 500 }, config: { url: '/test' } }
    const interceptor = api.interceptors.response.handlers[0].rejected
    const result = interceptor(error)
    expect(result).rejects.toBeDefined()
  })
})