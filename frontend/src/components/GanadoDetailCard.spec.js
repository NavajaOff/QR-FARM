import { mount } from '@vue/test-utils'
import GanadoDetailCard from './GanadoDetailCard.vue'

describe('GanadoDetailCard', () => {
  it('should mount correctly', () => {
    const wrapper = mount(GanadoDetailCard)
    expect(wrapper.exists()).toBe(true)
  })
})