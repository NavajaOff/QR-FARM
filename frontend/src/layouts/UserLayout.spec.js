import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { beforeEach, afterEach, vi, describe, it, expect } from 'vitest'
import UserLayout from './UserLayout.vue'
import authService from '../services/authService.js'

// Mock de authService
vi.mock('../services/authService.js', () => ({
  default: {
    isAuthenticated: vi.fn(),
    isUser: vi.fn(),
    getUser: vi.fn(),
    logout: vi.fn()
  }
}))

describe('UserLayout.vue', () => {
  let router
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    console.error = vi.fn()
    console.log = vi.fn()

    // Mock de location para createMemoryHistory
    globalThis.location = {
      pathname: '/',
      search: '',
      hash: ''
    }

    // Crear router mock con createMemoryHistory
    router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/login', component: { template: '<div>Login</div>' } },
        { path: '/user/inicio', component: { template: '<div>Inicio</div>' } },
        { path: '/user/ganado', component: { template: '<div>Ganado</div>' } },
        { path: '/user/potreros', component: { template: '<div>Potreros</div>' } },
        { path: '/user/reportes', component: { template: '<div>Reportes</div>' } },
        { path: '/user/registro-vacunacion', component: { template: '<div>Vacunacion</div>' } },
        { path: '/user/perfil', component: { template: '<div>Perfil</div>' } },
        { path: '/user/qr', component: { template: '<div>QR</div>' } }
      ]
    })

    // Setup default mocks
    authService.isAuthenticated.mockReturnValue(true)
    authService.isUser.mockReturnValue(true)
    authService.getUser.mockReturnValue({
      persona: {
        primer_nombre: 'Juan'
      }
    })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = (options = {}) => {
    return mount(UserLayout, {
      global: {
        plugins: [router],
        mocks: {
          $router: router
        }
      },
      ...options
    })
  }

  describe('Component Rendering', () => {
    it('should render the component', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(wrapper.find('.user-layout').exists()).toBe(true)
    })

    it('should render navbar', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const navbar = wrapper.find('.navbar')
      expect(navbar.exists()).toBe(true)
      expect(navbar.classes()).toContain('bg-success')
    })

    it('should render user name in navbar', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const userNameSpan = wrapper.find('.navbar .fw-bold')
      expect(userNameSpan.exists()).toBe(true)
      expect(userNameSpan.text()).toBe('Juan')
    })

    it('should render "Usuario" badge', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const badge = wrapper.find('.badge.bg-info')
      expect(badge.exists()).toBe(true)
      expect(badge.text()).toBe('Usuario')
    })

    it('should render QR FARM brand link', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const brandLink = wrapper.findComponent({ name: 'RouterLink' })
      expect(brandLink.exists()).toBe(true)
      expect(brandLink.text()).toContain('QR FARM')
      expect(brandLink.props('to')).toBe('/user/inicio')
    })

    it('should render logout button', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const logoutButtons = wrapper.findAll('button.btn-outline-light')
      // There are two buttons: mobile menu and logout
      const logoutButton = logoutButtons.find(btn => btn.text().includes('Salir'))
      expect(logoutButton).toBeDefined()
      expect(logoutButton.text()).toContain('Salir')
    })

    it('should render mobile menu button', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const menuButton = wrapper.find('button[data-bs-toggle="offcanvas"]')
      expect(menuButton.exists()).toBe(true)
      expect(menuButton.classes()).toContain('d-md-none')
    })

    it('should render sidebar', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const sidebar = wrapper.find('.user-sidebar')
      expect(sidebar.exists()).toBe(true)
      expect(sidebar.classes()).toContain('d-none')
      expect(sidebar.classes()).toContain('d-md-block')
    })

    it('should render all sidebar navigation links', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const navLinks = wrapper.findAllComponents({ name: 'RouterLink' })
      // Filter only sidebar links (exclude brand link)
      const sidebarLinks = navLinks.filter(link => {
        const parent = link.element.closest('.user-sidebar')
        return parent !== null
      })
      expect(sidebarLinks.length).toBe(7)

      const expectedRoutes = [
        { to: '/user/inicio', text: 'Inicio' },
        { to: '/user/ganado', text: 'Mi Ganado' },
        { to: '/user/potreros', text: 'Potreros' },
        { to: '/user/reportes', text: 'Reportes' },
        { to: '/user/registro-vacunacion', text: 'Vacunación' },
        { to: '/user/perfil', text: 'Perfil' },
        { to: '/user/qr', text: 'Escanear QR' }
      ]

      expectedRoutes.forEach((expected, index) => {
        const link = sidebarLinks[index]
        expect(link.props('to')).toBe(expected.to)
        expect(link.text()).toContain(expected.text)
      })
    })

    it('should render router-view', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const routerView = wrapper.find('.user-main-content')
      expect(routerView.exists()).toBe(true)
      // router-view is rendered as a component
      const routerViewComponent = wrapper.findComponent({ name: 'RouterView' })
      expect(routerViewComponent.exists()).toBe(true)
    })
  })

  describe('Authentication and Mounted Hook', () => {
    it('should redirect to login if not authenticated', async () => {
      authService.isAuthenticated.mockReturnValue(false)
      const pushSpy = vi.spyOn(router, 'push')

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(pushSpy).toHaveBeenCalledWith('/login')
    })

    it('should redirect to login if not user', async () => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.isUser.mockReturnValue(false)
      const pushSpy = vi.spyOn(router, 'push')

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(pushSpy).toHaveBeenCalledWith('/login')
    })

    it('should set userName from user data when authenticated and user', async () => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.isUser.mockReturnValue(true)
      authService.getUser.mockReturnValue({
        persona: {
          primer_nombre: 'María'
        }
      })

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.userName).toBe('María')
      const userNameSpan = wrapper.find('.navbar .fw-bold')
      expect(userNameSpan.text()).toBe('María')
    })

    it('should set userName to "Usuario" when user data is missing', async () => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.isUser.mockReturnValue(true)
      authService.getUser.mockReturnValue(null)

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.userName).toBe('Usuario')
      const userNameSpan = wrapper.find('.navbar .fw-bold')
      expect(userNameSpan.text()).toBe('Usuario')
    })

    it('should set userName to "Usuario" when persona is missing', async () => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.isUser.mockReturnValue(true)
      authService.getUser.mockReturnValue({})

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.userName).toBe('Usuario')
    })

    it('should set userName to "Usuario" when primer_nombre is missing', async () => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.isUser.mockReturnValue(true)
      authService.getUser.mockReturnValue({
        persona: {}
      })

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.userName).toBe('Usuario')
    })
  })

  describe('Logout Functionality', () => {
    it('should call logout method when logout button is clicked', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const logoutSpy = vi.spyOn(wrapper.vm, 'logout')
      const logoutButtons = wrapper.findAll('button.btn-outline-light')
      const logoutButton = logoutButtons.find(btn => btn.text().includes('Salir'))

      await logoutButton.trigger('click')

      expect(logoutSpy).toHaveBeenCalled()
    })

    it('should call authService.logout and redirect to login', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const pushSpy = vi.spyOn(router, 'push')
      const logoutButtons = wrapper.findAll('button.btn-outline-light')
      const logoutButton = logoutButtons.find(btn => btn.text().includes('Salir'))

      await logoutButton.trigger('click')

      expect(authService.logout).toHaveBeenCalled()
      expect(pushSpy).toHaveBeenCalledWith('/login')
    })

    it('should handle logout method call', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const pushSpy = vi.spyOn(router, 'push')
      wrapper.vm.logout()

      expect(authService.logout).toHaveBeenCalled()
      expect(pushSpy).toHaveBeenCalledWith('/login')
    })
  })

  describe('Sidebar Navigation Links', () => {
    it('should have correct route for Inicio link', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const navLinks = wrapper.findAllComponents({ name: 'RouterLink' })
      const sidebarLinks = navLinks.filter(link => {
        const parent = link.element.closest('.user-sidebar')
        return parent !== null
      })
      const inicioLink = sidebarLinks[0]
      expect(inicioLink.props('to')).toBe('/user/inicio')
      expect(inicioLink.text()).toContain('Inicio')
    })

    it('should have correct route for Mi Ganado link', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const navLinks = wrapper.findAllComponents({ name: 'RouterLink' })
      const sidebarLinks = navLinks.filter(link => {
        const parent = link.element.closest('.user-sidebar')
        return parent !== null
      })
      const ganadoLink = sidebarLinks[1]
      expect(ganadoLink.props('to')).toBe('/user/ganado')
      expect(ganadoLink.text()).toContain('Mi Ganado')
    })

    it('should have correct route for Potreros link', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const navLinks = wrapper.findAllComponents({ name: 'RouterLink' })
      const sidebarLinks = navLinks.filter(link => {
        const parent = link.element.closest('.user-sidebar')
        return parent !== null
      })
      const potrerosLink = sidebarLinks[2]
      expect(potrerosLink.props('to')).toBe('/user/potreros')
      expect(potrerosLink.text()).toContain('Potreros')
    })

    it('should have correct route for Reportes link', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const navLinks = wrapper.findAllComponents({ name: 'RouterLink' })
      const sidebarLinks = navLinks.filter(link => {
        const parent = link.element.closest('.user-sidebar')
        return parent !== null
      })
      const reportesLink = sidebarLinks[3]
      expect(reportesLink.props('to')).toBe('/user/reportes')
      expect(reportesLink.text()).toContain('Reportes')
    })

    it('should have correct route for Vacunación link', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const navLinks = wrapper.findAllComponents({ name: 'RouterLink' })
      const sidebarLinks = navLinks.filter(link => {
        const parent = link.element.closest('.user-sidebar')
        return parent !== null
      })
      const vacunacionLink = sidebarLinks[4]
      expect(vacunacionLink.props('to')).toBe('/user/registro-vacunacion')
      expect(vacunacionLink.text()).toContain('Vacunación')
    })

    it('should have correct route for Perfil link', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const navLinks = wrapper.findAllComponents({ name: 'RouterLink' })
      const sidebarLinks = navLinks.filter(link => {
        const parent = link.element.closest('.user-sidebar')
        return parent !== null
      })
      const perfilLink = sidebarLinks[5]
      expect(perfilLink.props('to')).toBe('/user/perfil')
      expect(perfilLink.text()).toContain('Perfil')
    })

    it('should have correct route for Escanear QR link', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const navLinks = wrapper.findAllComponents({ name: 'RouterLink' })
      const sidebarLinks = navLinks.filter(link => {
        const parent = link.element.closest('.user-sidebar')
        return parent !== null
      })
      const qrLink = sidebarLinks[6]
      expect(qrLink.props('to')).toBe('/user/qr')
      expect(qrLink.text()).toContain('Escanear QR')
    })
  })

  describe('Icons and Visual Elements', () => {
    it('should render user icon in navbar', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const userIcon = wrapper.find('.navbar .fa-user')
      expect(userIcon.exists()).toBe(true)
    })

    it('should render cow icon in brand', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const cowIcon = wrapper.find('.navbar .fa-cow')
      expect(cowIcon.exists()).toBe(true)
    })

    it('should render logout icon in logout button', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const logoutIcon = wrapper.find('.navbar .fa-sign-out-alt')
      expect(logoutIcon.exists()).toBe(true)
    })

    it('should render menu icon in mobile button', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const menuIcon = wrapper.find('button[data-bs-toggle="offcanvas"] .fa-bars')
      expect(menuIcon.exists()).toBe(true)
    })

    it('should render icons in sidebar links', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const icons = [
        'fa-home',
        'fa-cow',
        'fa-map-marked-alt',
        'fa-chart-line',
        'fa-syringe',
        'fa-user-edit',
        'fa-qrcode'
      ]

      icons.forEach(iconClass => {
        const icon = wrapper.find(`.user-sidebar .${iconClass}`)
        expect(icon.exists()).toBe(true)
      })
    })
  })

  describe('Component Structure', () => {
    it('should have correct component name', () => {
      expect(UserLayout.name).toBe('UserLayout')
    })

    it('should initialize with empty userName', () => {
      const data = UserLayout.data()
      expect(data.userName).toBe('')
    })

    it('should have mounted hook', () => {
      expect(typeof UserLayout.mounted).toBe('function')
    })

    it('should have logout method', () => {
      expect(typeof UserLayout.methods.logout).toBe('function')
    })
  })
})

