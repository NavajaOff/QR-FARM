import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { beforeEach, afterEach, vi, describe, it, expect } from 'vitest'
import PerfilUsuario from './PerfilUsuario.vue'
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

describe('PerfilUsuario.vue', () => {
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
        { path: '/user/perfil', component: { template: '<div>Profile</div>' }, name: 'PerfilUsuario' }
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
    authService.getRole.mockReturnValue('usuario')
    authAPI.getProfile.mockResolvedValue({
      data: {
        status: 'success',
        data: {
          nombre_completo: 'Juan Pérez',
          email: 'juan@example.com',
          telefono: '123456789',
          fecha_creacion: '2023-01-15T10:00:00Z'
        }
      }
    })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = (options = {}) => {
    return mount(PerfilUsuario, {
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

  describe('Template Rendering', () => {
    it('should render the component with container-fluid (line 2)', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const container = wrapper.find('.container-fluid')
      expect(container.exists()).toBe(true)
      expect(container.classes()).toContain('py-4')
    })

    it('should render the component', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(wrapper.find('h2').text()).toContain('Mi Perfil')
    })

    it('should render save button (line 35)', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      // Set mostrarResumen to false to show the form
      wrapper.vm.mostrarResumen = false
      await wrapper.vm.$nextTick()

      const saveButton = wrapper.find('form').find('button[type="submit"]')
      expect(saveButton.exists()).toBe(true)
      expect(saveButton.text()).toContain('Guardar cambios')
      expect(saveButton.attributes('disabled')).toBeUndefined()
    })

    it('should disable save button when loading', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.mostrarResumen = false
      wrapper.vm.loading = true
      await wrapper.vm.$nextTick()

      const saveButton = wrapper.find('form').find('button[type="submit"]')
      expect(saveButton.attributes('disabled')).toBeDefined()
    })

    it('should render cancel button (line 39)', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.mostrarResumen = false
      await wrapper.vm.$nextTick()

      const cancelButton = wrapper.find('form').find('button[type="button"]')
      expect(cancelButton.exists()).toBe(true)
      expect(cancelButton.text()).toContain('Cancelar')
    })

    it('should call cancelarEdicion when cancel button is clicked', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.mostrarResumen = false
      await wrapper.vm.$nextTick()

      const cancelarEdicionSpy = vi.spyOn(wrapper.vm, 'cancelarEdicion')
      const cancelButton = wrapper.find('form').find('button[type="button"]')

      await cancelButton.trigger('click')

      expect(cancelarEdicionSpy).toHaveBeenCalled()
    })

    it('should disable cancel button when loading', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.mostrarResumen = false
      wrapper.vm.loading = true
      await wrapper.vm.$nextTick()

      const cancelButton = wrapper.find('form').find('button[type="button"]')
      expect(cancelButton.attributes('disabled')).toBeDefined()
    })

    it('should show message alert when message exists (line 44)', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.mostrarResumen = false
      wrapper.vm.message = 'Test message'
      wrapper.vm.messageType = 'success'
      await wrapper.vm.$nextTick()

      const alert = wrapper.find('.alert')
      expect(alert.exists()).toBe(true)
      expect(alert.text()).toBe('Test message')
      expect(alert.classes()).toContain('alert-success')
    })

    it('should show error alert when messageType is error', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.mostrarResumen = false
      wrapper.vm.message = 'Error message'
      wrapper.vm.messageType = 'error'
      await wrapper.vm.$nextTick()

      const alert = wrapper.find('.alert')
      expect(alert.exists()).toBe(true)
      expect(alert.text()).toBe('Error message')
      expect(alert.classes()).toContain('alert-danger')
    })

    it('should not show alert when message is empty', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.mostrarResumen = false
      wrapper.vm.message = ''
      await wrapper.vm.$nextTick()

      const alert = wrapper.find('.alert')
      expect(alert.exists()).toBe(false)
    })

    it('should show summary view with profile data (lines 53, 57, 61)', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      // Wait for fetchProfile to complete
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      wrapper.vm.mostrarResumen = true
      wrapper.vm.profile = {
        nombreCompleto: 'Juan Pérez',
        email: 'juan@example.com',
        telefono: '123456789',
        fechaCreacion: '2023-01-15T10:00:00Z'
      }
      await wrapper.vm.$nextTick()

      const summaryView = wrapper.find('.card-body')
      expect(summaryView.exists()).toBe(true)
      expect(summaryView.text()).toContain('Juan Pérez')
      expect(summaryView.text()).toContain('juan@example.com')
      expect(summaryView.text()).toContain('123456789')
    })

    it('should show "Sin información" when profile data is empty (lines 53, 57, 61)', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.mostrarResumen = true
      wrapper.vm.profile = {
        nombreCompleto: '',
        email: '',
        telefono: '',
        fechaCreacion: ''
      }
      await wrapper.vm.$nextTick()

      const summaryView = wrapper.find('.card-body')
      expect(summaryView.exists()).toBe(true)
      expect(summaryView.text()).toContain('Sin información')
    })

    it('should show spinner when loading', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.mostrarResumen = false
      wrapper.vm.loading = true
      await wrapper.vm.$nextTick()

      const form = wrapper.find('form')
      const spinner = form.find('.spinner-border')
      expect(spinner.exists()).toBe(true)
    })
  })

  describe('Form Interactions', () => {
    it('should call updateProfile when form is submitted', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.mostrarResumen = false
      await wrapper.vm.$nextTick()

      authAPI.updateProfile.mockResolvedValue({
        data: { status: 'success', message: 'Perfil actualizado exitosamente' }
      })
      authAPI.getProfile.mockResolvedValue({
        data: { status: 'success', data: {} }
      })

      const updateProfileSpy = vi.spyOn(wrapper.vm, 'updateProfile')
      const form = wrapper.find('form')

      await form.trigger('submit')

      expect(updateProfileSpy).toHaveBeenCalled()
    })

    it('should update profile and show success message', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.mostrarResumen = false
      wrapper.vm.profile = {
        nombreCompleto: 'Juan Pérez',
        email: 'juan@example.com',
        telefono: '123456789'
      }
      await wrapper.vm.$nextTick()

      authAPI.updateProfile.mockResolvedValue({
        data: { status: 'success', message: 'Perfil actualizado exitosamente' }
      })
      authAPI.getProfile.mockResolvedValue({
        data: { status: 'success', data: {} }
      })

      const form = wrapper.find('form')
      await form.trigger('submit')
      
      // Wait for async operations
      await wrapper.vm.$nextTick()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.message).toBe('Perfil actualizado exitosamente')
      expect(wrapper.vm.messageType).toBe('success')
      
      wrapper.vm.mostrarResumen = false
      await wrapper.vm.$nextTick()
      
      const alert = wrapper.find('.alert')
      expect(alert.exists()).toBe(true)
      expect(alert.text()).toBe('Perfil actualizado exitosamente')
    })

    it('should toggle between form and summary view', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      // Initially should show summary
      wrapper.vm.mostrarResumen = true
      await wrapper.vm.$nextTick()

      let summaryView = wrapper.find('.card-body')
      expect(summaryView.text()).not.toContain('Guardar cambios')

      // Click button to show form
      const updateButton = wrapper.find('button.btn-primary')
      await updateButton.trigger('click')
      await wrapper.vm.$nextTick()

      wrapper.vm.mostrarResumen = false
      await wrapper.vm.$nextTick()

      const form = wrapper.find('form')
      expect(form.exists()).toBe(true)
    })
  })

  describe('Summary View', () => {
    it('should display profile information in summary', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.mostrarResumen = true
      wrapper.vm.profile = {
        nombreCompleto: 'Juan Pérez',
        email: 'juan@example.com',
        telefono: '123456789',
        fechaCreacion: '2023-01-15T10:00:00Z'
      }
      await wrapper.vm.$nextTick()

      const summaryText = wrapper.text()
      expect(summaryText).toContain('Juan Pérez')
      expect(summaryText).toContain('juan@example.com')
      expect(summaryText).toContain('123456789')
    })

    it('should display user role', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('usuario')
    })

    it('should display formatted date', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.profile.fechaCreacion = '2023-01-15T10:00:00Z'
      await wrapper.vm.$nextTick()

      const dateText = wrapper.text()
      expect(dateText).toMatch(/\d{1,2}\/\d{1,2}\/\d{4}/)
    })
  })

  describe('Input Binding', () => {
    it('should bind nombreCompleto input', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.mostrarResumen = false
      await wrapper.vm.$nextTick()

      const nombreInput = wrapper.find('input[type="text"]')
      expect(nombreInput.exists()).toBe(true)
      await nombreInput.setValue('Pedro García')
      expect(wrapper.vm.profile.nombreCompleto).toBe('Pedro García')
    })

    it('should bind email input', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.mostrarResumen = false
      await wrapper.vm.$nextTick()

      const emailInput = wrapper.find('input[type="email"]')
      expect(emailInput.exists()).toBe(true)
      await emailInput.setValue('pedro@example.com')
      expect(wrapper.vm.profile.email).toBe('pedro@example.com')
    })

    it('should bind telefono input', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.mostrarResumen = false
      await wrapper.vm.$nextTick()

      const telefonoInput = wrapper.find('input[type="tel"]')
      expect(telefonoInput.exists()).toBe(true)
      await telefonoInput.setValue('987654321')
      expect(wrapper.vm.profile.telefono).toBe('987654321')
    })
  })
})

