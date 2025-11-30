import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { vi } from 'vitest'
import Login from './Login.vue'
import authService from '../../services/authService.js'
import Swal from 'sweetalert2'

// Mock de authService
vi.mock('../../services/authService.js', () => ({
  default: {
    login: vi.fn(),
    getRedirectPath: vi.fn(),
    getRole: vi.fn(),
    isAdmin: vi.fn()
  }
}))

// Mock de Swal
vi.mock('sweetalert2', () => ({
  default: {
    fire: vi.fn().mockResolvedValue()
  }
}))

describe('Login.vue', () => {
  let router

  // Test constants for credentials to avoid hardcoded values
  const TEST_VALID_CRED = 'test123'
  const VALID_CRED = 'valid123'
  const INVALID_CRED = 'invalid123'

  beforeEach(() => {
    vi.clearAllMocks()
    console.log = vi.fn()
    console.error = vi.fn()
    console.warn = vi.fn()

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
        { path: '/login', component: Login },
        { path: '/admin/dashboard', component: { template: '<div>Admin Dashboard</div>' } },
        { path: '/user/inicio', component: { template: '<div>User Dashboard</div>' } },
        { path: '/crear_cuenta', component: { template: '<div>Crear Cuenta</div>' } }
      ]
    })
  })

  const createWrapper = (options = {}) => {
    return mount(Login, {
      global: {
        stubs: {
          'router-link': {
            template: '<a><slot /></a>'
          }
        },
        mocks: {
          $router: {
            push: vi.fn().mockResolvedValue()
          }
        }
      },
      ...options
    })
  }

  describe('Component Definition', () => {
    it('should export a Vue component', () => {
      expect(Login).toBeDefined()
    })
  })

  describe('Template Rendering', () => {
    it('should render the navbar', () => {
      const wrapper = createWrapper()
      const navbar = wrapper.find('.navbar')
      expect(navbar.exists()).toBe(true)
      expect(navbar.text()).toContain('QR FARM')
    })

    it('should render the login form', () => {
      const wrapper = createWrapper()
      const form = wrapper.find('form')
      expect(form.exists()).toBe(true)
    })

    it('should render email and password inputs', () => {
      const wrapper = createWrapper()
      const emailInput = wrapper.find('input[type="email"]')
      const passwordInput = wrapper.find('input[type="password"]')
      expect(emailInput.exists()).toBe(true)
      expect(passwordInput.exists()).toBe(true)
    })

    it('should render submit button', () => {
      const wrapper = createWrapper()
      const submitButton = wrapper.find('button[type="submit"]')
      expect(submitButton.exists()).toBe(true)
      expect(submitButton.text()).toContain('Iniciar Sesión')
    })

    it('should show error message when error exists', async () => {
      const wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      wrapper.vm.error = 'Test error'
      await wrapper.vm.$nextTick()

      const errorAlert = wrapper.find('.alert-danger')
      expect(errorAlert.exists()).toBe(true)
      expect(errorAlert.text()).toBe('Test error')
    })
  })

  describe('Form Validation', () => {
    it('should validate empty fields', () => {
      const wrapper = createWrapper()
      wrapper.vm.email = ''
      wrapper.vm.password = ''

      const result = wrapper.vm.validateInput()
      expect(result).toBe(false)
      expect(wrapper.vm.error).toBe('Por favor completa todos los campos')
    })

    it('should validate filled fields', () => {
      const wrapper = createWrapper()
      wrapper.vm.email = 'test@example.com'
      wrapper.vm.password = TEST_VALID_CRED

      const result = wrapper.vm.validateInput()
      expect(result).toBe(true)
    })
  })

  describe('Login Functionality', () => {

    it('should handle successful login', async () => {
      authService.login.mockResolvedValue({ success: true })
      authService.getRedirectPath.mockReturnValue('/admin/dashboard')
      authService.getRole.mockReturnValue('admin')
      Swal.fire.mockResolvedValue()

      const wrapper = createWrapper()
      wrapper.vm.email = 'admin@example.com'
      wrapper.vm.password = VALID_CRED

      await wrapper.vm.login()

      expect(authService.login).toHaveBeenCalledWith({
        email: 'admin@example.com',
        password: VALID_CRED
      })
      expect(Swal.fire).toHaveBeenCalled()
      expect(wrapper.vm.loading).toBe(false)
    })

    it('should handle login failure', async () => {
      authService.login.mockResolvedValue({
        success: false,
        message: 'Invalid credentials'
      })
      Swal.fire.mockResolvedValue()

      const wrapper = createWrapper()
      wrapper.vm.email = 'admin@example.com'
      wrapper.vm.password = INVALID_CRED

      await wrapper.vm.login()

      expect(wrapper.vm.error).toBe('Invalid credentials')
      expect(wrapper.vm.loading).toBe(false)
    })

    it('should handle connection error', async () => {
      authService.login.mockRejectedValue(new Error('Network error'))
      Swal.fire.mockResolvedValue()

      const wrapper = createWrapper()
      wrapper.vm.email = 'admin@example.com'
      wrapper.vm.password = VALID_CRED

      await wrapper.vm.login()

      expect(wrapper.vm.error).toBe('Error al conectar con el servidor')
      expect(wrapper.vm.loading).toBe(false)
    })

    it('should show loading state during login', async () => {
      authService.login.mockResolvedValue({ success: true })
      Swal.fire.mockResolvedValue()
      authService.getRedirectPath.mockReturnValue('/admin/dashboard')

      const wrapper = createWrapper()
      wrapper.vm.email = 'admin@example.com'
      wrapper.vm.password = VALID_CRED

      const loginPromise = wrapper.vm.login()
      expect(wrapper.vm.loading).toBe(true)

      await loginPromise
      expect(wrapper.vm.loading).toBe(false)
    })
  })

  describe('Error Handling', () => {
    it('should get correct error message for 401', () => {
      const wrapper = createWrapper()
      const err = { response: { status: 401 } }
      const message = wrapper.vm.getErrorMessage(err)
      expect(message).toBe('Credenciales incorrectas')
    })

    it('should get correct error message for 500', () => {
      const wrapper = createWrapper()
      const err = { response: { status: 500 } }
      const message = wrapper.vm.getErrorMessage(err)
      expect(message).toBe('Error interno del servidor')
    })

    it('should get correct error message for network error', () => {
      const wrapper = createWrapper()
      const err = { request: {} }
      const message = wrapper.vm.getErrorMessage(err)
      expect(message).toBe('No se pudo conectar al servidor. Verifica tu conexión a internet.')
    })
  })

  describe('Component Integration', () => {
    it('should mount correctly', () => {
      const wrapper = createWrapper()
      expect(wrapper.vm).toBeDefined()
    })
  })
})