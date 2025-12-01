import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { beforeEach, afterEach, vi, describe, it, expect } from 'vitest'
import PerfilAdmin from './PerfilAdmin.vue'
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

describe('PerfilAdmin.vue', () => {
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

    // Setup default mocks
    authService.isAuthenticated.mockReturnValue(true)
    authService.isAdmin.mockReturnValue(true)
    authService.getUser.mockReturnValue({
      persona: {
        primer_nombre: 'Juan',
        segundo_nombre: 'Carlos',
        primer_apellido: 'Pérez',
        segundo_apellido: 'Gómez',
        email: 'juan@example.com',
        telefono: '123456789',
        fecha_creacion: '2023-01-15T10:00:00Z'
      }
    })
    authService.getRole.mockReturnValue('admin')
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = (options = {}) => {
    return mount(PerfilAdmin, {
      global: {
        plugins: [router],
        mocks: {
          $router: router
        }
      },
      ...options
    })
  }

  describe('Template Rendering', () => {
    it('should render the component', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(wrapper.find('h2').text()).toContain('Mi Perfil')
      expect(wrapper.find('#admin-primer-nombre').exists()).toBe(true)
      expect(wrapper.find('#admin-email').exists()).toBe(true)
    })

    it('should render update profile button (line 47)', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const updateButton = wrapper.find('form').find('button[type="submit"]')
      expect(updateButton.exists()).toBe(true)
      expect(updateButton.text()).toContain('Actualizar Perfil')
      expect(updateButton.attributes('disabled')).toBeUndefined()
    })

    it('should disable update button when loading', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.loading = true
      await wrapper.vm.$nextTick()

      const updateButton = wrapper.find('form').find('button[type="submit"]')
      expect(updateButton.attributes('disabled')).toBeDefined()
    })

    it('should show message alert when message exists (line 53)', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

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

      wrapper.vm.message = ''
      await wrapper.vm.$nextTick()

      const alert = wrapper.find('.alert')
      expect(alert.exists()).toBe(false)
    })

    it('should render change password button (line 104)', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const passwordForm = wrapper.findAll('form').at(1)
      expect(passwordForm.exists()).toBe(true)
      const passwordButton = passwordForm.find('button[type="submit"]')
      expect(passwordButton.exists()).toBe(true)
      expect(passwordButton.text()).toContain('Cambiar Contraseña')
      expect(passwordButton.attributes('disabled')).toBeUndefined()
    })

    it('should show spinner when loading', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.loading = true
      await wrapper.vm.$nextTick()

      const updateForm = wrapper.findAll('form').at(0)
      const spinner = updateForm.find('.spinner-border')
      expect(spinner.exists()).toBe(true)
    })

    it('should show spinner when passwordLoading', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.passwordLoading = true
      await wrapper.vm.$nextTick()

      const passwordForm = wrapper.findAll('form').at(1)
      const spinner = passwordForm.find('.spinner-border')
      expect(spinner.exists()).toBe(true)
    })

    it('should disable password button when passwordLoading is true', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.passwordLoading = true
      await wrapper.vm.$nextTick()

      const passwordForm = wrapper.findAll('form').at(1)
      const passwordButton = passwordForm.find('button[type="submit"]')
      expect(passwordButton.attributes('disabled')).toBeDefined()
    })
  })

  describe('Form Interactions', () => {
    beforeEach(() => {
      vi.useFakeTimers()
    })

    afterEach(() => {
      vi.useRealTimers()
    })

    it('should call updateProfile when update form is submitted', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const updateProfileSpy = vi.spyOn(wrapper.vm, 'updateProfile')
      const updateForm = wrapper.findAll('form').at(0)

      await updateForm.trigger('submit')

      expect(updateProfileSpy).toHaveBeenCalled()
    })

    it('should call changePassword when password form is submitted', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.passwordData = {
        current: 'old',
        new: 'new',
        confirm: 'new'
      }
      await wrapper.vm.$nextTick()

      const changePasswordSpy = vi.spyOn(wrapper.vm, 'changePassword')
      const passwordForm = wrapper.findAll('form').at(1)

      await passwordForm.trigger('submit')

      expect(changePasswordSpy).toHaveBeenCalled()
    })

    it('should update profile and show success message', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const updateForm = wrapper.findAll('form').at(0)
      const promise = updateForm.trigger('submit')
      await vi.advanceTimersByTime(1000)
      await promise
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.message).toBe('Perfil actualizado exitosamente')
      expect(wrapper.vm.messageType).toBe('success')
      
      const alert = wrapper.find('.alert')
      expect(alert.exists()).toBe(true)
      expect(alert.text()).toBe('Perfil actualizado exitosamente')
    })

    it('should change password and show success message', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.passwordData = {
        current: 'old',
        new: 'new',
        confirm: 'new'
      }
      await wrapper.vm.$nextTick()

      const passwordForm = wrapper.findAll('form').at(1)
      const promise = passwordForm.trigger('submit')
      await vi.advanceTimersByTime(1000)
      await promise
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.message).toBe('Contraseña cambiada exitosamente')
      expect(wrapper.vm.messageType).toBe('success')
      
      const alert = wrapper.find('.alert')
      expect(alert.exists()).toBe(true)
      expect(alert.text()).toBe('Contraseña cambiada exitosamente')
    })

    it('should show error when passwords do not match', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.passwordData = {
        current: 'old',
        new: 'new',
        confirm: 'different'
      }
      await wrapper.vm.$nextTick()

      const passwordForm = wrapper.findAll('form').at(1)
      await passwordForm.trigger('submit')
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.message).toBe('Las contraseñas no coinciden')
      expect(wrapper.vm.messageType).toBe('error')
      
      const alert = wrapper.find('.alert')
      expect(alert.exists()).toBe(true)
      expect(alert.text()).toBe('Las contraseñas no coinciden')
    })
  })

  describe('User Information Display', () => {
    it('should display user role', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('admin')
    })

    it('should display formatted date', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const dateText = wrapper.text()
      expect(dateText).toMatch(/\d{1,2}\/\d{1,2}\/\d{4}/)
    })

    it('should display user profile data in form inputs', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const primerNombreInput = wrapper.find('#admin-primer-nombre')
      expect(primerNombreInput.element.value).toBe('Juan')
      
      const emailInput = wrapper.find('#admin-email')
      expect(emailInput.element.value).toBe('juan@example.com')
    })

    it('should render and bind all profile form inputs (lines 22, 26, 30, 34, 38)', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      // Line 22: primer nombre input
      const primerNombreInput = wrapper.find('#admin-primer-nombre')
      expect(primerNombreInput.exists()).toBe(true)
      expect(primerNombreInput.attributes('type')).toBe('text')
      await primerNombreInput.setValue('Pedro')
      expect(wrapper.vm.profile.primerNombre).toBe('Pedro')

      // Line 26: segundo nombre input
      const segundoNombreInput = wrapper.find('#admin-segundo-nombre')
      expect(segundoNombreInput.exists()).toBe(true)
      expect(segundoNombreInput.attributes('type')).toBe('text')
      await segundoNombreInput.setValue('Luis')
      expect(wrapper.vm.profile.segundoNombre).toBe('Luis')

      // Line 30: primer apellido input
      const primerApellidoInput = wrapper.find('#admin-primer-apellido')
      expect(primerApellidoInput.exists()).toBe(true)
      expect(primerApellidoInput.attributes('type')).toBe('text')
      await primerApellidoInput.setValue('García')
      expect(wrapper.vm.profile.primerApellido).toBe('García')

      // Line 34: segundo apellido input
      const segundoApellidoInput = wrapper.find('#admin-segundo-apellido')
      expect(segundoApellidoInput.exists()).toBe(true)
      expect(segundoApellidoInput.attributes('type')).toBe('text')
      await segundoApellidoInput.setValue('López')
      expect(wrapper.vm.profile.segundoApellido).toBe('López')

      // Line 38: email input (readonly)
      const emailInput = wrapper.find('#admin-email')
      expect(emailInput.exists()).toBe(true)
      expect(emailInput.attributes('type')).toBe('email')
      expect(emailInput.attributes('readonly')).toBeDefined()
      expect(emailInput.attributes('required')).toBeDefined()
      // Verify v-model binding even though readonly
      expect(emailInput.element.value).toBe('juan@example.com')
    })

    it('should properly handle email input readonly attribute (line 38)', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      // Find email input by its ID to ensure line 38 is executed
      const emailInput = wrapper.find('input#admin-email')
      expect(emailInput.exists()).toBe(true)
      
      // Email should be readonly
      expect(emailInput.attributes('readonly')).toBeDefined()
      expect(emailInput.attributes('required')).toBeDefined()
      expect(emailInput.attributes('type')).toBe('email')
      
      // Verify initial value from user data
      expect(emailInput.element.value).toBe('juan@example.com')
      expect(wrapper.vm.profile.email).toBe('juan@example.com')
      
      // Verify the input is rendered in the form
      const form = wrapper.find('form')
      expect(form.find('#admin-email').exists()).toBe(true)
    })

    it('should render icon in header (line 8)', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const icon = wrapper.find('.fa-user-edit')
      expect(icon.exists()).toBe(true)
    })

    it('should render and bind telefono input (line 42)', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const telefonoInput = wrapper.find('#admin-telefono')
      expect(telefonoInput.exists()).toBe(true)
      expect(telefonoInput.element.value).toBe('123456789')
      
      // Test v-model binding
      await telefonoInput.setValue('987654321')
      expect(wrapper.vm.profile.telefono).toBe('987654321')
    })

    it('should render and bind password inputs (lines 94, 98, 102)', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const currentPasswordInput = wrapper.find('#admin-password-current')
      expect(currentPasswordInput.exists()).toBe(true)
      expect(currentPasswordInput.attributes('type')).toBe('password')
      
      const newPasswordInput = wrapper.find('#admin-password-new')
      expect(newPasswordInput.exists()).toBe(true)
      expect(newPasswordInput.attributes('type')).toBe('password')
      
      const confirmPasswordInput = wrapper.find('#admin-password-confirm')
      expect(confirmPasswordInput.exists()).toBe(true)
      expect(confirmPasswordInput.attributes('type')).toBe('password')

      // Test v-model binding
      await currentPasswordInput.setValue('current123')
      await newPasswordInput.setValue('new123')
      await confirmPasswordInput.setValue('new123')
      
      expect(wrapper.vm.passwordData.current).toBe('current123')
      expect(wrapper.vm.passwordData.new).toBe('new123')
      expect(wrapper.vm.passwordData.confirm).toBe('new123')
    })
  })
})

