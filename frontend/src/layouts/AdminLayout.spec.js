import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { beforeEach, vi } from 'vitest'
import AdminLayout from './AdminLayout.vue'
import authService from '../services/authService.js'

// Mock de authService
vi.mock('../services/authService.js', () => ({
  default: {
    isAuthenticated: vi.fn(),
    getToken: vi.fn(),
    getRole: vi.fn(),
    isAdmin: vi.fn(),
    getUser: vi.fn(),
    logout: vi.fn()
  }
}))

// Mock de globalThis.location
const mockLocation = {
  href: '',
  reload: vi.fn(),
  pathname: '/',
  search: '',
  hash: ''
}
globalThis.location = mockLocation

describe('AdminLayout', () => {
  let router
  let wrapper

  beforeEach(() => {
    // Limpiar mocks
    vi.clearAllMocks()
    localStorage.clear()
    sessionStorage.clear()
    mockLocation.href = ''
    mockLocation.reload.mockClear()

    // Crear router mock con createMemoryHistory
    router = createRouter({
      history: createMemoryHistory(),
      routes: [
        {
          path: '/admin',
          component: AdminLayout,
          children: [
            { path: 'dashboard', component: { template: '<div>Dashboard</div>' } },
            { path: 'gestionar-tenants', component: { template: '<div>Gestionar Tenants</div>' } },
            { path: 'gestionar-usuarios', component: { template: '<div>Gestionar Usuarios</div>' } },
            { path: 'gestionar-animales', component: { template: '<div>Gestionar Animales</div>' } },
            { path: 'gestionar-potreros', component: { template: '<div>Gestionar Potreros</div>' } },
            { path: 'vacunacion', component: { template: '<div>Vacunacion</div>' } },
            { path: 'reportes', component: { template: '<div>Reportes</div>' } },
            { path: 'scan-qr', component: { template: '<div>Scan QR</div>' } }
          ]
        },
        { path: '/login', component: { template: '<div>Login</div>' } }
      ]
    })
  })

  const createWrapper = (options = {}) => {
    return mount(AdminLayout, {
      global: {
        plugins: [router],
        mocks: {
          $router: router
        }
      },
      ...options
    })
  }

  describe('Component Mounting', () => {
    it('should mount correctly', () => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.getToken.mockReturnValue('mock-token')
      authService.getRole.mockReturnValue('admin')
      authService.isAdmin.mockReturnValue(true)
      authService.getUser.mockReturnValue({
        persona: { primer_nombre: 'Test' },
        email: 'test@example.com'
      })

      wrapper = createWrapper()
      expect(wrapper.exists()).toBe(true)
    })

    it('should render navbar', () => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.getToken.mockReturnValue('mock-token')
      authService.getRole.mockReturnValue('admin')
      authService.isAdmin.mockReturnValue(true)
      authService.getUser.mockReturnValue({})

      wrapper = createWrapper()
      expect(wrapper.find('.navbar').exists()).toBe(true)
    })

    it('should render sidebar', () => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.getToken.mockReturnValue('mock-token')
      authService.getRole.mockReturnValue('admin')
      authService.isAdmin.mockReturnValue(true)
      authService.getUser.mockReturnValue({})

      wrapper = createWrapper()
      expect(wrapper.find('.admin-sidebar').exists()).toBe(true)
    })

    it('should render main content area', () => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.getToken.mockReturnValue('mock-token')
      authService.getRole.mockReturnValue('admin')
      authService.isAdmin.mockReturnValue(true)
      authService.getUser.mockReturnValue({})

      wrapper = createWrapper()
      expect(wrapper.find('.admin-main-content').exists()).toBe(true)
    })
  })

  describe('Computed Properties', () => {
    it('should return true for isSuperAdmin when role is super_admin', () => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.getToken.mockReturnValue('mock-token')
      authService.getRole.mockReturnValue('super_admin')
      authService.isAdmin.mockReturnValue(false)
      authService.getUser.mockReturnValue({})

      wrapper = createWrapper()
      expect(wrapper.vm.isSuperAdmin).toBe(true)
    })

    it('should return false for isSuperAdmin when role is not super_admin', () => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.getToken.mockReturnValue('mock-token')
      authService.getRole.mockReturnValue('admin')
      authService.isAdmin.mockReturnValue(true)
      authService.getUser.mockReturnValue({})

      wrapper = createWrapper()
      expect(wrapper.vm.isSuperAdmin).toBe(false)
    })

    it('should return "Super Admin" for userRoleDisplay when role is super_admin', () => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.getToken.mockReturnValue('mock-token')
      authService.getRole.mockReturnValue('super_admin')
      authService.isAdmin.mockReturnValue(false)
      authService.getUser.mockReturnValue({})

      wrapper = createWrapper()
      expect(wrapper.vm.userRoleDisplay).toBe('Super Admin')
    })

    it('should return "Administrador" for userRoleDisplay when role is admin', () => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.getToken.mockReturnValue('mock-token')
      authService.getRole.mockReturnValue('admin')
      authService.isAdmin.mockReturnValue(true)
      authService.getUser.mockReturnValue({})

      wrapper = createWrapper()
      expect(wrapper.vm.userRoleDisplay).toBe('Administrador')
    })

    it('should return "Administrador" for userRoleDisplay when role is administrador', () => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.getToken.mockReturnValue('mock-token')
      authService.getRole.mockReturnValue('administrador')
      authService.isAdmin.mockReturnValue(true)
      authService.getUser.mockReturnValue({})

      wrapper = createWrapper()
      expect(wrapper.vm.userRoleDisplay).toBe('Administrador')
    })

    it('should return "Admin" for userRoleDisplay for other roles', () => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.getToken.mockReturnValue('mock-token')
      authService.getRole.mockReturnValue('other_role')
      authService.isAdmin.mockReturnValue(false)
      authService.getUser.mockReturnValue({})

      wrapper = createWrapper()
      expect(wrapper.vm.userRoleDisplay).toBe('Admin')
    })
  })

  describe('Mounted Hook', () => {
    it('should redirect to login if user is not authenticated', async () => {
      authService.isAuthenticated.mockReturnValue(false)
      const pushSpy = vi.spyOn(router, 'push')

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(pushSpy).toHaveBeenCalledWith('/login')
    })

    it('should redirect to login if user is not admin and not super_admin', async () => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.getToken.mockReturnValue('mock-token')
      authService.getRole.mockReturnValue('usuario')
      authService.isAdmin.mockReturnValue(false)
      const pushSpy = vi.spyOn(router, 'push')

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(pushSpy).toHaveBeenCalledWith('/login')
    })

    it('should set userName from user.persona.primer_nombre', async () => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.getToken.mockReturnValue('mock-token')
      authService.getRole.mockReturnValue('admin')
      authService.isAdmin.mockReturnValue(true)
      authService.getUser.mockReturnValue({
        persona: { primer_nombre: 'Juan' }
      })

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.userName).toBe('Juan')
    })

    it('should set userName from user.primer_nombre if persona is not available', async () => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.getToken.mockReturnValue('mock-token')
      authService.getRole.mockReturnValue('admin')
      authService.isAdmin.mockReturnValue(true)
      authService.getUser.mockReturnValue({
        primer_nombre: 'Pedro'
      })

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.userName).toBe('Pedro')
    })

    it('should set userName from user.email if nombre is not available', async () => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.getToken.mockReturnValue('mock-token')
      authService.getRole.mockReturnValue('admin')
      authService.isAdmin.mockReturnValue(true)
      authService.getUser.mockReturnValue({
        email: 'test@example.com'
      })

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.userName).toBe('test@example.com')
    })

    it('should set userName to "Administrador" if user data is not available', async () => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.getToken.mockReturnValue('mock-token')
      authService.getRole.mockReturnValue('admin')
      authService.isAdmin.mockReturnValue(true)
      authService.getUser.mockReturnValue(null)

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.userName).toBe('Administrador')
    })

    it('should handle errors in mounted and redirect to login', async () => {
      authService.isAuthenticated.mockImplementation(() => {
        throw new Error('Test error')
      })
      const pushSpy = vi.spyOn(router, 'push')

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(pushSpy).toHaveBeenCalledWith('/login')
    })
  })

  describe('Logout Method', () => {
    beforeEach(() => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.getToken.mockReturnValue('mock-token')
      authService.getRole.mockReturnValue('admin')
      authService.isAdmin.mockReturnValue(true)
      authService.getUser.mockReturnValue({})
    })

    it('should call authService.logout', async () => {
       wrapper = createWrapper()
       await wrapper.vm.$nextTick()

       const mockEvent = { preventDefault: vi.fn(), stopPropagation: vi.fn() }
       await wrapper.vm.logout(mockEvent)

       expect(authService.logout).toHaveBeenCalled()
     })

    it('should clear localStorage and sessionStorage', async () => {
       localStorage.setItem('test', 'value')
       sessionStorage.setItem('test', 'value')

       wrapper = createWrapper()
       await wrapper.vm.$nextTick()

       await wrapper.vm.logout()

       expect(localStorage.getItem('test')).toBeNull()
       expect(sessionStorage.getItem('test')).toBeNull()
     })

    it('should prevent default and stop propagation if event is provided', async () => {
       wrapper = createWrapper()
       await wrapper.vm.$nextTick()

       const mockEvent = {
         preventDefault: vi.fn(),
         stopPropagation: vi.fn()
       }
       await wrapper.vm.logout(mockEvent)

       expect(mockEvent.preventDefault).toHaveBeenCalled()
       expect(mockEvent.stopPropagation).toHaveBeenCalled()
     })

    it('should redirect to login using router', async () => {
       const pushSpy = vi.spyOn(router, 'push').mockResolvedValue()

       wrapper = createWrapper()
       await wrapper.vm.$nextTick()

       await wrapper.vm.logout()

       expect(pushSpy).toHaveBeenCalledWith('/login')
     })

    it('should use globalThis.location.href if router.push fails', async () => {
       const pushSpy = vi.spyOn(router, 'push').mockRejectedValue(new Error('Router error'))

       wrapper = createWrapper()
       await wrapper.vm.$nextTick()

       await wrapper.vm.logout()

       // The component should attempt to use globalThis.location.href when router.push fails
       expect(pushSpy).toHaveBeenCalledWith('/login')
       expect(mockLocation.href).toBe('/login')
     })

    it('should handle errors in logout and use globalThis.location.href', async () => {
       authService.logout.mockImplementation(() => {
         throw new Error('Logout error')
       })

       wrapper = createWrapper()
       await wrapper.vm.$nextTick()

       await wrapper.vm.logout()

       expect(mockLocation.href).toBe('/login')
     })

    it('should reload page if cleanup also fails', async () => {
       authService.logout.mockImplementation(() => {
         throw new Error('Logout error')
       })
       const originalLocalStorage = globalThis.localStorage
       const originalSessionStorage = globalThis.sessionStorage
       globalThis.localStorage = { clear: vi.fn(() => { throw new Error('Clear error') }) }
       globalThis.sessionStorage = { clear: vi.fn(() => { throw new Error('Clear error') }) }
       mockLocation.href = ''
       mockLocation.reload.mockClear()

       wrapper = createWrapper()
       await wrapper.vm.$nextTick()

       await wrapper.vm.logout()

       // The component should attempt to reload when all cleanup fails
       expect(authService.logout).toHaveBeenCalled()
       expect(mockLocation.reload).toHaveBeenCalled()

       // Restore
       globalThis.localStorage = originalLocalStorage
       globalThis.sessionStorage = originalSessionStorage
     })
  })

  describe('Template Rendering', () => {
    beforeEach(() => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.getToken.mockReturnValue('mock-token')
      authService.getRole.mockReturnValue('admin')
      authService.isAdmin.mockReturnValue(true)
      authService.getUser.mockReturnValue({
        persona: { primer_nombre: 'Test' }
      })
    })

    it('should display userName in navbar', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const userNameElement = wrapper.find('.fw-semibold.small')
      expect(userNameElement.exists()).toBe(true)
    })

    it('should display userRoleDisplay in navbar', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const roleBadge = wrapper.find('.badge')
      expect(roleBadge.exists()).toBe(true)
    })

    it('should show super admin icon when isSuperAdmin is true', async () => {
      authService.getRole.mockReturnValue('super_admin')
      authService.isAdmin.mockReturnValue(false)

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const icon = wrapper.find('.fa-user-crown')
      expect(icon.exists()).toBe(true)
    })

    it('should show admin icon when isSuperAdmin is false', async () => {
      authService.getRole.mockReturnValue('admin')
      authService.isAdmin.mockReturnValue(true)

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const icon = wrapper.find('.fa-user-shield')
      expect(icon.exists()).toBe(true)
    })

    it('should show tenants link when isSuperAdmin is true', async () => {
       authService.getRole.mockReturnValue('super_admin')
       authService.isAdmin.mockReturnValue(false)

       wrapper = createWrapper()
       await wrapper.vm.$nextTick()

       const tenantsLink = wrapper.find('a[href="/admin/gestionar-tenants"]')
       expect(tenantsLink.exists()).toBe(true)
     })

    it('should render logout button', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const logoutButton = wrapper.find('button[title="Cerrar sesión"]')
      expect(logoutButton.exists()).toBe(true)
    })

    it('should call logout when logout button is clicked', async () => {
       wrapper = createWrapper()
       await wrapper.vm.$nextTick()

       const logoutSpy = vi.spyOn(wrapper.vm, 'logout')
       const logoutButton = wrapper.find('button[title="Cerrar sesión"]')
       await logoutButton.trigger('click')

       expect(logoutSpy).toHaveBeenCalled()
       // Wait for the async logout to complete
       await logoutSpy.mock.results[0].value
     })
  })
})

