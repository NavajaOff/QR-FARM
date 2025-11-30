import { mount } from '@vue/test-utils'
import Contacto from './Contacto.vue'

describe('Contacto', () => {
  it('should mount correctly', () => {
    const wrapper = mount(Contacto)
    expect(wrapper.exists()).toBe(true)
  })
})