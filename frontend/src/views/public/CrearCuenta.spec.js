import { mount } from '@vue/test-utils'
import { vi } from 'vitest'
import CrearCuenta from './CrearCuenta.vue'

// Mock de authAPI
vi.mock('../../services/api.js', () => ({
  authAPI: {
    register: vi.fn()
  }
}))

describe('CrearCuenta', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()
    wrapper = mount(CrearCuenta, {
      global: {
        mocks: {
          $router: {
            push: vi.fn()
          }
        }
      }
    })
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('should mount correctly', () => {
    expect(wrapper.exists()).toBe(true)
  })

  it('should render the form', () => {
    const form = wrapper.find('form')
    expect(form.exists()).toBe(true)
  })

  it('should have required inputs', () => {
    const inputs = wrapper.findAll('input[required]')
    expect(inputs.length).toBeGreaterThan(0)
  })

  it('should handle successful registration', async () => {
    const { authAPI } = await import('../../services/api.js')
    authAPI.register.mockResolvedValue({
      data: { status: 'success' }
    })

    // Fill form
    await wrapper.find('#primerNombre').setValue('Juan')
    await wrapper.find('#primerApellido').setValue('Perez')
    await wrapper.find('#email').setValue('juan@example.com')
    await wrapper.find('#password').setValue('password123')
    await wrapper.find('#telefono').setValue('123456789')
    await wrapper.find('#terminos').setChecked(true)

    // Submit form
    await wrapper.find('form').trigger('submit.prevent')

    expect(authAPI.register).toHaveBeenCalledWith({
      primer_nombre: 'Juan',
      segundo_nombre: null,
      primer_apellido: 'Perez',
      segundo_apellido: null,
      email: 'juan@example.com',
      telefono: '123456789',
      password: 'password123'
    })

    expect(wrapper.vm.success).toBe('Cuenta creada exitosamente. Redirigiendo al login...')

    // Advance timers to trigger the redirect
    vi.runAllTimers()

    expect(wrapper.vm.$router.push).toHaveBeenCalledWith('/login')
  })

  it('should handle validation error', async () => {
    // Submit form without filling required fields
    await wrapper.find('form').trigger('submit.prevent')

    expect(wrapper.vm.error).toBe('Por favor complete todos los campos requeridos')
    expect(wrapper.vm.loading).toBe(false)
  })

  it('should handle API error', async () => {
    const { authAPI } = await import('../../services/api.js')
    authAPI.register.mockRejectedValue({
      response: { data: { message: 'Email already exists' } }
    })

    // Fill form
    await wrapper.find('#primerNombre').setValue('Juan')
    await wrapper.find('#primerApellido').setValue('Perez')
    await wrapper.find('#email').setValue('juan@example.com')
    await wrapper.find('#password').setValue('password123')
    await wrapper.find('#terminos').setChecked(true)

    // Submit form
    await wrapper.find('form').trigger('submit.prevent')

    expect(wrapper.vm.error).toBe('Email already exists')
    expect(wrapper.vm.loading).toBe(false)
  })

  it('should handle API error without response data', async () => {
    const { authAPI } = await import('../../services/api.js')
    authAPI.register.mockRejectedValue(new Error('Network error'))

    // Fill form
    await wrapper.find('#primerNombre').setValue('Juan')
    await wrapper.find('#primerApellido').setValue('Perez')
    await wrapper.find('#email').setValue('juan@example.com')
    await wrapper.find('#password').setValue('password123')
    await wrapper.find('#terminos').setChecked(true)

    // Submit form
    await wrapper.find('form').trigger('submit.prevent')

    expect(wrapper.vm.error).toBe('Network error')
    expect(wrapper.vm.loading).toBe(false)
  })

  it('should handle API success but wrong status', async () => {
    const { authAPI } = await import('../../services/api.js')
    authAPI.register.mockResolvedValue({
      data: { status: 'error', message: 'Registration failed' }
    })

    // Fill form
    await wrapper.find('#primerNombre').setValue('Juan')
    await wrapper.find('#primerApellido').setValue('Perez')
    await wrapper.find('#email').setValue('juan@example.com')
    await wrapper.find('#password').setValue('password123')
    await wrapper.find('#terminos').setChecked(true)

    // Submit form
    await wrapper.find('form').trigger('submit.prevent')

    expect(wrapper.vm.error).toBe('Registration failed')
    expect(wrapper.vm.loading).toBe(false)
  })

  it('should set loading state during submission', async () => {
    const { authAPI } = await import('../../services/api.js')
    authAPI.register.mockResolvedValue({
      data: { status: 'success' }
    })

    // Fill form
    await wrapper.find('#primerNombre').setValue('Juan')
    await wrapper.find('#primerApellido').setValue('Perez')
    await wrapper.find('#email').setValue('juan@example.com')
    await wrapper.find('#password').setValue('password123')
    await wrapper.find('#terminos').setChecked(true)

    // Submit form
    const submitPromise = wrapper.find('form').trigger('submit.prevent')

    expect(wrapper.vm.loading).toBe(true)

    await submitPromise

    expect(wrapper.vm.loading).toBe(false)
  })
})