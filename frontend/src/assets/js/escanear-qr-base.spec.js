import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { beforeEach, vi } from 'vitest'
import { escanearQRBase } from './escanear-qr-base.js'
import authService from '../../services/authService.js'

// Mock de authService
vi.mock('../../services/authService.js', () => ({
  default: {
    isAuthenticated: vi.fn(),
    isAdmin: vi.fn(),
    getUser: vi.fn(),
    logout: vi.fn()
  }
}))

// Mock de Swal
globalThis.Swal = {
  fire: vi.fn(),
  showLoading: vi.fn()
}

describe('escanear-qr-base.js', () => {
  let router
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    console.error = vi.fn()
    console.log = vi.fn()

    // Mock de location para createMemoryHistory
        globalThis.location = {
          pathname: '/',
          search: '',
          hash: ''
        }

    // Crear router mock con createMemoryHistory
    router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/login', component: { template: '<div>Login</div>' } }
      ]
    })
  })

  const createWrapper = (options = {}) => {
    const component = {
      ...escanearQRBase,
      name: 'TestComponent',
      template: '<div><input ref="fileInput" type="file" /></div>',
      ...options
    }

    return mount(component, {
      global: {
        plugins: [router],
        mocks: {
          $router: router
        }
      }
    })
  }

  describe('Data Function', () => {
    it('should return default data when no config', () => {
      const mockVm = { $options: {} }
      const data = escanearQRBase.data.call(mockVm)
      expect(data.isScanning).toBe(false)
      expect(data.userName).toBe('Usuario')
      expect(data.recentScans).toEqual([])
      expect(data.estadisticas).toBeNull()
    })

    it('should use config data when provided', () => {
      const mockVm = {
        $options: {
          escanearQRConfig: {
            defaultUserName: 'TestUser',
            recentScans: [{ id: 1 }],
            estadisticas: { total: 10 }
          }
        }
      }
      const data = escanearQRBase.data.call(mockVm)
      expect(data.userName).toBe('TestUser')
      expect(data.recentScans).toEqual([{ id: 1 }])
      expect(data.estadisticas).toEqual({ total: 10 })
    })
  })

  describe('Mounted Hook', () => {
    it('should redirect to login if not authorized', async () => {
      authService.isAuthenticated.mockReturnValue(false)
      const pushSpy = vi.spyOn(router, 'push')

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(pushSpy).toHaveBeenCalledWith('/login')
    })

    it('should not redirect if authorized', async () => {
      authService.isAuthenticated.mockReturnValue(true)
      const pushSpy = vi.spyOn(router, 'push')

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(pushSpy).not.toHaveBeenCalled()
    })

    it('should call onAuthorized if provided', async () => {
      authService.isAuthenticated.mockReturnValue(true)
      const onAuthorizedSpy = vi.fn()

      wrapper = createWrapper({
        escanearQRConfig: {
          authorize: () => true,
          onAuthorized: onAuthorizedSpy
        }
      })
      await wrapper.vm.$nextTick()

      expect(onAuthorizedSpy).toHaveBeenCalledWith(authService)
    })
  })

  describe('iniciarEscaneo Method', () => {
    beforeEach(() => {
      vi.useFakeTimers()
    })

    afterEach(() => {
      vi.useRealTimers()
    })

    it('should set isScanning to true and then false', async () => {
      wrapper = createWrapper()
      const promise = wrapper.vm.iniciarEscaneo()

      expect(wrapper.vm.isScanning).toBe(true)

      await vi.advanceTimersByTime(2000)
      await promise

      expect(wrapper.vm.isScanning).toBe(false)
    })

    it('should show success Swal with default color', async () => {
      wrapper = createWrapper()
      const promise = wrapper.vm.iniciarEscaneo()

      await vi.advanceTimersByTime(2000)
      await promise

      expect(Swal.fire).toHaveBeenCalledWith({
        title: 'Escaneo completado',
        text: 'Código QR detectado correctamente',
        icon: 'success',
        confirmButtonColor: '#28a745'
      })
    })

    it('should show success Swal with config color', async () => {
      wrapper = createWrapper({
        escanearQRConfig: {
          successButtonColor: '#007bff'
        }
      })
      const promise = wrapper.vm.iniciarEscaneo()

      await vi.advanceTimersByTime(2000)
      await promise

      expect(Swal.fire).toHaveBeenCalledWith({
        title: 'Escaneo completado',
        text: 'Código QR detectado correctamente',
        icon: 'success',
        confirmButtonColor: '#007bff'
      })
    })

    it('should use alert if Swal is undefined', async () => {
      const originalSwal = globalThis.Swal
      globalThis.Swal = undefined
      const alertSpy = vi.spyOn(globalThis, 'alert').mockImplementation(() => {})

      wrapper = createWrapper()
      const promise = wrapper.vm.iniciarEscaneo()

      await vi.advanceTimersByTime(2000)
      await promise

      expect(alertSpy).toHaveBeenCalledWith('Escaneo completado - Código QR detectado')

      globalThis.Swal = originalSwal
    })

    it('should handle errors gracefully', async () => {
      // Mock setTimeout to throw an error
      const originalSetTimeout = globalThis.setTimeout
      globalThis.setTimeout = vi.fn(() => {
        throw new Error('Test error')
      })

      wrapper = createWrapper()
      await wrapper.vm.iniciarEscaneo()

      expect(console.error).toHaveBeenCalledWith('Error en escaneo:', expect.any(Error))

      globalThis.setTimeout = originalSetTimeout
    })
  })

  describe('subirImagen Method', () => {
    it('should click file input if ref exists', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      const clickSpy = vi.fn()
      Object.defineProperty(wrapper.vm.$refs, 'fileInput', {
        value: { click: clickSpy },
        writable: true
      })

      wrapper.vm.subirImagen()

      expect(clickSpy).toHaveBeenCalled()
    })

    it('should do nothing if fileInput ref does not exist', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      Object.defineProperty(wrapper.vm.$refs, 'fileInput', {
        value: undefined,
        writable: true
      })

      expect(() => wrapper.vm.subirImagen()).not.toThrow()
    })
  })

  describe('handleFileUpload Method', () => {
    beforeEach(() => {
      vi.useFakeTimers()
    })

    afterEach(() => {
      vi.useRealTimers()
    })

    it('should do nothing if no file', () => {
      wrapper = createWrapper()
      wrapper.vm.handleFileUpload({ target: { files: [] } })

      expect(console.log).not.toHaveBeenCalled()
    })

    it('should process file and show Swal', async () => {
      const file = new File(['test'], 'test.png', { type: 'image/png' })
      wrapper = createWrapper()
      wrapper.vm.handleFileUpload({ target: { files: [file] } })

      expect(console.log).toHaveBeenCalledWith('Imagen subida:', 'test.png')

      expect(Swal.fire).toHaveBeenCalledWith({
        title: 'Procesando imagen',
        text: 'Analizando código QR...',
        allowOutsideClick: false,
        didOpen: expect.any(Function)
      })

      await vi.advanceTimersByTime(2000)

      expect(Swal.fire).toHaveBeenCalledWith({
        title: 'Imagen procesada',
        text: 'Código QR encontrado en la imagen',
        icon: 'success',
        confirmButtonColor: '#28a745'
      })
    })

    it('should use config success color', async () => {
      const file = new File(['test'], 'test.png', { type: 'image/png' })
      wrapper = createWrapper({
        escanearQRConfig: {
          successButtonColor: '#007bff'
        }
      })
      wrapper.vm.handleFileUpload({ target: { files: [file] } })

      await vi.advanceTimersByTime(2000)

      expect(Swal.fire).toHaveBeenCalledWith({
        title: 'Imagen procesada',
        text: 'Código QR encontrado en la imagen',
        icon: 'success',
        confirmButtonColor: '#007bff'
      })
    })
  })

  describe('Component Integration', () => {
    it('should mount correctly', () => {
      wrapper = createWrapper()
      expect(wrapper.vm).toBeDefined()
      expect(wrapper.vm.isScanning).toBe(false)
    })
  })
})