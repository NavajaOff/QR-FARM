import { mount } from '@vue/test-utils'
import QrScanner from './QrScanner.vue'

describe('QrScanner', () => {
  it('should mount correctly', () => {
    const wrapper = mount(QrScanner)
    expect(wrapper.exists()).toBe(true)
  })
})