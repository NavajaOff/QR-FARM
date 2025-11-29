import { mount } from '@vue/test-utils'
import TenantSelector from './TenantSelector.vue'

describe('TenantSelector', () => {
  it('should mount correctly', () => {
    const wrapper = mount(TenantSelector)
    expect(wrapper.exists()).toBe(true)
  })
})