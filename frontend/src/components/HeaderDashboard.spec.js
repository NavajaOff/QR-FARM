import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { vi } from 'vitest'
import HeaderDashboard from './HeaderDashboard.vue'
import authService from '../services/authService.js'

// Mock de authService
vi.mock('../services/authService.js', () => ({
  default: {
    getUser: vi.fn(),
    getRole: vi.fn(),
    logout: vi.fn()
  }
}))

describe('HeaderDashboard', () => {
  let router

  beforeEach(() => {
    // Mock de location para createMemoryHistory
    globalThis.location = {
      pathname: '/',
      search: '',
      hash: ''
    }

    // Crear router mock
    router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/user/perfil', component: { template: '<div>Perfil</div>' } },
        { path: '/user/qr', component: { template: '<div>QR</div>' } }
      ]
    })
  })

  it('should mount correctly', () => {
    const wrapper = mount(HeaderDashboard, {
      global: {
        plugins: [router],
        stubs: ['router-link']
      }
    })
    expect(wrapper.exists()).toBe(true)
  })
})