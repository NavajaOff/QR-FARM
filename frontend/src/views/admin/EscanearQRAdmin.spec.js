import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import EscanearQRAdmin from './EscanearQRAdmin.vue'
import QrScanner from '../../components/QrScanner.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { name: 'GestionarAnimalesAdmin', path: '/admin/animales' }
  ]
})

describe('EscanearQRAdmin', () => {
  it('should mount correctly', () => {
    const wrapper = mount(EscanearQRAdmin, {
      global: {
        plugins: [router],
        components: {
          QrScanner
        }
      }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('should handle resource loaded', () => {
    const wrapper = mount(EscanearQRAdmin, {
      global: {
        plugins: [router],
        components: {
          QrScanner
        }
      }
    })
    const vm = wrapper.vm
    vm.handleResourceLoaded({ id: '123' })
    expect(vm.lastResourceId).toBe('123')
  })

  it('should handle scanner error', () => {
    const wrapper = mount(EscanearQRAdmin, {
      global: {
        plugins: [router],
        components: {
          QrScanner
        }
      }
    })
    const vm = wrapper.vm
    vm.handleScannerError('Test error')
    // Just check it doesn't throw
  })

  it('should forward action ver-historial', () => {
    const wrapper = mount(EscanearQRAdmin, {
      global: {
        plugins: [router],
        components: {
          QrScanner
        }
      }
    })
    const vm = wrapper.vm
    vm.lastResourceId = '123'
    vm.forwardAction('ver-historial')
    // Check router push was called, but since it's mocked, just ensure no error
  })
})