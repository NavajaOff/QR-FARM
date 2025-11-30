import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { beforeEach, vi } from 'vitest'
import perfilAdmin from './perfil-admin.js'
import authService from '../../services/authService.js'

// Mock de authService
vi.mock('../../services/authService.js', () => ({
  default: {
    isAuthenticated: vi.fn(),
    isAdmin: vi.fn(),
    getUser: vi.fn(),
    getRole: vi.fn(),
    logout: vi.fn()
  }
}))

describe('perfil-admin.js', () => {
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
        { path: '/login', component: { template: '<div>Login</div>' } }
      ]
    })
  })

  const createWrapper = (options = {}) => {
    return mount(perfilAdmin, {
      global: {
        plugins: [router],
        mocks: {
          $router: router
        }
      },
      ...options
    })
  }

  describe('Component Definition', () => {
    it('should export a Vue component', () => {
      expect(perfilAdmin).toBeDefined()
      expect(perfilAdmin.name).toBe('PerfilAdmin')
    })

    it('should have data function', () => {
      expect(typeof perfilAdmin.data).toBe('function')
      const data = perfilAdmin.data()
      expect(data).toHaveProperty('userName')
      expect(data).toHaveProperty('profile')
      expect(data).toHaveProperty('passwordData')
    })

    it('should have mounted hook', () => {
      expect(typeof perfilAdmin.mounted).toBe('function')
    })

    it('should have methods object', () => {
      expect(perfilAdmin.methods).toBeDefined()
      expect(typeof perfilAdmin.methods.loadProfile).toBe('function')
      expect(typeof perfilAdmin.methods.updateProfile).toBe('function')
      expect(typeof perfilAdmin.methods.changePassword).toBe('function')
      expect(typeof perfilAdmin.methods.logout).toBe('function')
    })
  })

  describe('Data Initialization', () => {
    it('should initialize with default values', () => {
      const data = perfilAdmin.data()
      expect(data.userName).toBe('')
      expect(data.user).toBeNull()
      expect(data.userRole).toBe('')
      expect(data.loading).toBe(false)
      expect(data.passwordLoading).toBe(false)
      expect(data.message).toBe('')
      expect(data.messageType).toBe('')
      expect(data.profile).toEqual({
        primerNombre: '',
        segundoNombre: '',
        primerApellido: '',
        segundoApellido: '',
        email: '',
        telefono: ''
      })
      expect(data.passwordData).toEqual({
        current: '',
        new: '',
        confirm: ''
      })
    })
  })

  describe('Mounted Hook', () => {
    it('should redirect to login if not authenticated', async () => {
      authService.isAuthenticated.mockReturnValue(false)
      const pushSpy = vi.spyOn(router, 'push')

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(pushSpy).toHaveBeenCalledWith('/login')
    })

    it('should redirect to login if not admin', async () => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.isAdmin.mockReturnValue(false)
      const pushSpy = vi.spyOn(router, 'push')

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(pushSpy).toHaveBeenCalledWith('/login')
    })

    it('should set user data when authenticated and admin', async () => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.isAdmin.mockReturnValue(true)
      authService.getUser.mockReturnValue({
        persona: { primer_nombre: 'Juan' }
      })
      authService.getRole.mockReturnValue('admin')

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.userName).toBe('Juan')
      expect(wrapper.vm.userRole).toBe('admin')
    })

    it('should call loadProfile', async () => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.isAdmin.mockReturnValue(true)
      authService.getUser.mockReturnValue({})

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.profile.primerNombre).toBe('')
    })
  })

  describe('loadProfile Method', () => {
    it('should load profile data from user', () => {
      wrapper = createWrapper()
      wrapper.vm.user = {
        persona: {
          primer_nombre: 'Juan',
          segundo_nombre: 'Carlos',
          primer_apellido: 'Pérez',
          segundo_apellido: 'Gómez',
          email: 'juan@example.com',
          telefono: '123456789'
        }
      }

      wrapper.vm.loadProfile()

      expect(wrapper.vm.profile.primerNombre).toBe('Juan')
      expect(wrapper.vm.profile.segundoNombre).toBe('Carlos')
      expect(wrapper.vm.profile.primerApellido).toBe('Pérez')
      expect(wrapper.vm.profile.segundoApellido).toBe('Gómez')
      expect(wrapper.vm.profile.email).toBe('juan@example.com')
      expect(wrapper.vm.profile.telefono).toBe('123456789')
    })

    it('should handle user without persona', () => {
      wrapper = createWrapper()
      wrapper.vm.user = {}

      wrapper.vm.loadProfile()

      expect(wrapper.vm.profile.primerNombre).toBe('')
    })
  })

  describe('updateProfile Method', () => {
    beforeEach(() => {
      vi.useFakeTimers()
    })

    afterEach(() => {
      vi.useRealTimers()
    })

    it('should update profile successfully', async () => {
      wrapper = createWrapper()

      const promise = wrapper.vm.updateProfile()
      await vi.advanceTimersByTime(1000)
      await promise

      expect(wrapper.vm.message).toBe('Perfil actualizado exitosamente')
      expect(wrapper.vm.messageType).toBe('success')
      expect(wrapper.vm.loading).toBe(false)
    })

    it('should handle errors', async () => {
      wrapper = createWrapper()
      // Simulate error by mocking setTimeout to throw
      const originalSetTimeout = globalThis.setTimeout
      globalThis.setTimeout = vi.fn((cb, delay) => {
        throw new Error('Test error')
      })

      await wrapper.vm.updateProfile()

      expect(wrapper.vm.message).toBe('Error al actualizar el perfil')
      expect(wrapper.vm.messageType).toBe('error')
      expect(wrapper.vm.loading).toBe(false)

      globalThis.setTimeout = originalSetTimeout
    })
  })

  describe('changePassword Method', () => {
    beforeEach(() => {
      vi.useFakeTimers()
    })

    afterEach(() => {
      vi.useRealTimers()
    })

    it('should show error if passwords do not match', () => {
      wrapper = createWrapper()
      wrapper.vm.passwordData = {
        current: 'old',
        new: 'new',
        confirm: 'different'
      }

      wrapper.vm.changePassword()

      expect(wrapper.vm.message).toBe('Las contraseñas no coinciden')
      expect(wrapper.vm.messageType).toBe('error')
    })

    it('should change password successfully', async () => {
      wrapper = createWrapper()
      wrapper.vm.passwordData = {
        current: 'old',
        new: 'new',
        confirm: 'new'
      }

      const promise = wrapper.vm.changePassword()
      await vi.advanceTimersByTime(1000)
      await promise

      expect(wrapper.vm.message).toBe('Contraseña cambiada exitosamente')
      expect(wrapper.vm.messageType).toBe('success')
      expect(wrapper.vm.passwordData).toEqual({
        current: '',
        new: '',
        confirm: ''
      })
      expect(wrapper.vm.passwordLoading).toBe(false)
    })
  })

  describe('formatDate Method', () => {
    it('should format date correctly', () => {
      wrapper = createWrapper()
      const result = wrapper.vm.formatDate('2023-10-15')
      expect(result).toMatch(/\d{1,2}\/\d{1,2}\/\d{4}/)
    })

    it('should return N/A for invalid date', () => {
      wrapper = createWrapper()
      const result = wrapper.vm.formatDate(null)
      expect(result).toBe('N/A')
    })
  })

  describe('logout Method', () => {
    it('should call authService.logout and redirect', () => {
      const pushSpy = vi.spyOn(router, 'push')
      wrapper = createWrapper()

      wrapper.vm.logout()

      expect(authService.logout).toHaveBeenCalled()
      expect(pushSpy).toHaveBeenCalledWith('/login')
    })
  })
})