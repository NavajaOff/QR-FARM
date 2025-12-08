import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest'
import Login from './Login.vue'
import authService from '../../../src/services/authService'
import Swal from 'sweetalert2'

// Mock de authService
vi.mock('../../../src/services/authService', () => ({
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
    fire: vi.fn()
  }
}))

// Mock de sessionStorage
const mockSessionStorage = {
  setItem: vi.fn(),
  getItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn()
}
Object.defineProperty(window, 'sessionStorage', {
  value: mockSessionStorage
})

const createDeferred = () => {
  let resolveFn
  let rejectFn
  const promise = new Promise((resolve, reject) => {
    resolveFn = resolve
    rejectFn = reject
  })
  return {
    promise,
    resolve: (value) => resolveFn(value),
    reject: (reason) => rejectFn(reason)
  }
}

describe('Login.vue', () => {
  let router
  let wrapper

  beforeEach(() => {
    // Mock de location
    globalThis.location = {
      pathname: '/',
      search: '',
      hash: ''
    }

    // Crear router mock
    router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/login', component: { template: '<div>Login</div>' } },
        { path: '/admin/dashboard', component: { template: '<div>Admin Dashboard</div>' } },
        { path: '/user/inicio', component: { template: '<div>User Inicio</div>' } }
      ]
    })

    // Reset mocks
    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const mountComponent = () => {
    wrapper = mount(Login, {
      global: {
        plugins: [router],
        stubs: {
          'router-link': {
            template: '<a><slot /></a>'
          }
        }
      }
    })
    return wrapper
  }

  describe('Component Rendering', () => {
    it('should mount correctly', () => {
      const wrapper = mountComponent()
      expect(wrapper.exists()).toBe(true)
    })

    it('should render the login form', () => {
      const wrapper = mountComponent()
      expect(wrapper.find('form').exists()).toBe(true)
      expect(wrapper.find('input[type="email"]').exists()).toBe(true)
      expect(wrapper.find('input[type="password"]').exists()).toBe(true)
      expect(wrapper.find('button[type="submit"]').exists()).toBe(true)
    })

    it('should render navbar with correct elements', () => {
      const wrapper = mountComponent()
      const navbar = wrapper.find('.navbar')
      expect(navbar.exists()).toBe(true)
      expect(navbar.text()).toContain('QR FARM')
    })

    it('should display initial state correctly', () => {
      const wrapper = mountComponent()
      expect(wrapper.vm.email).toBe('')
      expect(wrapper.vm.password).toBe('')
      expect(wrapper.vm.error).toBe('')
      expect(wrapper.vm.loading).toBe(false)
    })
  })

  describe('Form Validation', () => {
    it('should validate empty fields', async () => {
      const wrapper = mountComponent()

      // Simular envío del formulario sin datos
      await wrapper.find('form').trigger('submit.prevent')

      expect(wrapper.vm.error).toBe('Por favor completa todos los campos')
      expect(authService.login).not.toHaveBeenCalled()
    })

    it('should validate email field only', async () => {
      const wrapper = mountComponent()

      // Solo email, sin password
      await wrapper.find('input[type="email"]').setValue('test@example.com')
      await wrapper.find('form').trigger('submit.prevent')

      expect(wrapper.vm.error).toBe('Por favor completa todos los campos')
      expect(authService.login).not.toHaveBeenCalled()
    })

    it('should validate password field only', async () => {
      const wrapper = mountComponent()

      // Solo password, sin email
      await wrapper.find('input[type="password"]').setValue('password123')
      await wrapper.find('form').trigger('submit.prevent')

      expect(wrapper.vm.error).toBe('Por favor completa todos los campos')
      expect(authService.login).not.toHaveBeenCalled()
    })

    it('should pass validation with both fields filled', async () => {
      const wrapper = mountComponent()

      // Ambos campos llenos
      await wrapper.find('input[type="email"]').setValue('test@example.com')
      await wrapper.find('input[type="password"]').setValue('password123')

      // Mock successful login
      authService.login.mockResolvedValue({ success: true })

      await wrapper.find('form').trigger('submit.prevent')

      expect(wrapper.vm.error).toBe('')
      expect(authService.login).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123'
      })
    })
  })

  describe('Successful Login Flow', () => {
    beforeEach(() => {
      authService.getRedirectPath.mockReturnValue('/admin/dashboard')
      authService.getRole.mockReturnValue('admin')
      authService.isAdmin.mockReturnValue(true)
    })

    it('should handle successful login', async () => {
      const wrapper = mountComponent()

      // Llenar formulario
      wrapper.vm.email = 'admin@example.com'
      wrapper.vm.password = 'password123'

      const loginDeferred = createDeferred()
      authService.login.mockImplementation(() => loginDeferred.promise)

      await wrapper.find('form').trigger('submit.prevent')
      await wrapper.vm.$nextTick()

      // Verificar que se muestra loading
      expect(wrapper.vm.loading).toBe(true)

      loginDeferred.resolve({ success: true })
      await loginDeferred.promise
      await wrapper.vm.$nextTick()
      await router.isReady()

      // Verificar que se guardaron las credenciales
      expect(mockSessionStorage.setItem).toHaveBeenCalledWith('lastLoginEmail', 'admin@example.com')
      expect(mockSessionStorage.setItem).toHaveBeenCalledWith('lastLoginPassword', 'password123')

      // Verificar que se mostró el Swal de éxito
      expect(Swal.fire).toHaveBeenCalledWith({
        icon: 'success',
        title: '¡Bienvenido!',
        text: 'Inicio de sesión exitoso',
        timer: 1500,
        showConfirmButton: false
      })

      // Verificar redirección
      expect(router.currentRoute.value.path).toBe('/admin/dashboard')
    })

    it('should handle sessionStorage errors gracefully', async () => {
      const wrapper = mountComponent()

      // Mock sessionStorage error
      mockSessionStorage.setItem.mockImplementation(() => {
        throw new Error('Storage quota exceeded')
      })

      await wrapper.find('input[type="email"]').setValue('admin@example.com')
      await wrapper.find('input[type="password"]').setValue('password123')

      authService.login.mockResolvedValue({ success: true })

      // Spy on console.warn
      const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})

      await wrapper.find('form').trigger('submit.prevent')
      await new Promise(resolve => setTimeout(resolve, 0))

      // Verificar que se mostró la advertencia
      expect(consoleSpy).toHaveBeenCalledWith(
        'No se pudieron guardar las credenciales en sessionStorage',
        expect.any(Error)
      )

      consoleSpy.mockRestore()
    })

    it('should handle router navigation errors', async () => {
      const wrapper = mountComponent()

      // Mock router.push to throw error
      const routerPushSpy = vi.spyOn(router, 'push').mockRejectedValue(new Error('Navigation failed'))

      await wrapper.find('input[type="email"]').setValue('admin@example.com')
      await wrapper.find('input[type="password"]').setValue('password123')

      authService.login.mockResolvedValue({ success: true })

      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

      await wrapper.find('form').trigger('submit.prevent')
      await new Promise(resolve => setTimeout(resolve, 0))

      // Verificar que se intentó la redirección alternativa
      expect(routerPushSpy).toHaveBeenCalledWith('/admin/dashboard')
      expect(routerPushSpy).toHaveBeenCalledWith('/admin/dashboard') // fallback

      consoleSpy.mockRestore()
      routerPushSpy.mockRestore()
    })
  })

  describe('Error Handling', () => {
    it('should handle login failure with message', async () => {
      const wrapper = mountComponent()

      await wrapper.find('input[type="email"]').setValue('wrong@example.com')
      await wrapper.find('input[type="password"]').setValue('wrongpassword')

      authService.login.mockResolvedValue({
        success: false,
        message: 'Credenciales incorrectas'
      })

      await wrapper.find('form').trigger('submit.prevent')
      await new Promise(resolve => setTimeout(resolve, 0))

      expect(wrapper.vm.error).toBe('Credenciales incorrectas')
      expect(Swal.fire).toHaveBeenCalledWith({
        icon: 'error',
        title: 'Error de autenticación',
        text: 'Credenciales incorrectas',
        confirmButtonText: 'Intentar de nuevo'
      })
    })

    it('should handle 401 error', async () => {
      const wrapper = mountComponent()

      const mockError = {
        response: {
          status: 401,
          data: { message: 'Unauthorized' }
        }
      }

      authService.login.mockRejectedValue(mockError)

      await wrapper.find('input[type="email"]').setValue('test@example.com')
      await wrapper.find('input[type="password"]').setValue('password')

      await wrapper.find('form').trigger('submit.prevent')
      await new Promise(resolve => setTimeout(resolve, 0))

      expect(wrapper.vm.error).toBe('Credenciales incorrectas')
      expect(Swal.fire).toHaveBeenCalledWith({
        icon: 'error',
        title: 'Error de conexión',
        text: 'Credenciales incorrectas',
        confirmButtonText: 'Aceptar'
      })
    })

    it('should handle 500 server error', async () => {
      const wrapper = mountComponent()

      const mockError = {
        response: {
          status: 500,
          data: { message: 'Internal Server Error' }
        }
      }

      authService.login.mockRejectedValue(mockError)

      await wrapper.find('input[type="email"]').setValue('test@example.com')
      await wrapper.find('input[type="password"]').setValue('password')

      await wrapper.find('form').trigger('submit.prevent')
      await new Promise(resolve => setTimeout(resolve, 0))

      expect(wrapper.vm.error).toBe('Error interno del servidor')
    })

    it('should handle network error', async () => {
      const wrapper = mountComponent()

      const mockError = {
        request: {},
        message: 'Network Error'
      }

      authService.login.mockRejectedValue(mockError)

      await wrapper.find('input[type="email"]').setValue('test@example.com')
      await wrapper.find('input[type="password"]').setValue('password')

      await wrapper.find('form').trigger('submit.prevent')
      await new Promise(resolve => setTimeout(resolve, 0))

      expect(wrapper.vm.error).toBe('No se pudo conectar al servidor. Verifica tu conexión a internet.')
    })

    it('should handle unknown server error', async () => {
      const wrapper = mountComponent()

      const mockError = {
        response: {
          status: 418,
          data: { message: 'I\'m a teapot' }
        }
      }

      authService.login.mockRejectedValue(mockError)

      await wrapper.find('input[type="email"]').setValue('test@example.com')
      await wrapper.find('input[type="password"]').setValue('password')

      await wrapper.find('form').trigger('submit.prevent')
      await new Promise(resolve => setTimeout(resolve, 0))

      expect(wrapper.vm.error).toBe('I\'m a teapot')
    })

    it('should handle generic error', async () => {
      const wrapper = mountComponent()

      authService.login.mockRejectedValue(new Error('Generic error'))

      await wrapper.find('input[type="email"]').setValue('test@example.com')
      await wrapper.find('input[type="password"]').setValue('password')

      await wrapper.find('form').trigger('submit.prevent')
      await new Promise(resolve => setTimeout(resolve, 0))

      expect(wrapper.vm.error).toBe('Error al conectar con el servidor')
    })
  })

  describe('Loading States', () => {
    it('should show loading state during login', async () => {
      const wrapper = mountComponent()

      wrapper.vm.email = 'test@example.com'
      wrapper.vm.password = 'password'

      // Mock login que toma tiempo
      authService.login.mockImplementation(() => new Promise(resolve => {
        setTimeout(() => resolve({ success: true }), 100)
      }))

      await wrapper.find('form').trigger('submit.prevent')
      await wrapper.vm.$nextTick()

      // Verificar estado de loading
      expect(wrapper.vm.loading).toBe(true)
      expect(wrapper.find('button[type="submit"]').attributes('disabled')).toBeDefined()
      expect(wrapper.text()).toContain('Iniciando...')

      // Esperar a que termine
      await new Promise(resolve => setTimeout(resolve, 150))

      expect(wrapper.vm.loading).toBe(false)
    })

    it('should reset loading state on error', async () => {
      const wrapper = mountComponent()

      wrapper.vm.email = 'test@example.com'
      wrapper.vm.password = 'password'

      const loginDeferred = createDeferred()
      authService.login.mockImplementation(() => loginDeferred.promise)

      await wrapper.find('form').trigger('submit.prevent')
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.loading).toBe(true)

      loginDeferred.reject(new Error('Login failed'))
      await loginDeferred.promise.catch(() => {})
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.loading).toBe(false)
    })
  })

  describe('UI Elements', () => {
    it('should show error message in alert', async () => {
      const wrapper = mountComponent()

      wrapper.vm.error = 'Test error message'

      await wrapper.vm.$nextTick()

      const alert = wrapper.find('.alert-danger')
      expect(alert.exists()).toBe(true)
      expect(alert.text()).toBe('Test error message')
    })

    it('should not show error alert when no error', () => {
      const wrapper = mountComponent()

      const alert = wrapper.find('.alert-danger')
      expect(alert.exists()).toBe(false)
    })

    it('should render image with correct alt text', () => {
      const wrapper = mountComponent()

      const img = wrapper.find('img')
      expect(img.exists()).toBe(true)
      expect(img.attributes('alt')).toBe('Grupo de vacas')
    })

    it('should have required attributes on form inputs', () => {
      const wrapper = mountComponent()

      const emailInput = wrapper.find('input[type="email"]')
      const passwordInput = wrapper.find('input[type="password"]')

      expect(emailInput.attributes('required')).toBeDefined()
      expect(passwordInput.attributes('required')).toBeDefined()
    })
  })

  describe('Component Lifecycle', () => {
    it('should unmount without errors', () => {
      const wrapper = mountComponent()
      expect(() => wrapper.unmount()).not.toThrow()
    })

    it('should handle reactive updates', async () => {
      const wrapper = mountComponent()

      wrapper.vm.email = 'test@example.com'
      wrapper.vm.password = 'password123'
      wrapper.vm.loading = true

      await wrapper.vm.$nextTick()

      expect(wrapper.find('input[type="email"]').element.value).toBe('test@example.com')
      expect(wrapper.find('input[type="password"]').element.value).toBe('password123')
      expect(wrapper.text()).toContain('Iniciando...')
    })
  })
})