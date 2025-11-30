import { mount } from '@vue/test-utils'
import CrearCuenta from './CrearCuenta.vue'

describe('CrearCuenta', () => {
  it('should mount correctly', () => {
    const wrapper = mount(CrearCuenta)
    expect(wrapper.exists()).toBe(true)
  })

  it('should render the form', () => {
    const wrapper = mount(CrearCuenta)
    const form = wrapper.find('form')
    expect(form.exists()).toBe(true)
  })

  it('should have required inputs', () => {
    const wrapper = mount(CrearCuenta)
    const inputs = wrapper.findAll('input[required]')
    expect(inputs.length).toBeGreaterThan(0)
  })
})