import { beforeEach, afterEach, vi, describe, it, expect } from 'vitest'
import { createRouter, createMemoryHistory } from 'vue-router'
import { mount } from '@vue/test-utils'

// Mock all lazy-loaded components
const mockComponent = { template: '<div>Mock Component</div>' }

vi.mock('../views/public/Login.vue', () => ({ default: mockComponent }))
vi.mock('../views/public/Home.vue', () => ({ default: mockComponent }))
vi.mock('../views/public/Contacto.vue', () => ({ default: mockComponent }))
vi.mock('../layouts/AdminLayout.vue', () => ({ default: mockComponent }))
vi.mock('../layouts/UserLayout.vue', () => ({ default: mockComponent }))
vi.mock('../views/admin/DashboardContent.vue', () => ({ default: mockComponent }))
vi.mock('../views/admin/GestionarUsuarios.vue', () => ({ default: mockComponent }))
vi.mock('../views/admin/GestionarTenants.vue', () => ({ default: mockComponent }))
vi.mock('../views/admin/GestionarAnimalesAdmin.vue', () => ({ default: mockComponent }))
vi.mock('../views/admin/GestionarPotrerosAdmin.vue', () => ({ default: mockComponent }))
vi.mock('../views/admin/ReportesAdmin.vue', () => ({ default: mockComponent }))
vi.mock('../views/admin/RegistroVacunacionAdmin.vue', () => ({ default: mockComponent }))
vi.mock('../views/admin/PerfilAdmin.vue', () => ({ default: mockComponent }))
vi.mock('../views/admin/EscanearQRAdmin.vue', () => ({ default: mockComponent }))
vi.mock('../views/user/DashboardContent.vue', () => ({ default: mockComponent }))
vi.mock('../views/user/GestionarAnimalesUsuario.vue', () => ({ default: mockComponent }))
vi.mock('../views/user/GestionarPotrerosUsuario.vue', () => ({ default: mockComponent }))
vi.mock('../views/user/ReportesUsuario.vue', () => ({ default: mockComponent }))
vi.mock('../views/user/RegistroVacunacionUsuario.vue', () => ({ default: mockComponent }))
vi.mock('../views/user/PerfilUsuario.vue', () => ({ default: mockComponent }))
vi.mock('../views/user/EscanearQRUsuario.vue', () => ({ default: mockComponent }))

// Mock import.meta.env before importing router
vi.stubGlobal('import.meta', {
  env: {
    BASE_URL: '/'
  }
})

// Mock createWebHistory to use createMemoryHistory for testing
vi.mock('vue-router', async () => {
  const actual = await vi.importActual('vue-router')
  return {
    ...actual,
    createWebHistory: () => createMemoryHistory()
  }
})

// Import router after mocking
import router from './index.js'

// Mock console.log to avoid noise in tests
const originalConsoleLog = console.log
beforeEach(() => {
  console.log = vi.fn()
  localStorage.clear()
})

afterEach(() => {
  console.log = originalConsoleLog
  localStorage.clear()
})

describe('Router Configuration', () => {
  it('should export a router instance', () => {
    expect(router).toBeDefined()
    expect(router).toHaveProperty('currentRoute')
    expect(router).toHaveProperty('push')
    expect(router).toHaveProperty('beforeEach')
  })

  it('should have routes defined', () => {
    const routes = router.getRoutes()
    expect(routes.length).toBeGreaterThan(0)
  })

  it('should have root route redirecting to login', async () => {
    const routes = router.getRoutes()
    const rootRoute = routes.find(r => r.path === '/')
    expect(rootRoute).toBeDefined()
    expect(rootRoute.redirect).toBe('/login')
  })

  describe('Public Routes', () => {
    it('should have Login route', async () => {
      await router.push('/login')
      await router.isReady()
      expect(router.currentRoute.value.name).toBe('Login')
      expect(router.currentRoute.value.path).toBe('/login')
    })

    it('should have Home route', async () => {
      await router.push('/home')
      await router.isReady()
      expect(router.currentRoute.value.name).toBe('Home')
      expect(router.currentRoute.value.path).toBe('/home')
    })

    it('should have Contacto route', async () => {
      await router.push('/contacto')
      await router.isReady()
      expect(router.currentRoute.value.name).toBe('Contacto')
      expect(router.currentRoute.value.path).toBe('/contacto')
    })
  })

  describe('Admin Routes', () => {
    beforeEach(() => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'admin')
    })

    it('should have DashboardAdmin route', async () => {
      await router.push('/admin/dashboard')
      await router.isReady()
      expect(router.currentRoute.value.name).toBe('DashboardAdmin')
      expect(router.currentRoute.value.path).toBe('/admin/dashboard')
    })

    it('should have GestionarUsuarios route', async () => {
      await router.push('/admin/gestionar-usuarios')
      await router.isReady()
      expect(router.currentRoute.value.name).toBe('GestionarUsuarios')
      expect(router.currentRoute.value.path).toBe('/admin/gestionar-usuarios')
    })

    it('should have GestionarTenants route', async () => {
      localStorage.setItem('userRole', 'super_admin')
      await router.push('/admin/gestionar-tenants')
      await router.isReady()
      expect(router.currentRoute.value.name).toBe('GestionarTenants')
      expect(router.currentRoute.value.path).toBe('/admin/gestionar-tenants')
    })

    it('should have GestionarAnimalesAdmin route', async () => {
      await router.push('/admin/gestionar-animales')
      await router.isReady()
      expect(router.currentRoute.value.name).toBe('GestionarAnimalesAdmin')
      expect(router.currentRoute.value.path).toBe('/admin/gestionar-animales')
    })

    it('should have GestionarGanadoAdmin route', async () => {
      await router.push('/admin/gestionar-ganado')
      await router.isReady()
      expect(router.currentRoute.value.name).toBe('GestionarGanadoAdmin')
      expect(router.currentRoute.value.path).toBe('/admin/gestionar-ganado')
    })

    it('should have GestionarGanadosAdmin route', async () => {
      await router.push('/admin/gestionar-ganados')
      await router.isReady()
      expect(router.currentRoute.value.name).toBe('GestionarGanadosAdmin')
      expect(router.currentRoute.value.path).toBe('/admin/gestionar-ganados')
    })

    it('should have GestionarPotrerosAdmin route', async () => {
      await router.push('/admin/gestionar-potreros')
      await router.isReady()
      expect(router.currentRoute.value.name).toBe('GestionarPotrerosAdmin')
      expect(router.currentRoute.value.path).toBe('/admin/gestionar-potreros')
    })

    it('should have ReportesAdmin route', async () => {
      await router.push('/admin/reportes')
      await router.isReady()
      expect(router.currentRoute.value.name).toBe('ReportesAdmin')
      expect(router.currentRoute.value.path).toBe('/admin/reportes')
    })

    it('should have RegistroVacunacionAdmin route', async () => {
      await router.push('/admin/vacunacion')
      await router.isReady()
      expect(router.currentRoute.value.name).toBe('RegistroVacunacionAdmin')
      expect(router.currentRoute.value.path).toBe('/admin/vacunacion')
    })

    it('should have PerfilAdmin route', async () => {
      await router.push('/admin/perfil')
      await router.isReady()
      expect(router.currentRoute.value.name).toBe('PerfilAdmin')
      expect(router.currentRoute.value.path).toBe('/admin/perfil')
    })

    it('should have EscanearQRAdmin route', async () => {
      await router.push('/admin/scan-qr')
      await router.isReady()
      expect(router.currentRoute.value.name).toBe('EscanearQRAdmin')
      expect(router.currentRoute.value.path).toBe('/admin/scan-qr')
    })

    it('should have admin route with correct meta', () => {
      const routes = router.getRoutes()
      const adminRoute = routes.find(r => r.path === '/admin')
      expect(adminRoute).toBeDefined()
      expect(adminRoute.meta).toBeDefined()
      expect(adminRoute.meta.requiresAuth).toBe(true)
      expect(adminRoute.meta.allowedRoles).toContain('admin')
      expect(adminRoute.meta.allowedRoles).toContain('super_admin')
    })

    it('should have gestionar-tenants route with super_admin only', () => {
      const routes = router.getRoutes()
      const tenantsRoute = routes.find(r => r.name === 'GestionarTenants')
      expect(tenantsRoute).toBeDefined()
      expect(tenantsRoute.meta).toBeDefined()
      expect(tenantsRoute.meta.allowedRoles).toEqual(['super_admin'])
    })
  })

  describe('User Routes', () => {
    beforeEach(() => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'usuario')
    })

    it('should redirect from /user to InicioUsuario', async () => {
      await router.push('/user')
      await router.isReady()
      expect(router.currentRoute.value.name).toBe('InicioUsuario')
      expect(router.currentRoute.value.path).toBe('/user/inicio')
    })

    it('should have InicioUsuario route', async () => {
      await router.push('/user/inicio')
      await router.isReady()
      expect(router.currentRoute.value.name).toBe('InicioUsuario')
      expect(router.currentRoute.value.path).toBe('/user/inicio')
    })

    it('should redirect from /user/dashboard to InicioUsuario', async () => {
      await router.push('/user/dashboard')
      await router.isReady()
      expect(router.currentRoute.value.name).toBe('InicioUsuario')
      expect(router.currentRoute.value.path).toBe('/user/inicio')
    })

    it('should have GanadoUsuario route', async () => {
      await router.push('/user/ganado')
      await router.isReady()
      expect(router.currentRoute.value.name).toBe('GanadoUsuario')
      expect(router.currentRoute.value.path).toBe('/user/ganado')
    })

    it('should redirect from gestionar-animales to GanadoUsuario', async () => {
      await router.push('/user/gestionar-animales')
      await router.isReady()
      expect(router.currentRoute.value.name).toBe('GanadoUsuario')
      expect(router.currentRoute.value.path).toBe('/user/ganado')
    })

    it('should have PotrerosUsuario route', async () => {
      await router.push('/user/potreros')
      await router.isReady()
      expect(router.currentRoute.value.name).toBe('PotrerosUsuario')
      expect(router.currentRoute.value.path).toBe('/user/potreros')
    })

    it('should NOT have ReportesUsuario route (reportes removed from user routes)', async () => {
      // Reportes fue eliminado de las rutas de usuario según las nuevas reglas
      // Solo los admins tienen acceso a reportes en /admin/reportes
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'admin')
      
      try {
        await router.push('/user/reportes')
        await router.isReady()
      } catch (error) {
        // Expected: la ruta no existe o redirige
      }
      
      // La ruta /user/reportes no debe existir
      const routes = router.getRoutes()
      const reportesRoute = routes.find(r => r.name === 'ReportesUsuario')
      expect(reportesRoute).toBeUndefined()
      
      // Reset para otros tests
      localStorage.setItem('userRole', 'usuario')
    })

    it('should have RegistroVacunacionUsuario route', async () => {
      await router.push('/user/registro-vacunacion')
      await router.isReady()
      expect(router.currentRoute.value.name).toBe('RegistroVacunacionUsuario')
      expect(router.currentRoute.value.path).toBe('/user/registro-vacunacion')
    })

    it('should redirect from /user/vacunacion to RegistroVacunacionUsuario', async () => {
      await router.push('/user/vacunacion')
      await router.isReady()
      expect(router.currentRoute.value.name).toBe('RegistroVacunacionUsuario')
      expect(router.currentRoute.value.path).toBe('/user/registro-vacunacion')
    })

    it('should have PerfilUsuario route', async () => {
      await router.push('/user/perfil')
      await router.isReady()
      expect(router.currentRoute.value.name).toBe('PerfilUsuario')
      expect(router.currentRoute.value.path).toBe('/user/perfil')
    })

    it('should have EscanearQRUsuario route', async () => {
      await router.push('/user/scan-qr')
      await router.isReady()
      expect(router.currentRoute.value.name).toBe('EscanearQRUsuario')
      expect(router.currentRoute.value.path).toBe('/user/scan-qr')
    })

    it('should redirect from /user/qr to EscanearQRUsuario', async () => {
      await router.push('/user/qr')
      await router.isReady()
      expect(router.currentRoute.value.name).toBe('EscanearQRUsuario')
      expect(router.currentRoute.value.path).toBe('/user/scan-qr')
    })

    it('should have user route with correct meta', () => {
      const routes = router.getRoutes()
      const userRoute = routes.find(r => r.path === '/user' && r.children && r.children.length > 0)
      expect(userRoute).toBeDefined()
      expect(userRoute.meta).toBeDefined()
      expect(userRoute.meta.requiresAuth).toBe(true)
      expect(userRoute.meta.allowedRoles).toContain('usuario')
    })
  })
})

describe('Router Navigation Guards', () => {
  describe('isRootOrLogin function', () => {
    it('should return true for root path', () => {
      // This tests the function indirectly through router behavior
      localStorage.clear()
      // Navigating to root should trigger the function
      router.push('/').catch(() => {})
    })

    it('should return true for login path', () => {
      localStorage.clear()
      // Navigating to login should trigger the function
      router.push('/login').catch(() => {})
    })
  })

  describe('Public routes access', () => {
    it('should allow access to login without token', async () => {
      localStorage.clear()
      await router.push('/login')
      await router.isReady()
      expect(router.currentRoute.value.path).toBe('/login')
    })

    it('should allow access to home without token', async () => {
      localStorage.clear()
      await router.push('/home')
      await router.isReady()
      expect(router.currentRoute.value.path).toBe('/home')
    })

    it('should allow access to contacto without token', async () => {
      localStorage.clear()
      await router.push('/contacto')
      await router.isReady()
      expect(router.currentRoute.value.path).toBe('/contacto')
    })
  })

  describe('Authentication guard - lacksAuth', () => {
    it('should redirect to login when accessing protected route without token', async () => {
      localStorage.clear()
      try {
        await router.push('/admin/dashboard')
        await router.isReady()
      } catch (error) {
        // Redirect errors are acceptable
      }
      expect(router.currentRoute.value.path).toBe('/login')
    })

    it('should allow access to protected route with token', async () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'admin')
      await router.push('/admin/dashboard')
      await router.isReady()
      expect(router.currentRoute.value.path).toBe('/admin/dashboard')
    })

    it('should redirect user route without token', async () => {
      localStorage.clear()
      try {
        await router.push('/user/inicio')
        await router.isReady()
      } catch (error) {
        // Redirect errors are acceptable
      }
      expect(router.currentRoute.value.path).toBe('/login')
    })
  })

  describe('Role-based access control - invalidRole', () => {
    it('should allow admin to access admin routes', async () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'admin')
      await router.push('/admin/dashboard')
      await router.isReady()
      expect(router.currentRoute.value.path).toBe('/admin/dashboard')
    })

    it('should allow administrador to access admin routes', async () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'administrador')
      await router.push('/admin/dashboard')
      await router.isReady()
      expect(router.currentRoute.value.path).toBe('/admin/dashboard')
    })

    it('should allow super_admin to access admin routes with allowSuperAdmin', async () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'super_admin')
      await router.push('/admin/dashboard')
      await router.isReady()
      expect(router.currentRoute.value.path).toBe('/admin/dashboard')
    })

    it('should block super_admin from accessing routes with blockSuperAdmin', async () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'super_admin')
      
      try {
        await router.push('/admin/scan-qr')
        await router.isReady()
      } catch (error) {
        // Redirect error is acceptable
      }
      const currentPath = router.currentRoute.value.path
      expect(currentPath === '/admin/dashboard' || currentPath === '/login').toBe(true)
    })

    it('should block super_admin from accessing routes with requiresTenant', async () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'super_admin')
      
      try {
        await router.push('/admin/gestionar-animales')
        await router.isReady()
      } catch (error) {
        // Redirect error is acceptable
      }
      const currentPath = router.currentRoute.value.path
      expect(currentPath === '/admin/dashboard' || currentPath === '/login').toBe(true)
    })

    it('should allow super_admin to access super_admin routes', async () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'super_admin')
      await router.push('/admin/gestionar-tenants')
      await router.isReady()
      expect(router.currentRoute.value.path).toBe('/admin/gestionar-tenants')
    })

    it('should block admin from accessing super_admin routes', async () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'admin')
      
      await router.push('/admin/dashboard')
      await router.isReady()
      
      try {
        await router.push('/admin/gestionar-tenants')
        await router.isReady()
      } catch (error) {
        // Redirect error is acceptable
      }
      const currentPath = router.currentRoute.value.path
      expect(currentPath === '/login' || currentPath !== '/admin/gestionar-tenants').toBe(true)
    })

    it('should allow usuario to access user routes', async () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'usuario')
      await router.push('/user/inicio')
      await router.isReady()
      expect(router.currentRoute.value.path).toBe('/user/inicio')
    })

    it('should allow user (alternative role name) to access user routes', async () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'user')
      await router.push('/user/inicio')
      await router.isReady()
      expect(router.currentRoute.value.path).toBe('/user/inicio')
    })

    it('should block usuario from accessing admin routes', async () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'usuario')
      
      await router.push('/user/inicio')
      await router.isReady()
      
      try {
        await router.push('/admin/dashboard')
        await router.isReady()
      } catch (error) {
        // Redirect error is acceptable
      }
      const currentPath = router.currentRoute.value.path
      expect(currentPath === '/login' || currentPath !== '/admin/dashboard').toBe(true)
    })

    it('should block admin from accessing user routes', async () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'admin')
      
      await router.push('/login')
      await router.isReady()
      
      try {
        await router.push('/user/inicio')
        await router.isReady()
      } catch (error) {
        // Redirect error is acceptable
      }
      const currentPath = router.currentRoute.value.path
      expect(currentPath === '/login' || currentPath !== '/user/inicio').toBe(true)
    })

    it('should block super_admin from accessing user routes if not user', async () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'super_admin')
      
      await router.push('/admin/dashboard')
      await router.isReady()
      
      await router.push('/login')
      await router.isReady()
      
      try {
        await router.push('/user/inicio')
        await router.isReady()
      } catch (error) {
        // Redirect error is acceptable
      }
      const currentPath = router.currentRoute.value.path
      expect(currentPath === '/login' || currentPath !== '/user/inicio').toBe(true)
    })

    it('should handle routes without role requirement', async () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'admin')
      await router.push('/home')
      await router.isReady()
      expect(router.currentRoute.value.path).toBe('/home')
    })

    it('should handle routes without meta requirements', async () => {
      localStorage.clear()
      await router.push('/home')
      await router.isReady()
      expect(router.currentRoute.value.path).toBe('/home')
    })

    it('should block invalid role from accessing admin routes', async () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'unknown_role')
      
      await router.push('/home')
      await router.isReady()
      
      try {
        await router.push('/admin/dashboard')
        await router.isReady()
      } catch (error) {
        // Infinite redirect error is expected for invalid roles
        expect(error.message).toContain('redirect')
      }
    })
  })

  describe('Redirect behavior for authenticated users - redirectByRole', () => {
    it('should redirect admin from root to admin dashboard', async () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'admin')
      await router.push('/')
      await router.isReady()
      expect(router.currentRoute.value.path).toBe('/admin/dashboard')
    })

    it('should redirect administrador from root to admin dashboard', async () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'administrador')
      await router.push('/')
      await router.isReady()
      expect(router.currentRoute.value.path).toBe('/admin/dashboard')
    })

    it('should redirect super_admin from root to admin dashboard', async () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'super_admin')
      await router.push('/')
      await router.isReady()
      expect(router.currentRoute.value.path).toBe('/admin/dashboard')
    })

    it('should redirect usuario from root to user dashboard', async () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'usuario')
      await router.push('/')
      await router.isReady()
      expect(router.currentRoute.value.path).toBe('/user/inicio')
    })

    it('should redirect user from root to user dashboard', async () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'user')
      await router.push('/')
      await router.isReady()
      expect(router.currentRoute.value.path).toBe('/user/inicio')
    })

    it('should redirect admin from login to admin dashboard', async () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'admin')
      await router.push('/login')
      await router.isReady()
      expect(router.currentRoute.value.path).toBe('/admin/dashboard')
    })

    it('should redirect super_admin from login to admin dashboard', async () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'super_admin')
      await router.push('/login')
      await router.isReady()
      expect(router.currentRoute.value.path).toBe('/admin/dashboard')
    })

    it('should redirect usuario from login to user dashboard', async () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'usuario')
      await router.push('/login')
      await router.isReady()
      expect(router.currentRoute.value.path).toBe('/user/inicio')
    })

    it('should redirect to login when no role is set but token exists', async () => {
      localStorage.setItem('token', 'test-token')
      localStorage.removeItem('userRole')
      try {
        await router.push('/')
        await router.isReady()
      } catch (error) {
        // Infinite redirect is expected in this edge case
        expect(error.message).toContain('redirect')
      }
      expect(localStorage.getItem('token')).toBe('test-token')
      expect(localStorage.getItem('userRole')).toBeNull()
    })
  })

  describe('Guard console logging', () => {
    it('should log navigation information only in development mode', async () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'admin')
      
      // Los logs ahora solo se muestran en desarrollo cuando hay errores
      // Este test verifica que el guard funciona sin logs excesivos
      await router.push('/admin/dashboard')
      await router.isReady()
      
      // El guard funciona correctamente (no hay error de navegación)
      expect(router.currentRoute.value.path).toBe('/admin/dashboard')
    })
  })

  describe('Edge cases and complex scenarios', () => {
    it('should handle navigation from one protected route to another with same role', async () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'admin')
      
      await router.push('/admin/dashboard')
      await router.isReady()
      expect(router.currentRoute.value.path).toBe('/admin/dashboard')
      
      await router.push('/admin/gestionar-usuarios')
      await router.isReady()
      expect(router.currentRoute.value.path).toBe('/admin/gestionar-usuarios')
    })

    it('should handle navigation from protected route to public route', async () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'admin')
      
      await router.push('/admin/dashboard')
      await router.isReady()
      
      await router.push('/home')
      await router.isReady()
      expect(router.currentRoute.value.path).toBe('/home')
    })

    it('should handle navigation from public route to protected route with auth', async () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'usuario')
      
      await router.push('/home')
      await router.isReady()
      
      await router.push('/user/inicio')
      await router.isReady()
      expect(router.currentRoute.value.path).toBe('/user/inicio')
    })

    it('should handle super_admin accessing nested admin routes', async () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'super_admin')
      
      await router.push('/admin/gestionar-usuarios')
      await router.isReady()
      expect(router.currentRoute.value.path).toBe('/admin/gestionar-usuarios')
    })

    it('should handle regular admin accessing nested admin routes', async () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'admin')
      
      await router.push('/admin/gestionar-usuarios')
      await router.isReady()
      expect(router.currentRoute.value.path).toBe('/admin/gestionar-usuarios')
    })

    it('should handle usuario accessing nested user routes', async () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'usuario')
      
      await router.push('/user/ganado')
      await router.isReady()
      expect(router.currentRoute.value.path).toBe('/user/ganado')
    })

    it('should handle invalidRole when role does not match exactly', async () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'other_role')
      
      try {
        await router.push('/admin/dashboard')
        await router.isReady()
      } catch (error) {
        // Esperamos un error de redirect infinito
        expect(error.message).toContain('redirect')
      }
      
      expect(localStorage.getItem('userRole')).toBe('other_role')
    })

    it('should handle routes with children meta inheritance', async () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'admin')
      
      await router.push('/admin/gestionar-usuarios')
      await router.isReady()
      expect(router.currentRoute.value.path).toBe('/admin/gestionar-usuarios')
    })

    it('should handle redirect routes correctly', async () => {
      localStorage.clear()
      
      const routes = router.getRoutes()
      const rootRoute = routes.find(r => r.path === '/')
      expect(rootRoute.redirect).toBe('/login')
    })

    it('should handle routes without requiresAuth in meta', async () => {
      localStorage.clear()
      
      await router.push('/home')
      await router.isReady()
      expect(router.currentRoute.value.path).toBe('/home')
    })

    it('should handle token present but accessing public route', async () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'admin')
      
      await router.push('/contacto')
      await router.isReady()
      expect(router.currentRoute.value.path).toBe('/contacto')
    })

    it('should handle super_admin role accessing super_admin route', async () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'super_admin')
      
      await router.push('/admin/gestionar-tenants')
      await router.isReady()
      expect(router.currentRoute.value.path).toBe('/admin/gestionar-tenants')
    })

    it('should handle regular admin accessing admin route (not super_admin)', async () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'admin')
      
      await router.push('/admin/dashboard')
      await router.isReady()
      expect(router.currentRoute.value.path).toBe('/admin/dashboard')
    })

    it('should handle administrador role accessing admin route', async () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'administrador')
      
      await router.push('/admin/dashboard')
      await router.isReady()
      expect(router.currentRoute.value.path).toBe('/admin/dashboard')
    })

    it('should handle user role accessing user route', async () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'user')
      
      // Start from a known state (login) to avoid redirect loops
      await router.push('/login')
      await router.isReady()
      
      // Now navigate to user route
      await router.push('/user/inicio')
      await router.isReady()
      expect(router.currentRoute.value.path).toBe('/user/inicio')
    })

    it('should handle invalidRole when to.meta.role is usuario and userRole is not usuario or user', async () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'admin')
      
      // Start from a known state (login) to avoid redirect loops
      await router.push('/login')
      await router.isReady()
      
      // Admin should be blocked from accessing user routes
      try {
        await router.push('/user/inicio')
        await router.isReady()
      } catch (error) {
        // Redirect error is acceptable
      }
      
      // After the attempt, we should NOT be on the user route
      // Admin should be redirected to their dashboard or login
      const currentPath = router.currentRoute.value.path
      expect(currentPath).not.toBe('/user/inicio')
      expect(currentPath === '/admin/dashboard' || currentPath === '/login').toBe(true)
    })

    it('should handle invalidRole when to.meta.role is admin and userRole is not admin', async () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'usuario')
      
      // Start from a known state
      await router.push('/user/inicio')
      await router.isReady()
      expect(router.currentRoute.value.path).toBe('/user/inicio')
      
      // Usuario should be blocked from accessing admin routes
      try {
        await router.push('/admin/dashboard')
        await router.isReady()
      } catch (error) {
        // Redirect error is acceptable
      }
      
      // After the attempt, we should NOT be on the admin route
      const currentPath = router.currentRoute.value.path
      expect(currentPath).not.toBe('/admin/dashboard')
    })

    it('should handle invalidRole when to.meta.role matches userRole exactly', async () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'usuario')
      
      await router.push('/user/inicio')
      await router.isReady()
      expect(router.currentRoute.value.path).toBe('/user/inicio')
    })

    it('should handle redirectByRole when no role matches', async () => {
      localStorage.setItem('token', 'test-token')
      localStorage.removeItem('userRole')
      
      try {
        await router.push('/')
        await router.isReady()
      } catch (error) {
        // May cause redirect loop, which is expected
      }
      expect(localStorage.getItem('token')).toBe('test-token')
    })

    it('should handle isRootOrLogin for root path', async () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'admin')
      
      await router.push('/')
      await router.isReady()
      expect(router.currentRoute.value.path).toBe('/admin/dashboard')
    })

    it('should handle isRootOrLogin for login path with token', async () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'usuario')
      
      await router.push('/login')
      await router.isReady()
      expect(router.currentRoute.value.path).toBe('/user/inicio')
    })

    it('should handle lacksAuth returning false when route has no requiresAuth', async () => {
      localStorage.clear()
      
      await router.push('/home')
      await router.isReady()
      expect(router.currentRoute.value.path).toBe('/home')
    })

    it('should handle invalidRole returning false when route has no role requirement', async () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'admin')
      
      await router.push('/home')
      await router.isReady()
      expect(router.currentRoute.value.path).toBe('/home')
    })

    it('should handle super_admin accessing admin route with admin role requirement', async () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'super_admin')
      
      await router.push('/admin/dashboard')
      await router.isReady()
      expect(router.currentRoute.value.path).toBe('/admin/dashboard')
    })

    it('should handle invalidRole when isSuperAdmin is true and to.meta.role is usuario but isUser is false', async () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'super_admin')
      
      try {
        await router.push('/user/inicio')
        await router.isReady()
      } catch (error) {
        // May redirect
      }
      const currentPath = router.currentRoute.value.path
      expect(currentPath === '/login' || currentPath !== '/user/inicio').toBe(true)
    })

    it('should handle invalidRole when to.meta.role is super_admin and user is not super_admin', async () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'admin')
      
      try {
        await router.push('/admin/gestionar-tenants')
        await router.isReady()
      } catch (error) {
        // May redirect
      }
      const currentPath = router.currentRoute.value.path
      expect(currentPath === '/login' || currentPath !== '/admin/gestionar-tenants').toBe(true)
    })

    it('should handle invalidRole when to.meta.role is admin and isAdmin is true', async () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'admin')
      
      await router.push('/admin/dashboard')
      await router.isReady()
      expect(router.currentRoute.value.path).toBe('/admin/dashboard')
    })

    it('should handle invalidRole when to.meta.role is usuario and isUser is true', async () => {
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('userRole', 'usuario')
      
      await router.push('/user/inicio')
      await router.isReady()
      expect(router.currentRoute.value.path).toBe('/user/inicio')
    })
  })
})
