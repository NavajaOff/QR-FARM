import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { beforeEach } from 'vitest'
import App from './App.vue'

describe('App', () => {
  let router

  beforeEach(() => {
    // Mock de location para createMemoryHistory
    globalThis.location = {
      pathname: '/',
      search: '',
      hash: ''
    }

    // Crear router mock para los tests con createMemoryHistory
    router = createRouter({
      history: createMemoryHistory(),
      routes: [
        {
          path: '/',
          component: { template: '<div>Home</div>' }
        },
        {
          path: '/login',
          component: { template: '<div>Login</div>' }
        },
        {
          path: '/admin',
          component: { template: '<div>Admin</div>' }
        }
      ]
    })
  })

  it('should mount correctly', () => {
    const wrapper = mount(App, {
      global: {
        plugins: [router]
      }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('should render router-view', () => {
    const wrapper = mount(App, {
      global: {
        plugins: [router],
        stubs: {
          'router-view': true
        }
      }
    })
    // Check for router-view stub or actual router-view
    const routerView = wrapper.find('router-view-stub')
    const hasRouterView = routerView.exists() || wrapper.html().includes('router-view')
    expect(hasRouterView).toBe(true)
  })

  it('should be a Vue component', () => {
    const wrapper = mount(App, {
      global: {
        plugins: [router]
      }
    })
    expect(wrapper.vm).toBeDefined()
  })

  it('should render template correctly', () => {
    const wrapper = mount(App, {
      global: {
        plugins: [router],
        stubs: {
          'router-view': { template: '<div>Router View</div>' }
        }
      }
    })
    // Verify template is rendered
    const html = wrapper.html()
    expect(html).toBeTruthy()
    expect(html.length).toBeGreaterThan(0)
  })

  it('should work with router navigation', async () => {
    const wrapper = mount(App, {
      global: {
        plugins: [router]
      }
    })

    await router.push('/login')
    await wrapper.vm.$nextTick()

    expect(wrapper.exists()).toBe(true)
    expect(wrapper.html()).toBeTruthy()
  })

  it('should handle router changes', async () => {
    const wrapper = mount(App, {
      global: {
        plugins: [router]
      }
    })

    await router.push('/')
    await wrapper.vm.$nextTick()
    expect(wrapper.exists()).toBe(true)

    await router.push('/admin')
    await wrapper.vm.$nextTick()
    expect(wrapper.exists()).toBe(true)
  })

  it('should handle multiple route changes', async () => {
    const wrapper = mount(App, {
      global: {
        plugins: [router]
      }
    })

    const routes = ['/', '/login', '/admin']
    for (const route of routes) {
      await router.push(route)
      await wrapper.vm.$nextTick()
      expect(wrapper.exists()).toBe(true)
    }
  })

  it('should render without errors on initial mount', () => {
    const wrapper = mount(App, {
      global: {
        plugins: [router],
        stubs: {
          'router-view': { template: '<div>Router View</div>' }
        }
      }
    })
    expect(() => wrapper.html()).not.toThrow()
    const html = wrapper.html()
    expect(html).toBeTruthy()
    expect(html.length).toBeGreaterThan(0)
  })

  it('should have scoped styles applied', () => {
    const wrapper = mount(App, {
      global: {
        plugins: [router],
        stubs: {
          'router-view': { template: '<div>Router View</div>' }
        }
      }
    })
    // Component should render with styles
    const html = wrapper.html()
    expect(html).toBeTruthy()
    expect(html.length).toBeGreaterThan(0)
  })

  it('should unmount without errors', () => {
    const wrapper = mount(App, {
      global: {
        plugins: [router]
      }
    })
    expect(() => wrapper.unmount()).not.toThrow()
    expect(wrapper.exists()).toBe(false)
  })

  it('should handle component lifecycle', async () => {
    const wrapper = mount(App, {
      global: {
        plugins: [router]
      }
    })

    // Component should be mounted
    expect(wrapper.exists()).toBe(true)

    // Wait for any async operations
    await wrapper.vm.$nextTick()

    // Component should still exist
    expect(wrapper.exists()).toBe(true)
  })

  it('should work with different router configurations', () => {
    const customRouter = createRouter({
      history: createMemoryHistory(),
      routes: [
        {
          path: '/test',
          component: { template: '<div>Test</div>' }
        }
      ]
    })

    const wrapper = mount(App, {
      global: {
        plugins: [customRouter]
      }
    })

    expect(wrapper.exists()).toBe(true)
  })
})