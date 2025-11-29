import { mount } from '@vue/test-utils'
import PotreroModal from './PotreroModal.vue'

describe('PotreroModal', () => {
  it('should mount correctly', () => {
    const wrapper = mount(PotreroModal)
    expect(wrapper.exists()).toBe(true)
  })
})