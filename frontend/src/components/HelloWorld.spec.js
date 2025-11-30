import { mount } from '@vue/test-utils'
import HelloWorld from './HelloWorld.vue'

describe('HelloWorld', () => {
  it('should mount correctly', () => {
    const wrapper = mount(HelloWorld, {
      props: {
        msg: 'Hello World'
      }
    })
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.text()).toContain('Hello World')
  })

  it('should increment count on button click', async () => {
    const wrapper = mount(HelloWorld, {
      props: {
        msg: 'Test'
      }
    })
    const button = wrapper.find('button')
    await button.trigger('click')
    expect(wrapper.text()).toContain('count is 1')
  })
})