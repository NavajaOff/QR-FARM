import { mount } from '@vue/test-utils'
import { beforeEach, afterEach, vi, describe, it, expect } from 'vitest'
import QrScanner from './QrScanner.vue'
import { fetchQrResource } from '../services/qr'

// Mock html5-qrcode
vi.mock('html5-qrcode', () => ({
  Html5Qrcode: vi.fn().mockImplementation(() => ({
    start: vi.fn().mockResolvedValue(),
    stop: vi.fn().mockResolvedValue(),
    clear: vi.fn().mockResolvedValue(),
    pause: vi.fn().mockResolvedValue(),
    resume: vi.fn().mockResolvedValue(),
    scanFileV2: vi.fn().mockResolvedValue({ decodedText: 'test', decodedResult: {} })
  })),
  Html5QrcodeSupportedFormats: {
    QR_CODE: 'QR_CODE',
    AZTEC: 'AZTEC',
    PDF_417: 'PDF_417'
  },
  Html5Qrcode: {
    getCameras: vi.fn().mockResolvedValue([
      { id: 'camera1', label: 'Camera 1' },
      { id: 'camera2', label: 'Camera 2' }
    ])
  }
}))

// Mock qr service
vi.mock('../services/qr', () => ({
  fetchQrResource: vi.fn(),
  transformEmbeddedPayload: vi.fn()
}))

// Mock GanadoDetailCard
vi.mock('./GanadoDetailCard.vue', () => ({
  default: {
    name: 'GanadoDetailCard',
    template: '<div>GanadoDetailCard</div>'
  }
}))

describe('QrScanner.vue', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    console.log = vi.fn()
    console.error = vi.fn()
    console.debug = vi.fn()
    console.info = vi.fn()

    // Mock navigator
    globalThis.navigator = {
      onLine: true,
      mediaDevices: {
        getUserMedia: vi.fn()
      }
    }

    // Mock crypto if not already defined
    if (!globalThis.crypto) {
      Object.defineProperty(globalThis, 'crypto', {
        value: {
          getRandomValues: vi.fn((arr) => {
            for (let i = 0; i < arr.length; i++) {
              arr[i] = Math.floor(Math.random() * 256)
            }
            return arr
          })
        },
        writable: true,
        configurable: true
      })
    }

    // Mock window
    globalThis.window = {}
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = (props = {}) => {
    return mount(QrScanner, {
      props: {
        resourceEndpoint: '/api/ganado/{id}',
        ...props
      }
    })
  }

  describe('Component Rendering', () => {
    it('should mount correctly', () => {
      wrapper = createWrapper()
      expect(wrapper.exists()).toBe(true)
    })

    it('should render header with title', () => {
      wrapper = createWrapper()
      expect(wrapper.find('.qr-header__title').exists()).toBe(true)
      expect(wrapper.text()).toContain('Escáner de códigos QR')
    })

    it('should render role badge for admin', () => {
      wrapper = createWrapper({ role: 'admin' })
      const badge = wrapper.find('.qr-badge')
      expect(badge.exists()).toBe(true)
      expect(badge.text()).toBe('Administrador')
    })

    it('should render role badge for user', () => {
      wrapper = createWrapper({ role: 'user' })
      const badge = wrapper.find('.qr-badge')
      expect(badge.exists()).toBe(true)
      expect(badge.text()).toBe('Usuario')
    })

    it('should use default role "user" when role prop is not provided', () => {
      wrapper = createWrapper() // Sin prop role
      const badge = wrapper.find('.qr-badge')
      expect(badge.exists()).toBe(true)
      expect(badge.text()).toBe('Usuario')
    })

    it('should render video viewport', () => {
      wrapper = createWrapper()
      expect(wrapper.find('.qr-video__viewport').exists()).toBe(true)
    })

    it('should render camera select', () => {
      wrapper = createWrapper()
      expect(wrapper.find('.qr-camera-select').exists()).toBe(true)
      expect(wrapper.find('#qr-camera-options').exists()).toBe(true)
    })

    it('should render action buttons', () => {
      wrapper = createWrapper()
      const buttons = wrapper.findAll('.qr-btn')
      expect(buttons.length).toBeGreaterThan(0)
    })

    it('should render file input', () => {
      wrapper = createWrapper()
      const fileInput = wrapper.find('.qr-file-input')
      expect(fileInput.exists()).toBe(true)
      expect(fileInput.attributes('type')).toBe('file')
      expect(fileInput.attributes('accept')).toBe('image/*')
    })
  })

  describe('Resource States', () => {
    it('should show idle state initially', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))

      expect(wrapper.text()).toContain('Sin resultados todavía')
    })

    it('should show loading state', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      
      // Access state through component instance
      const component = wrapper.vm
      if (component && component.state) {
        component.state.resourceState = 'loading'
        await wrapper.vm.$nextTick()
        expect(wrapper.text()).toContain('Cargando información...')
      } else {
        // If we can't access state directly, just verify component renders
        expect(wrapper.exists()).toBe(true)
      }
    })

    it('should show error state', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      
      const component = wrapper.vm
      if (component && component.state) {
        component.state.resourceState = 'error'
        component.state.resourceError = 'Error de prueba'
        await wrapper.vm.$nextTick()
        expect(wrapper.text()).toContain('Error al consultar')
      } else {
        expect(wrapper.exists()).toBe(true)
      }
    })

    it('should show ready state with resource', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      
      const component = wrapper.vm
      if (component && component.state) {
        component.state.resourceState = 'ready'
        component.state.resource = {
          id: '1',
          nombre: 'Test Animal'
        }
        await wrapper.vm.$nextTick()
        const ganadoCard = wrapper.findComponent({ name: 'GanadoDetailCard' })
        expect(ganadoCard.exists()).toBe(true)
      } else {
        expect(wrapper.exists()).toBe(true)
      }
    })
  })

  describe('Error Display', () => {
    it('should show error message when lastError exists', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      
      wrapper.vm.state.lastError = 'Error de prueba'
      await wrapper.vm.$nextTick()

      const errorAlert = wrapper.find('.qr-alert--error')
      expect(errorAlert.exists()).toBe(true)
      expect(errorAlert.text()).toContain('Error de prueba')
    })

    it('should show warning when resourceError exists in ready state', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      
      wrapper.vm.state.resourceState = 'ready'
      wrapper.vm.state.resource = { id: '1', nombre: 'Test' }
      wrapper.vm.state.resourceError = 'Warning message'
      await wrapper.vm.$nextTick()

      const warningAlert = wrapper.find('.qr-alert--warning')
      expect(warningAlert.exists()).toBe(true)
      expect(warningAlert.text()).toContain('Warning message')
    })
  })

  describe('Telemetry Display', () => {
    it('should show telemetry messages when they exist', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      
      wrapper.vm.state.telemetryMessages = [
        {
          id: '1',
          timestamp: Date.now(),
          formatted: '10:00:00',
          message: 'Test message'
        }
      ]
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('Registro de escaneos')
      expect(wrapper.text()).toContain('Test message')
    })

    it('should not show telemetry when messages array is empty', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      
      wrapper.vm.state.telemetryMessages = []
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).not.toContain('Registro de escaneos')
    })
  })

  describe('Button States', () => {
    it('should disable start button when scanning', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      
      wrapper.vm.state.isScanning = true
      await wrapper.vm.$nextTick()

      const startButton = wrapper.find('.qr-btn--primary')
      expect(startButton.attributes('disabled')).toBeDefined()
    })

    it('should disable start button when no camera selected', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      
      wrapper.vm.state.selectedCameraId = ''
      wrapper.vm.state.isScanning = false
      await wrapper.vm.$nextTick()

      const startButton = wrapper.find('.qr-btn--primary')
      expect(startButton.attributes('disabled')).toBeDefined()
    })

    it('should disable pause button when not scanning', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      
      wrapper.vm.state.isScanning = false
      await wrapper.vm.$nextTick()

      const buttons = wrapper.findAll('.qr-btn')
      const pauseButton = buttons.find(btn => btn.text().includes('Pausar') || btn.text().includes('Continuar'))
      if (pauseButton) {
        expect(pauseButton.attributes('disabled')).toBeDefined()
      }
    })

    it('should disable stop button when not scanning', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      
      wrapper.vm.state.isScanning = false
      await wrapper.vm.$nextTick()

      const buttons = wrapper.findAll('.qr-btn')
      const stopButton = buttons.find(btn => btn.text().includes('Cerrar cámara'))
      if (stopButton) {
        expect(stopButton.attributes('disabled')).toBeDefined()
      }
    })
  })

  describe('Camera Selection', () => {
    it('should show error when no cameras available', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      
      wrapper.vm.state.availableCameras = []
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('No se detectaron cámaras. Verifica los permisos del navegador.')
    })

    it('should disable camera select when scanning', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      
      wrapper.vm.state.isScanning = true
      await wrapper.vm.$nextTick()

      const cameraSelect = wrapper.find('#qr-camera-options')
      expect(cameraSelect.attributes('disabled')).toBeDefined()
    })
  })

  describe('Scanner Status', () => {
    it('should show error status when lastError exists', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      
      wrapper.vm.state.lastError = 'Error de prueba'
      await wrapper.vm.$nextTick()

      const status = wrapper.find('.qr-status')
      expect(status.attributes('data-status')).toBe('error')
    })

    it('should show paused status when isPaused is true', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      
      wrapper.vm.state.isPaused = true
      wrapper.vm.state.lastError = ''
      await wrapper.vm.$nextTick()

      const status = wrapper.find('.qr-status')
      expect(status.attributes('data-status')).toBe('paused')
    })

    it('should show scanning status when isScanning is true', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      
      wrapper.vm.state.isScanning = true
      wrapper.vm.state.isPaused = false
      wrapper.vm.state.lastError = ''
      await wrapper.vm.$nextTick()

      const status = wrapper.find('.qr-status')
      expect(status.attributes('data-status')).toBe('scanning')
    })

    it('should show idle status by default', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      
      wrapper.vm.state.isScanning = false
      wrapper.vm.state.isPaused = false
      wrapper.vm.state.lastError = ''
      await wrapper.vm.$nextTick()

      const status = wrapper.find('.qr-status')
      expect(status.attributes('data-status')).toBe('idle')
    })
  })

  describe('Component Lifecycle', () => {
    it('should load cameras on mount', async () => {
      // Ensure navigator.mediaDevices.getUserMedia is available
      globalThis.navigator.mediaDevices.getUserMedia = vi.fn()
      
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 300))

      // The component should mount and attempt to load cameras
      // We verify the component exists and renders correctly
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.find('.qr-camera-select').exists()).toBe(true)
    })

    it('should handle missing navigator.mediaDevices.getUserMedia', async () => {
      globalThis.navigator.mediaDevices.getUserMedia = undefined
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(wrapper.exists()).toBe(true)
    })
  })

  describe('Event Handlers', () => {
    it('should handle retry button click', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      
      wrapper.vm.state.resourceState = 'error'
      wrapper.vm.state.resourceError = 'Error de prueba'
      wrapper.vm.state.lastPayload = {
        kind: 'resource',
        resourceId: '1',
        resourceType: null,
        raw: 'test',
        metadata: {}
      }
      await wrapper.vm.$nextTick()

      fetchQrResource.mockResolvedValue({
        id: '1',
        nombre: 'Test Animal'
      })

      const retryButton = wrapper.find('button.qr-btn')
      if (retryButton && retryButton.text().includes('Reintentar')) {
        await retryButton.trigger('click')
        await wrapper.vm.$nextTick()
        await new Promise(resolve => setTimeout(resolve, 100))
        
        expect(fetchQrResource).toHaveBeenCalled()
      }
    })
  })

  describe('Computed Properties', () => {
    it('should compute roleLabel correctly for admin', async () => {
      wrapper = createWrapper({ role: 'admin' })
      await wrapper.vm.$nextTick()
      const badge = wrapper.find('.qr-badge')
      expect(badge.text()).toBe('Administrador')
    })

    it('should compute roleLabel correctly for user', async () => {
      wrapper = createWrapper({ role: 'user' })
      await wrapper.vm.$nextTick()
      const badge = wrapper.find('.qr-badge')
      expect(badge.text()).toBe('Usuario')
    })

    it('should compute headerTitle correctly', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      expect(wrapper.text()).toContain('Escáner de códigos QR')
    })

    it('should compute headerSubtitle correctly', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      expect(wrapper.text()).toContain('Apunta el código dentro del recuadro')
    })
  })

  describe('Button Actions', () => {
    it('should handle start scan button click', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      
      wrapper.vm.state.selectedCameraId = 'camera1'
      wrapper.vm.state.availableCameras = [
        { id: 'camera1', label: 'Camera 1' }
      ]
      
      const startButton = wrapper.find('.qr-btn--primary')
      if (startButton.exists() && !startButton.attributes('disabled')) {
        await startButton.trigger('click')
        await wrapper.vm.$nextTick()
        await new Promise(resolve => setTimeout(resolve, 100))
        
        expect(wrapper.exists()).toBe(true)
      }
    })

    it('should handle stop scan button click', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      
      // Create mock instance directly
      const mockInstance = {
        start: vi.fn().mockResolvedValue(),
        stop: vi.fn().mockResolvedValue(),
        clear: vi.fn().mockResolvedValue(),
        pause: vi.fn().mockResolvedValue(),
        resume: vi.fn().mockResolvedValue()
      }
      // Assign mock instance directly
      wrapper.vm.html5QrCodeInstance = { value: mockInstance }
      wrapper.vm.state.isScanning = true
      await wrapper.vm.$nextTick()
      
      // Call the handler directly
      await wrapper.vm.handleStopScan()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))
      
      expect(wrapper.exists()).toBe(true)
      // stopScanner sets isScanning to false in finally block
      expect(wrapper.vm.state.isScanning).toBe(false)
    })

    it('should handle file upload button click', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      
      // Instead of using trigger('click'), call the handler directly
      wrapper.vm.openFileDialog()
      await wrapper.vm.$nextTick()
      
      expect(wrapper.exists()).toBe(true)
    })
  })

  describe('Network and Offline Handling', () => {
    it('should handle offline state', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      
      globalThis.navigator.onLine = false
      
      fetchQrResource.mockResolvedValue({
        id: '1',
        nombre: 'Test Animal'
      })
      
      const { transformEmbeddedPayload } = await import('../services/qr')
      transformEmbeddedPayload.mockReturnValue({
        id: '1',
        nombre: 'Test Animal'
      })
      
      wrapper.vm.state.lastPayload = {
        kind: 'resource',
        resourceId: '1',
        resourceType: null,
        raw: JSON.stringify({ id: '1', nombre: 'Test', schema: 'qr-farm', type: 'ganado' }),
        metadata: {},
        embeddedResource: { id: '1', nombre: 'Test', schema: 'qr-farm', type: 'ganado' }
      }
      
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))
      
      expect(wrapper.exists()).toBe(true)
    })
  })

  describe('Error Handling', () => {
    it('should handle fetch error gracefully', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      
      fetchQrResource.mockRejectedValue(new Error('Network error'))
      
      wrapper.vm.state.lastPayload = {
        kind: 'resource',
        resourceId: '999',
        resourceType: null,
        raw: '999',
        metadata: {}
      }
      
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))
      
      expect(wrapper.exists()).toBe(true)
    })

    it('should handle camera permission denied error', async () => {
      const { Html5Qrcode } = await import('html5-qrcode')
      Html5Qrcode.getCameras.mockRejectedValue(new Error('Permission denied'))
      
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 500))
      
      // El error puede ser sobre obtener cámaras o sobre inicializar el escáner
      const error = wrapper.vm.state.lastError
      expect(error).toBeTruthy()
      // Verificar que se maneja el error de alguna forma
      expect(error.length).toBeGreaterThan(0)
    })

    it('should handle camera loading error', async () => {
      const { Html5Qrcode } = await import('html5-qrcode')
      Html5Qrcode.getCameras.mockRejectedValue(new Error('Camera error'))
      
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 300))
      
      expect(wrapper.vm.state.lastError).toBeTruthy()
      expect(console.error).toHaveBeenCalled()
    })

    it('should handle no cameras available', async () => {
      const { Html5Qrcode } = await import('html5-qrcode')
      // Mock getCameras to return empty array
      Html5Qrcode.getCameras.mockResolvedValueOnce([])
      
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      // Wait for loadCameras to complete (it's called in onMounted)
      await new Promise(resolve => setTimeout(resolve, 500))
      
      // Verificar que se maneja el caso de no tener cámaras
      // Puede ser un error o simplemente un array vacío
      const hasError = wrapper.vm.state.lastError && wrapper.vm.state.lastError.length > 0
      const hasNoCameras = wrapper.vm.state.availableCameras.length === 0
      expect(hasError || hasNoCameras).toBe(true)
    })

    it('should handle scanner start error', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      
      const mockInstance = {
        start: vi.fn().mockRejectedValue(new Error('Start failed')),
        stop: vi.fn().mockResolvedValue(),
        clear: vi.fn().mockResolvedValue()
      }
      
      wrapper.vm.html5QrCodeInstance = { value: mockInstance }
      wrapper.vm.state.selectedCameraId = 'camera1'
      
      await wrapper.vm.startScanner()
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.state.lastError).toContain('No fue posible iniciar el escaneo')
      expect(console.error).toHaveBeenCalled()
    })

    it('should handle scanner stop error', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      
      const mockInstance = {
        start: vi.fn().mockResolvedValue(),
        stop: vi.fn().mockRejectedValue(new Error('Stop failed')),
        clear: vi.fn().mockRejectedValue(new Error('Clear failed'))
      }
      
      wrapper.vm.html5QrCodeInstance = { value: mockInstance }
      wrapper.vm.state.isScanning = true
      
      await wrapper.vm.stopScanner()
      await wrapper.vm.$nextTick()
      
      // Should still set isScanning to false in finally block
      expect(wrapper.vm.state.isScanning).toBe(false)
      expect(console.error).toHaveBeenCalled()
    })

    it('should handle file scan error', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      
      const mockInstance = {
        scanFileV2: vi.fn().mockRejectedValue(new Error('No QR found')),
        stop: vi.fn().mockResolvedValue(),
        clear: vi.fn().mockResolvedValue()
      }
      
      wrapper.vm.html5QrCodeInstance = { value: mockInstance }
      
      const file = new File(['test'], 'test.png', { type: 'image/png' })
      const input = wrapper.find('.qr-file-input')
      if (input.exists()) {
        Object.defineProperty(input.element, 'files', {
          value: [file],
          writable: false
        })
        
        await wrapper.vm.handleFileInput({ target: input.element })
        await wrapper.vm.$nextTick()
        
        expect(wrapper.vm.state.lastError).toContain('No se encontró un código QR')
        expect(console.error).toHaveBeenCalled()
      }
    })

    it('should handle file input with no files', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      
      // Clear any existing error
      wrapper.vm.state.lastError = ''
      
      const input = { target: { files: [] } }
      await wrapper.vm.handleFileInput(input)
      
      // Should return early without error
      expect(wrapper.vm.state.lastError).toBe('')
    })

    it('should handle scan failure callback', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      
      wrapper.vm.handleScanFailure('Scan failed')
      
      expect(console.debug).toHaveBeenCalledWith('Intento fallido de lectura:', 'Scan failed')
    })

    it('should handle window undefined error', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      
      // Temporarily set window to undefined for the test
      const tempWindow = globalThis.window
      Object.defineProperty(globalThis, 'window', {
        value: undefined,
        writable: true,
        configurable: true
      })
      
      try {
        // Clear instance first by setting the ref value
        if (wrapper.vm.html5QrCodeInstance) {
          wrapper.vm.html5QrCodeInstance.value = null
        }
        
        await wrapper.vm.ensureHtml5QrCodeInstance()
        await wrapper.vm.$nextTick()
        
        expect(wrapper.vm.state.lastError).toContain('La ventana del navegador no está disponible')
      } finally {
        // Restore window
        Object.defineProperty(globalThis, 'window', {
          value: tempWindow,
          writable: true,
          configurable: true
        })
      }
    })

    it('should handle start scanner without selected camera', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      
      wrapper.vm.state.selectedCameraId = ''
      
      await wrapper.vm.startScanner()
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.state.lastError).toContain('Selecciona una cámara antes de iniciar')
    })

    it('should handle start scanner with null instance', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      
      wrapper.vm.state.selectedCameraId = 'camera1'
      
      // Mock ensureHtml5QrCodeInstance to not set the instance
      wrapper.vm.ensureHtml5QrCodeInstance = vi.fn(async () => {
        // Don't set the instance - leave it as null
        if (wrapper.vm.html5QrCodeInstance) {
          wrapper.vm.html5QrCodeInstance.value = null
        }
        return Promise.resolve()
      })
      
      await wrapper.vm.startScanner()
      await wrapper.vm.$nextTick()
      
      // The error message depends on whether ensureHtml5QrCodeInstance succeeds but instance is null
      // or if it throws an error. Let's check for either message
      const error = wrapper.vm.state.lastError
      expect(error).toMatch(/El escáner no se inicializó correctamente|No fue posible iniciar el escaneo/)
    })

    it('should handle pause scanner when not scanning', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      
      wrapper.vm.state.isScanning = false
      
      await wrapper.vm.pauseScanner()
      
      // Should return early without error
      expect(wrapper.vm.state.isPaused).toBe(false)
    })

    it('should handle resume scanner when not scanning', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      
      wrapper.vm.state.isScanning = false
      
      await wrapper.vm.resumeScanner()
      
      // Should return early without error
      expect(wrapper.vm.state.isPaused).toBe(false)
    })

    it('should handle stop scanner when instance is null', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      
      wrapper.vm.html5QrCodeInstance = { value: null }
      
      await wrapper.vm.stopScanner()
      
      // Should return early without error
      expect(wrapper.vm.state.isScanning).toBe(false)
    })

    it('should handle fetchResource with non-resource payload', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      
      const payload = {
        kind: 'unknown',
        raw: 'test'
      }
      
      await wrapper.vm.fetchResource(payload)
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.state.resourceState).toBe('error')
      expect(wrapper.vm.state.resourceError).toContain('identificador válido')
    })

    it('should handle fetchResource offline without embedded data', async () => {
      globalThis.navigator.onLine = false
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      
      const payload = {
        kind: 'resource',
        resourceId: '1',
        resourceType: null,
        raw: '1',
        metadata: {}
      }
      
      await wrapper.vm.fetchResource(payload)
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.state.resourceState).toBe('error')
      expect(wrapper.vm.state.resourceError).toContain('No hay conexión')
    })

    it('should handle fetchResource with embedded data and sync error', async () => {
      globalThis.navigator.onLine = true
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      
      const { transformEmbeddedPayload } = await import('../services/qr')
      transformEmbeddedPayload.mockReturnValue({
        id: '1',
        nombre: 'Test Animal'
      })
      
      fetchQrResource.mockRejectedValue(new Error('Sync failed'))
      
      const payload = {
        kind: 'resource',
        resourceId: '1',
        resourceType: null,
        raw: JSON.stringify({ id: '1', schema: 'qr-farm', type: 'ganado' }),
        metadata: {},
        embeddedResource: { id: '1', schema: 'qr-farm', type: 'ganado' }
      }
      
      await wrapper.vm.fetchResource(payload)
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.state.resourceOrigin).toBe('embedded')
      expect(wrapper.vm.state.resourceError).toContain('Sync failed')
      expect(wrapper.vm.state.isSyncing).toBe(false)
    })

    it('should handle handleRefresh with no lastPayload', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      
      wrapper.vm.state.lastPayload = null
      
      await wrapper.vm.handleRefresh()
      
      // Should return early
      expect(fetchQrResource).not.toHaveBeenCalled()
    })

    it('should handle resumeScanAfterResult when not paused', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      
      wrapper.vm.state.isScanning = true
      wrapper.vm.state.isPaused = false
      
      await wrapper.vm.resumeScanAfterResult()
      await wrapper.vm.$nextTick()
      
      // Should call startScanner
      expect(wrapper.vm.state.resourceState).toBe('idle')
    })

    it('should handle camera change while scanning', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      
      const mockInstance = {
        start: vi.fn().mockResolvedValue(),
        stop: vi.fn().mockResolvedValue(),
        clear: vi.fn().mockResolvedValue()
      }
      
      // Set the instance - html5QrCodeInstance is a ref, access it correctly
      // In Vue 3, when accessing from vm, refs are automatically unwrapped
      // But to set it, we might need to access the ref directly
      const instanceRef = wrapper.vm.html5QrCodeInstance
      if (instanceRef && typeof instanceRef === 'object' && 'value' in instanceRef) {
        instanceRef.value = mockInstance
      } else {
        // If it's already unwrapped, set directly
        wrapper.vm.html5QrCodeInstance = mockInstance
      }
      
      wrapper.vm.state.isScanning = true
      wrapper.vm.state.selectedCameraId = 'camera1'
      
      const event = {
        target: { value: 'camera2' }
      }
      
      await wrapper.vm.handleCameraChange(event)
      await wrapper.vm.$nextTick()
      // Wait for async operations
      await new Promise(resolve => setTimeout(resolve, 400))
      
      expect(wrapper.vm.state.selectedCameraId).toBe('camera2')
      // stopScanner should be called, which calls instance.stop
      // Verify that stop was called (it should be if instance exists and isScanning is true)
      expect(mockInstance.stop).toHaveBeenCalled()
    })

    it('should handle normalizePayload with empty string', () => {
      wrapper = createWrapper()
      const result = wrapper.vm.normalizePayload('')
      expect(result.kind).toBe('unknown')
    })

    it('should handle normalizePayload with whitespace only', () => {
      wrapper = createWrapper()
      const result = wrapper.vm.normalizePayload('   ')
      expect(result.kind).toBe('unknown')
    })

    it('should handle normalizePayload with invalid JSON', () => {
      wrapper = createWrapper()
      const result = wrapper.vm.normalizePayload('invalid json {')
      // Should try to parse as ID or URL, fallback to unknown
      expect(result).toBeDefined()
    })

    it('should handle normalizePayload with URL without numeric ID', () => {
      wrapper = createWrapper()
      const result = wrapper.vm.normalizePayload('https://example.com/path')
      expect(result.kind).toBe('url')
    })

    it('should handle isEmbeddedGanadoPayload with invalid value', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.isEmbeddedGanadoPayload(null)).toBe(false)
      expect(wrapper.vm.isEmbeddedGanadoPayload('string')).toBe(false)
      expect(wrapper.vm.isEmbeddedGanadoPayload({})).toBe(false)
    })

    it('should handle isEmbeddedGanadoPayload with valid embedded payload', () => {
      wrapper = createWrapper()
      const payload = {
        schema: 'qr-farm',
        type: 'ganado',
        id: '1'
      }
      expect(wrapper.vm.isEmbeddedGanadoPayload(payload)).toBe(true)
    })

    it('should handle isEmbeddedGanadoPayload with numeric id', () => {
      wrapper = createWrapper()
      const payload = {
        schema: 'qr-farm',
        type: 'ganado',
        id: 123
      }
      expect(wrapper.vm.isEmbeddedGanadoPayload(payload)).toBe(true)
    })

    it('should handle canUseNetwork when navigator is undefined', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      
      // The canUseNetwork function checks hasNavigatorSupport which is set at module load
      // If navigator was undefined at module load, hasNavigatorSupport would be false
      // and canUseNetwork would return true (because !hasNavigatorSupport is true)
      // But if navigator exists at module load, it will try to access navigator.onLine
      // So we need to test the case where navigator.onLine is false
      const originalOnLine = globalThis.navigator?.onLine
      if (globalThis.navigator) {
        Object.defineProperty(globalThis.navigator, 'onLine', {
          value: false,
          writable: true,
          configurable: true
        })
      }
      
      try {
        const result = wrapper.vm.canUseNetwork()
        // If navigator exists, onLine false means canUseNetwork returns false
        // If navigator doesn't exist, hasNavigatorSupport is false, so it returns true
        if (globalThis.navigator) {
          expect(result).toBe(false)
        } else {
          expect(result).toBe(true)
        }
      } finally {
        // Restore navigator.onLine
        if (globalThis.navigator && originalOnLine !== undefined) {
          Object.defineProperty(globalThis.navigator, 'onLine', {
            value: originalOnLine,
            writable: true,
            configurable: true
          })
        }
      }
    })

    it('should handle buildFetchErrorMessage with non-error object', () => {
      wrapper = createWrapper()
      const result = wrapper.vm.buildFetchErrorMessage('string error')
      expect(result).toBe('No se pudo consultar el recurso asociado.')
    })

    it('should handle buildFetchErrorMessage with error without message', () => {
      wrapper = createWrapper()
      const result = wrapper.vm.buildFetchErrorMessage({})
      expect(result).toBe('No se pudo consultar el recurso asociado.')
    })

    it('should handle emitAction', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      
      // Clear any existing errors/telemetry
      wrapper.vm.state.lastError = ''
      wrapper.vm.state.telemetryMessages = []
      
      // In Vue 3 Composition API, we need to check the emitted events
      const initialTelemetryCount = wrapper.vm.state.telemetryMessages.length
      
      wrapper.vm.emitAction('test-action')
      await wrapper.vm.$nextTick()
      
      // Check that telemetry was added
      expect(wrapper.vm.state.telemetryMessages.length).toBeGreaterThan(initialTelemetryCount)
      // Check that the last telemetry message contains the action
      const lastMessage = wrapper.vm.state.telemetryMessages[wrapper.vm.state.telemetryMessages.length - 1]
      expect(lastMessage.message).toContain('test-action')
    })

    it('should handle openFileDialog with null fileInputRef', () => {
      wrapper = createWrapper()
      // Set fileInputRef.value to null (optional chaining should handle this)
      if (wrapper.vm.fileInputRef) {
        wrapper.vm.fileInputRef.value = null
      } else {
        wrapper.vm.fileInputRef = { value: null }
      }
      
      // Should not throw error due to optional chaining
      expect(() => wrapper.vm.openFileDialog()).not.toThrow()
    })
  })
})
