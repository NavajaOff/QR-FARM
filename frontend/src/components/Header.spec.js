import { mount } from '@vue/test-utils'
import Header from './Header.vue'

describe('Header', () => {
  it('should mount correctly', () => {
    const wrapper = mount(Header)
    expect(wrapper.exists()).toBe(true)
  })
})