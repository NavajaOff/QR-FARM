import { beforeEach, describe, it, expect, vi } from 'vitest'
import { createRouter, createMemoryHistory } from 'vue-router'
import router from './index.js'

describe('Router Configuration', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.clearAllMocks()
  })

  it('should export a router instance', () => {
    expect(router).toBeDefined()
    expect(router).toHaveProperty('beforeEach')
  })

  it('should have routes defined', () => {
    expect(router.getRoutes().length).toBeGreaterThan(0)
  })

  it('should redirect root path to login', async () => {
    localStorage.clear()
    const testRouter = createRouter({
      history: createMemoryHistory(),
      routes: router.getRoutes()
    })

    await testRouter.push('/')
    await testRouter.isReady()

    expect(testRouter.currentRoute.value.path).toBe('/login')
  })

  it('should have login route', async () => {
    const testRouter = createRouter({
      history: createMemoryHistory(),
      routes: router.getRoutes()
    })

    await testRouter.push('/login')
    await testRouter.isReady()

    expect(testRouter.currentRoute.value.name).toBe('Login')
  })

  it('should have admin dashboard route', async () => {
    localStorage.setItem('token', 'test-token')
    localStorage.setItem('userRole', 'admin')

    const testRouter = createRouter({
      history: createMemoryHistory(),
      routes: router.getRoutes()
    })

    await testRouter.push('/admin/dashboard')
    await testRouter.isReady()

    expect(testRouter.currentRoute.value.name).toBe('DashboardAdmin')
  })

  it('should redirect to login when accessing protected route without token', async () => {
    localStorage.clear()

    const testRouter = createRouter({
      history: createMemoryHistory(),
      routes: router.getRoutes()
    })

    await testRouter.push('/admin/dashboard')
    await testRouter.isReady()

    expect(testRouter.currentRoute.value.path).toBe('/login')
  })

  it('should redirect to login when accessing super_admin route as admin', async () => {
    localStorage.setItem('token', 'test-token')
    localStorage.setItem('userRole', 'admin')

    const testRouter = createRouter({
      history: createMemoryHistory(),
      routes: router.getRoutes()
    })

    await testRouter.push('/admin/gestionar-tenants')
    await testRouter.isReady()

    expect(testRouter.currentRoute.value.path).toBe('/login')
  })

  it('should allow super_admin to access super_admin routes', async () => {
    localStorage.setItem('token', 'test-token')
    localStorage.setItem('userRole', 'super_admin')

    const testRouter = createRouter({
      history: createMemoryHistory(),
      routes: router.getRoutes()
    })

    await testRouter.push('/admin/gestionar-tenants')
    await testRouter.isReady()

    expect(testRouter.currentRoute.value.name).toBe('GestionarTenants')
  })

  it('should redirect authenticated user from login to dashboard', async () => {
    localStorage.setItem('token', 'test-token')
    localStorage.setItem('userRole', 'admin')

    const testRouter = createRouter({
      history: createMemoryHistory(),
      routes: router.getRoutes()
    })

    await testRouter.push('/login')
    await testRouter.isReady()

    expect(testRouter.currentRoute.value.path).toBe('/admin/dashboard')
  })

  it('should redirect authenticated user from root to dashboard', async () => {
    localStorage.setItem('token', 'test-token')
    localStorage.setItem('userRole', 'admin')

    const testRouter = createRouter({
      history: createMemoryHistory(),
      routes: router.getRoutes()
    })

    await testRouter.push('/')
    await testRouter.isReady()

    expect(testRouter.currentRoute.value.path).toBe('/admin/dashboard')
  })

  it('should redirect user role to user dashboard', async () => {
    localStorage.setItem('token', 'test-token')
    localStorage.setItem('userRole', 'usuario')

    const testRouter = createRouter({
      history: createMemoryHistory(),
      routes: router.getRoutes()
    })

    await testRouter.push('/')
    await testRouter.isReady()

    expect(testRouter.currentRoute.value.path).toBe('/user/inicio')
  })

  it('should allow user to access user routes', async () => {
    localStorage.setItem('token', 'test-token')
    localStorage.setItem('userRole', 'usuario')

    const testRouter = createRouter({
      history: createMemoryHistory(),
      routes: router.getRoutes()
    })

    await testRouter.push('/user/inicio')
    await testRouter.isReady()

    expect(testRouter.currentRoute.value.name).toBe('InicioUsuario')
  })

  it('should have admin routes with admin role requirement', () => {
    // Verify that admin routes have the correct meta configuration
    const adminRoute = router.getRoutes().find(r => r.name === 'DashboardAdmin')
    expect(adminRoute).toBeDefined()
    expect(adminRoute?.meta?.role).toBe('admin')
  })

  it('should have super_admin routes with super_admin role requirement', () => {
    // Verify that super_admin routes have the correct meta configuration
    const superAdminRoute = router.getRoutes().find(r => r.name === 'GestionarTenants')
    expect(superAdminRoute).toBeDefined()
    expect(superAdminRoute?.meta?.role).toBe('super_admin')
  })

  it('should handle administrador role as admin', async () => {
    localStorage.setItem('token', 'test-token')
    localStorage.setItem('userRole', 'administrador')

    const testRouter = createRouter({
      history: createMemoryHistory(),
      routes: router.getRoutes()
    })

    await testRouter.push('/admin/dashboard')
    await testRouter.isReady()

    expect(testRouter.currentRoute.value.name).toBe('DashboardAdmin')
  })

  it('should handle user role alias', async () => {
    localStorage.setItem('token', 'test-token')
    localStorage.setItem('userRole', 'user')

    const testRouter = createRouter({
      history: createMemoryHistory(),
      routes: router.getRoutes()
    })

    await testRouter.push('/user/inicio')
    await testRouter.isReady()

    expect(testRouter.currentRoute.value.name).toBe('InicioUsuario')
  })
})

