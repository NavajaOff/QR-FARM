import { mount } from '@vue/test-utils'
import App from './App.vue'

describe('App', () => {
  it('should mount correctly', () => {
    const wrapper = mount(App)
    expect(wrapper.exists()).toBe(true)
  })
})