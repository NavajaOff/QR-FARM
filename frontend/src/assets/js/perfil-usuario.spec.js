import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { beforeEach, vi } from 'vitest'
import perfilUsuario from './perfil-usuario.js'
import authService from '../../services/authService.js'
import { authAPI } from '../../services/api.js'

// Mock de authService
vi.mock('../../services/authService.js', () => ({
  default: {
    isAuthenticated: vi.fn(),
    isUser: vi.fn(),
    getUser: vi.fn(),
    getRole: vi.fn(),
    logout: vi.fn()
  }
}))

// Mock de API
vi.mock('../../services/api.js', () => ({
  authAPI: {
    getProfile: vi.fn(),
    updateProfile: vi.fn()
  }
}))

describe('perfil-usuario.js', () => {
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
        { path: '/user/profile', component: { template: '<div>Profile</div>' }, name: 'PerfilUsuario' }
      ]
    })
  })

  const createWrapper = (options = {}) => {
    return mount(perfilUsuario, {
      global: {
        plugins: [router],
        mocks: {
          $router: router,
          $route: { name: 'PerfilUsuario' }
        }
      },
      ...options
    })
  }

  describe('Component Definition', () => {
    it('should export a Vue component', () => {
      expect(perfilUsuario).toBeDefined()
      expect(perfilUsuario.name).toBe('PerfilUsuario')
    })

    it('should have data function', () => {
      expect(typeof perfilUsuario.data).toBe('function')
      const data = perfilUsuario.data()
      expect(data).toHaveProperty('userName')
      expect(data).toHaveProperty('profile')
    })

    it('should have mounted hook', () => {
      expect(typeof perfilUsuario.mounted).toBe('function')
    })

    it('should have watch object', () => {
      expect(perfilUsuario.watch).toBeDefined()
      expect(typeof perfilUsuario.watch.$route).toBe('function')
    })

    it('should have methods object', () => {
      expect(perfilUsuario.methods).toBeDefined()
      expect(typeof perfilUsuario.methods.fetchProfile).toBe('function')
      expect(typeof perfilUsuario.methods.updateProfile).toBe('function')
      expect(typeof perfilUsuario.methods.cancelarEdicion).toBe('function')
    })
  })

  describe('Data Initialization', () => {
    it('should initialize with default values', () => {
      const data = perfilUsuario.data()
      expect(data.userName).toBe('')
      expect(data.userRole).toBe('')
      expect(data.loading).toBe(false)
      expect(data.message).toBe('')
      expect(data.messageType).toBe('')
      expect(data.mostrarResumen).toBe(true)
      expect(data.profile).toEqual({
        nombreCompleto: '',
        email: '',
        telefono: '',
        fechaCreacion: ''
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

    it('should redirect to login if not user', async () => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.isUser.mockReturnValue(false)
      const pushSpy = vi.spyOn(router, 'push')

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(pushSpy).toHaveBeenCalledWith('/login')
    })

    it('should set user data when authenticated and user', async () => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.isUser.mockReturnValue(true)
      authService.getUser.mockReturnValue({
        persona: { primer_nombre: 'Juan' }
      })
      authService.getRole.mockReturnValue('user')
      authAPI.getProfile.mockResolvedValue({
        data: { status: 'success', data: {} }
      })

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.userName).toBe('Juan')
      expect(wrapper.vm.userRole).toBe('user')
      expect(authAPI.getProfile).toHaveBeenCalled()
    })
  })

  describe('fetchProfile Method', () => {
    it('should fetch profile successfully', async () => {
      authAPI.getProfile.mockResolvedValue({
        data: {
          status: 'success',
          data: {
            nombre_completo: 'Juan Pérez',
            email: 'juan@example.com',
            telefono: '123456789',
            fecha_creacion: '2023-01-01'
          }
        }
      })

      wrapper = createWrapper()
      await wrapper.vm.fetchProfile()

      expect(wrapper.vm.profile.nombreCompleto).toBe('Juan Pérez')
      expect(wrapper.vm.profile.email).toBe('juan@example.com')
      expect(wrapper.vm.profile.telefono).toBe('123456789')
      expect(wrapper.vm.profile.fechaCreacion).toBe('2023-01-01')
      expect(wrapper.vm.mostrarResumen).toBe(true)
    })

    it('should handle API errors', async () => {
      authAPI.getProfile.mockRejectedValue(new Error('Network error'))

      wrapper = createWrapper()
      await wrapper.vm.fetchProfile()

      expect(wrapper.vm.message).toBe('Network error')
      expect(wrapper.vm.messageType).toBe('error')
    })

    it('should handle unsuccessful response', async () => {
      authAPI.getProfile.mockResolvedValue({
        data: { status: 'error', message: 'Profile not found' }
      })

      wrapper = createWrapper()
      await wrapper.vm.fetchProfile()

      expect(wrapper.vm.message).toBe('Profile not found')
      expect(wrapper.vm.messageType).toBe('error')
    })
  })

  describe('updateProfile Method', () => {
    it('should update profile successfully', async () => {
      authAPI.updateProfile.mockResolvedValue({
        data: { status: 'success', message: 'Updated successfully' }
      })
      authAPI.getProfile.mockResolvedValue({
        data: { status: 'success', data: {} }
      })

      wrapper = createWrapper()
      wrapper.vm.profile = {
        nombreCompleto: 'Juan Pérez',
        email: 'juan@example.com',
        telefono: '123456789'
      }

      await wrapper.vm.updateProfile()

      expect(authAPI.updateProfile).toHaveBeenCalledWith({
        nombre_completo: 'Juan Pérez',
        email: 'juan@example.com',
        telefono: '123456789'
      })
      expect(wrapper.vm.message).toBe('Updated successfully')
      expect(wrapper.vm.messageType).toBe('success')
      expect(wrapper.vm.mostrarResumen).toBe(true)
      expect(wrapper.vm.loading).toBe(false)
    })

    it('should handle update errors', async () => {
      authAPI.updateProfile.mockRejectedValue(new Error('Update failed'))

      wrapper = createWrapper()
      await wrapper.vm.updateProfile()

      expect(wrapper.vm.message).toBe('Update failed')
      expect(wrapper.vm.messageType).toBe('error')
      expect(wrapper.vm.loading).toBe(false)
    })
  })

  describe('cancelarEdicion Method', () => {
    it('should cancel editing and refetch profile', () => {
      authAPI.getProfile.mockResolvedValue({
        data: { status: 'success', data: {} }
      })

      wrapper = createWrapper()
      wrapper.vm.mostrarResumen = false

      wrapper.vm.cancelarEdicion()

      expect(wrapper.vm.mostrarResumen).toBe(true)
      expect(authAPI.getProfile).toHaveBeenCalled()
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

  describe('Watch $route', () => {
    it('should refetch profile when route is PerfilUsuario', () => {
      authAPI.getProfile.mockResolvedValue({
        data: { status: 'success', data: {} }
      })

      wrapper = createWrapper()
      perfilUsuario.watch.$route.call(wrapper.vm, { name: 'PerfilUsuario' })

      expect(authAPI.getProfile).toHaveBeenCalled()
    })

    it('should not refetch profile for other routes', () => {
      // Create a mock vm without mounting the component
      const mockVm = {
        fetchProfile: vi.fn()
      }
      perfilUsuario.watch.$route.call(mockVm, { name: 'OtherRoute' })

      expect(mockVm.fetchProfile).not.toHaveBeenCalled()
    })
  })

  describe('Edge Cases', () => {
    it('should handle fetchProfile with missing data fields', async () => {
      authAPI.getProfile.mockResolvedValue({
        data: {
          status: 'success',
          data: {
            nombre_completo: null,
            email: null,
            telefono: null,
            fecha_creacion: null
          }
        }
      })

      wrapper = createWrapper()
      await wrapper.vm.fetchProfile()

      expect(wrapper.vm.profile.nombreCompleto).toBe('')
      expect(wrapper.vm.profile.email).toBe('')
      expect(wrapper.vm.profile.telefono).toBe('')
      expect(wrapper.vm.profile.fechaCreacion).toBe('')
    })

    it('should handle fetchProfile with response without status', async () => {
      authAPI.getProfile.mockResolvedValue({
        data: { data: {} }
      })

      wrapper = createWrapper()
      await wrapper.vm.fetchProfile()

      expect(wrapper.vm.message).toBe('No se pudo cargar el perfil')
      expect(wrapper.vm.messageType).toBe('error')
    })

    it('should handle updateProfile with response without status', async () => {
      authAPI.updateProfile.mockResolvedValue({
        data: {} // No status and no message
      })

      wrapper = createWrapper()
      await wrapper.vm.updateProfile()

      // When status is not 'success', it throws with message || default
      expect(wrapper.vm.message).toBe('No se pudo actualizar el perfil')
      expect(wrapper.vm.messageType).toBe('error')
    })

    it('should handle updateProfile with success but no message', async () => {
      authAPI.updateProfile.mockResolvedValue({
        data: { status: 'success' }
      })
      authAPI.getProfile.mockResolvedValue({
        data: { status: 'success', data: {} }
      })

      wrapper = createWrapper()
      await wrapper.vm.updateProfile()

      expect(wrapper.vm.message).toBe('Perfil actualizado exitosamente')
      expect(wrapper.vm.messageType).toBe('success')
    })

    it('should handle formatDate with empty string', () => {
      wrapper = createWrapper()
      const result = wrapper.vm.formatDate('')
      expect(result).toBe('N/A')
    })

    it('should handle formatDate with undefined', () => {
      wrapper = createWrapper()
      const result = wrapper.vm.formatDate(undefined)
      expect(result).toBe('N/A')
    })

    it('should handle userName with null persona', async () => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.isUser.mockReturnValue(true)
      authService.getUser.mockReturnValue({ persona: null })
      authService.getRole.mockReturnValue('user')
      authAPI.getProfile.mockResolvedValue({
        data: { status: 'success', data: {} }
      })

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.userName).toBe('Usuario')
    })

    it('should handle userName with missing primer_nombre', async () => {
      authService.isAuthenticated.mockReturnValue(true)
      authService.isUser.mockReturnValue(true)
      authService.getUser.mockReturnValue({ persona: {} })
      authService.getRole.mockReturnValue('user')
      authAPI.getProfile.mockResolvedValue({
        data: { status: 'success', data: {} }
      })

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.userName).toBe('Usuario')
    })
  })
})