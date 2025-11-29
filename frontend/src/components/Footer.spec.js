import { mount } from '@vue/test-utils'
import Footer from './Footer.vue'

describe('Footer', () => {
  it('should mount correctly', () => {
    const wrapper = mount(Footer)
    expect(wrapper.exists()).toBe(true)
  })
})