import { mount } from '@vue/test-utils'
import HeaderDashboard from './HeaderDashboard.vue'

describe('HeaderDashboard', () => {
  it('should mount correctly', () => {
    const wrapper = mount(HeaderDashboard)
    expect(wrapper.exists()).toBe(true)
  })
})