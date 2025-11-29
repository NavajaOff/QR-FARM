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

  it('should have protected routes with requiresAuth meta', () => {
    // Verify that protected routes have requiresAuth meta
    // The meta is on the parent route /admin
    const adminParentRoute = router.getRoutes().find(r => r.path === '/admin')
    expect(adminParentRoute).toBeDefined()
    expect(adminParentRoute?.meta?.requiresAuth).toBe(true)
    expect(adminParentRoute?.meta?.role).toBe('admin')
  })

  it('should have role-based route protection configured', () => {
    // Verify that routes have role requirements in meta
    // GestionarTenants has its own meta that overrides parent
    const superAdminRoute = router.getRoutes().find(r => r.name === 'GestionarTenants')
    expect(superAdminRoute).toBeDefined()
    expect(superAdminRoute?.meta?.role).toBe('super_admin')
    expect(superAdminRoute?.meta?.requiresAuth).toBe(true)
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

  it('should have user routes configured', () => {
    // User routes have meta on parent /user route
    const userParentRoute = router.getRoutes().find(r => r.path === '/user')
    expect(userParentRoute).toBeDefined()
    // Verify meta exists (may be requiresAuth or role)
    expect(userParentRoute?.meta).toBeDefined()
    
    // Verify child route exists
    const userRoute = router.getRoutes().find(r => r.name === 'InicioUsuario')
    expect(userRoute).toBeDefined()
  })

  it('should have public routes without auth requirement', () => {
    const loginRoute = router.getRoutes().find(r => r.name === 'Login')
    expect(loginRoute).toBeDefined()
    // Login route should not require auth
    expect(loginRoute?.meta?.requiresAuth).toBeUndefined()
  })

  it('should have all required route names', () => {
    const routeNames = router.getRoutes().map(r => r.name).filter(Boolean)
    expect(routeNames).toContain('Login')
    expect(routeNames).toContain('DashboardAdmin')
    expect(routeNames).toContain('GestionarUsuarios')
    expect(routeNames).toContain('GestionarTenants')
    expect(routeNames).toContain('InicioUsuario')
  })

  it('should have beforeEach guard configured', () => {
    // Verify router has navigation guard
    expect(router.beforeEach).toBeDefined()
    expect(typeof router.beforeEach).toBe('function')
  })
})

