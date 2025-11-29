import { mount } from '@vue/test-utils'
import PotreroCard from './PotreroCard.vue'

describe('PotreroCard', () => {
  it('should mount correctly', () => {
    const wrapper = mount(PotreroCard)
    expect(wrapper.exists()).toBe(true)
  })
})