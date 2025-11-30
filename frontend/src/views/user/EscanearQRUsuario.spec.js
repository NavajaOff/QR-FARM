import { mount } from '@vue/test-utils'
import EscanearQRUsuario from './EscanearQRUsuario.vue'
import QrScanner from '../../components/QrScanner.vue'

describe('EscanearQRUsuario', () => {
  it('should mount correctly', () => {
    const wrapper = mount(EscanearQRUsuario, {
      global: {
        components: {
          QrScanner
        }
      }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('should handle resource loaded', () => {
    const wrapper = mount(EscanearQRUsuario, {
      global: {
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
    const wrapper = mount(EscanearQRUsuario, {
      global: {
        components: {
          QrScanner
        }
      }
    })
    const vm = wrapper.vm
    vm.handleScannerError('Test error')
    // Just check it doesn't throw
  })

  it('should forward action', () => {
    const wrapper = mount(EscanearQRUsuario, {
      global: {
        components: {
          QrScanner
        }
      }
    })
    const vm = wrapper.vm
    vm.lastResourceId = '123'
    vm.forwardAction('test-action')
    // Just check it doesn't throw
  })
})