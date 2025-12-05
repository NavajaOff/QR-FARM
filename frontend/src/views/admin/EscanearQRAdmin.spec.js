import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { beforeEach, vi, describe, it, expect } from 'vitest'
import EscanearQRAdmin from './EscanearQRAdmin.vue'
import QrScanner from '../../components/QrScanner.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { name: 'GestionarAnimalesAdmin', path: '/admin/animales' }
  ]
})

// Mock console.debug
const mockConsoleDebug = vi.spyOn(console, 'debug').mockImplementation(() => {})

describe('EscanearQRAdmin', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    mockConsoleDebug.mockClear()
  })

  describe('Component mounting', () => {
    it('should mount correctly', () => {
      wrapper = mount(EscanearQRAdmin, {
        global: {
          plugins: [router],
          components: {
            QrScanner
          }
        }
      })
      expect(wrapper.exists()).toBe(true)
    })

    it('should render QrScanner component', () => {
      wrapper = mount(EscanearQRAdmin, {
        global: {
          plugins: [router],
          components: {
            QrScanner
          }
        }
      })
      const qrScanner = wrapper.findComponent(QrScanner)
      expect(qrScanner.exists()).toBe(true)
    })

    it('should pass correct props to QrScanner', () => {
      wrapper = mount(EscanearQRAdmin, {
        global: {
          plugins: [router],
          components: {
            QrScanner
          }
        }
      })
      const qrScanner = wrapper.findComponent(QrScanner)
      expect(qrScanner.props('resourceEndpoint')).toBe('/animales/qr/{id}')
    })
  })

  describe('handleResourceLoaded', () => {
    it('should update lastResourceId when resource is loaded', async () => {
      wrapper = mount(EscanearQRAdmin, {
        global: {
          plugins: [router],
          components: {
            QrScanner
          }
        }
      })
      
      const resource = { id: '123', nombre: 'Vaca Test' }
      const qrScanner = wrapper.findComponent(QrScanner)
      await qrScanner.vm.$emit('resource-loaded', resource)
      
      expect(wrapper.vm.lastResourceId).toBe('123')
      expect(mockConsoleDebug).toHaveBeenCalledWith('[ADMIN QR] Recurso cargado', resource)
    })

    it('should handle resource with different id', async () => {
      wrapper = mount(EscanearQRAdmin, {
        global: {
          plugins: [router],
          components: {
            QrScanner
          }
        }
      })
      
      const resource = { id: '456', nombre: 'Otra Vaca' }
      const qrScanner = wrapper.findComponent(QrScanner)
      await qrScanner.vm.$emit('resource-loaded', resource)
      
      expect(wrapper.vm.lastResourceId).toBe('456')
    })

    it('should handle empty resource id', async () => {
      wrapper = mount(EscanearQRAdmin, {
        global: {
          plugins: [router],
          components: {
            QrScanner
          }
        }
      })
      
      const resource = { id: '', nombre: 'Sin ID' }
      const qrScanner = wrapper.findComponent(QrScanner)
      await qrScanner.vm.$emit('resource-loaded', resource)
      
      expect(wrapper.vm.lastResourceId).toBe('')
    })
  })

  describe('handleScannerError', () => {
    it('should log error message', async () => {
      wrapper = mount(EscanearQRAdmin, {
        global: {
          plugins: [router],
          components: {
            QrScanner
          }
        }
      })
      
      const errorMessage = 'Test error message'
      const qrScanner = wrapper.findComponent(QrScanner)
      await qrScanner.vm.$emit('error', errorMessage)
      
      expect(mockConsoleDebug).toHaveBeenCalledWith('[ADMIN QR] Error recibido', errorMessage)
    })

    it('should handle different error messages', async () => {
      wrapper = mount(EscanearQRAdmin, {
        global: {
          plugins: [router],
          components: {
            QrScanner
          }
        }
      })
      
      const errorMessage = 'Network error'
      const qrScanner = wrapper.findComponent(QrScanner)
      await qrScanner.vm.$emit('error', errorMessage)
      
      expect(mockConsoleDebug).toHaveBeenCalledWith('[ADMIN QR] Error recibido', errorMessage)
    })
  })

  describe('forwardAction', () => {
    beforeEach(() => {
      vi.spyOn(router, 'push').mockResolvedValue()
    })

    it('should navigate to GestionarAnimalesAdmin with seleccionado query for ver-historial', async () => {
      wrapper = mount(EscanearQRAdmin, {
        global: {
          plugins: [router],
          components: {
            QrScanner
          }
        }
      })
      
      wrapper.vm.lastResourceId = '123'
      const qrScanner = wrapper.findComponent(QrScanner)
      await qrScanner.vm.$emit('action', 'ver-historial')
      
      expect(router.push).toHaveBeenCalledWith({
        name: 'GestionarAnimalesAdmin',
        query: { seleccionado: '123' }
      })
    })

    it('should navigate to GestionarAnimalesAdmin with editar query for editar', async () => {
      wrapper = mount(EscanearQRAdmin, {
        global: {
          plugins: [router],
          components: {
            QrScanner
          }
        }
      })
      
      wrapper.vm.lastResourceId = '456'
      const qrScanner = wrapper.findComponent(QrScanner)
      await qrScanner.vm.$emit('action', 'editar')
      
      expect(router.push).toHaveBeenCalledWith({
        name: 'GestionarAnimalesAdmin',
        query: { editar: '456' }
      })
    })

    it('should log descargar-ficha action', async () => {
      wrapper = mount(EscanearQRAdmin, {
        global: {
          plugins: [router],
          components: {
            QrScanner
          }
        }
      })
      
      wrapper.vm.lastResourceId = '789'
      const qrScanner = wrapper.findComponent(QrScanner)
      await qrScanner.vm.$emit('action', 'descargar-ficha')
      
      expect(mockConsoleDebug).toHaveBeenCalledWith('[ADMIN QR] Solicitud de descarga de ficha', '789')
      expect(router.push).not.toHaveBeenCalled()
    })

    it('should log unknown action', async () => {
      wrapper = mount(EscanearQRAdmin, {
        global: {
          plugins: [router],
          components: {
            QrScanner
          }
        }
      })
      
      wrapper.vm.lastResourceId = '999'
      const qrScanner = wrapper.findComponent(QrScanner)
      await qrScanner.vm.$emit('action', 'unknown-action')
      
      expect(mockConsoleDebug).toHaveBeenCalledWith('[ADMIN QR] Acción emitida', 'unknown-action')
      expect(router.push).not.toHaveBeenCalled()
    })

    it('should not navigate if lastResourceId is empty for ver-historial', async () => {
      wrapper = mount(EscanearQRAdmin, {
        global: {
          plugins: [router],
          components: {
            QrScanner
          }
        }
      })
      
      wrapper.vm.lastResourceId = ''
      const qrScanner = wrapper.findComponent(QrScanner)
      await qrScanner.vm.$emit('action', 'ver-historial')
      
      expect(router.push).not.toHaveBeenCalled()
    })

    it('should not navigate if lastResourceId is empty for editar', async () => {
      wrapper = mount(EscanearQRAdmin, {
        global: {
          plugins: [router],
          components: {
            QrScanner
          }
        }
      })
      
      wrapper.vm.lastResourceId = ''
      const qrScanner = wrapper.findComponent(QrScanner)
      await qrScanner.vm.$emit('action', 'editar')
      
      expect(router.push).not.toHaveBeenCalled()
    })

    it('should handle multiple actions in sequence', async () => {
      wrapper = mount(EscanearQRAdmin, {
        global: {
          plugins: [router],
          components: {
            QrScanner
          }
        }
      })
      
      const qrScanner = wrapper.findComponent(QrScanner)
      
      // First action
      wrapper.vm.lastResourceId = '111'
      await qrScanner.vm.$emit('action', 'ver-historial')
      expect(router.push).toHaveBeenCalledWith({
        name: 'GestionarAnimalesAdmin',
        query: { seleccionado: '111' }
      })
      
      // Second action
      wrapper.vm.lastResourceId = '222'
      await qrScanner.vm.$emit('action', 'editar')
      expect(router.push).toHaveBeenCalledWith({
        name: 'GestionarAnimalesAdmin',
        query: { editar: '222' }
      })
    })
  })

  describe('Event handling from QrScanner', () => {
    it('should handle all events from QrScanner', async () => {
      wrapper = mount(EscanearQRAdmin, {
        global: {
          plugins: [router],
          components: {
            QrScanner
          }
        }
      })
      
      const qrScanner = wrapper.findComponent(QrScanner)
      
      // Test resource-loaded
      await qrScanner.vm.$emit('resource-loaded', { id: '123' })
      expect(wrapper.vm.lastResourceId).toBe('123')
      
      // Test error
      await qrScanner.vm.$emit('error', 'Test error')
      expect(mockConsoleDebug).toHaveBeenCalledWith('[ADMIN QR] Error recibido', 'Test error')
      
      // Test action
      vi.spyOn(router, 'push').mockResolvedValue()
      await qrScanner.vm.$emit('action', 'ver-historial')
      expect(router.push).toHaveBeenCalled()
    })
  })
})
