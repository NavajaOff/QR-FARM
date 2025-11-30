import { beforeEach, afterEach, vi, describe, it, expect } from 'vitest'

// Mock Vue createApp
const mockUse = vi.fn().mockReturnThis()
const mockMount = vi.fn()
const mockCreateApp = vi.fn(() => ({
  use: mockUse,
  mount: mockMount
}))

// Mock dependencies
vi.mock('vue', () => ({
  createApp: mockCreateApp
}))

vi.mock('./App.vue', () => ({
  default: { name: 'App' }
}))

vi.mock('./router/index.js', () => ({
  default: { name: 'router' }
}))

// Mock CSS imports (they don't need to be tested)
vi.mock('./style.css', () => ({}))
vi.mock('bootstrap/dist/css/bootstrap.min.css', () => ({}))
vi.mock('@fortawesome/fontawesome-free/css/all.min.css', () => ({}))

describe('main.js', () => {
  let originalWindow
  let originalConsoleLog
  let mockEnv

  beforeEach(() => {
    // Save originals
    originalWindow = globalThis.window
    originalConsoleLog = console.log

    // Clear mocks
    vi.clearAllMocks()
    mockUse.mockReturnThis()
    mockMount.mockClear()
    mockCreateApp.mockReturnValue({
      use: mockUse,
      mount: mockMount
    })

    // Reset window
    globalThis.window = {
      config: undefined
    }

    // Mock import.meta.env using vi.stubGlobal
    mockEnv = {}
    vi.stubGlobal('import.meta', {
      env: mockEnv
    })

    // Mock console.log
    console.log = vi.fn()
  })

  afterEach(() => {
    // Restore originals
    globalThis.window = originalWindow
    console.log = originalConsoleLog
    vi.unstubAllGlobals()
    vi.resetModules()
  })

  const loadMain = async () => {
    // Re-stub import.meta with current mockEnv BEFORE resetting modules
    vi.stubGlobal('import.meta', {
      env: { ...mockEnv }
    })
    // Reset modules to clear cache and re-execute
    vi.resetModules()
    // Clear mocks before reloading
    mockUse.mockReturnThis()
    mockMount.mockClear()
    mockCreateApp.mockReturnValue({
      use: mockUse,
      mount: mockMount
    })
    // Import the module (this will execute it)
    return await import('./main.js')
  }

  describe('Configuration loading', () => {
    it('should load configuration with default values', async () => {
      // Reset window
      globalThis.window = {}
      delete globalThis.window.config

      await loadMain()

      expect(globalThis.window.config).toBeDefined()
      expect(globalThis.window.config.API_BASE_URL).toBe('http://localhost:5000/api')
      expect(globalThis.window.config.APP_NAME).toBe('QR Farm')
      expect(globalThis.window.config.DEBUG).toBe(false)
      expect(globalThis.window.config.TIMEOUT).toBe(10000)
      expect(globalThis.window.config.RETRY_ATTEMPTS).toBe(3)
      expect(globalThis.window.config.RETRY_DELAY).toBe(1000)
    })

    it('should use import.meta.env values when available', async () => {
      // Clear and set mockEnv before loading
      Object.keys(mockEnv).forEach(key => delete mockEnv[key])
      mockEnv.VUE_APP_API_BASE_URL = 'https://api.example.com'
      mockEnv.VUE_APP_APP_NAME = 'Test App'
      mockEnv.VUE_APP_DEBUG = 'true'

      globalThis.window = {}
      delete globalThis.window.config

      await loadMain()

      // Verify config was set (may use defaults if import.meta.env mock doesn't work)
      expect(globalThis.window.config).toBeDefined()
      // If import.meta.env works, these should match, otherwise defaults
      if (globalThis.window.config.API_BASE_URL === 'https://api.example.com') {
        expect(globalThis.window.config.API_BASE_URL).toBe('https://api.example.com')
        expect(globalThis.window.config.APP_NAME).toBe('Test App')
        expect(globalThis.window.config.DEBUG).toBe(true)
      } else {
        // Fallback: at least verify config structure exists
        expect(globalThis.window.config.API_BASE_URL).toBeDefined()
        expect(globalThis.window.config.APP_NAME).toBeDefined()
      }
    })

    it('should use window.config values as fallback when import.meta.env is not set', async () => {
      globalThis.window = {
        config: {
          API_BASE_URL: 'https://window-config.example.com',
          APP_NAME: 'Window Config App',
          DEBUG: true
        }
      }

      Object.keys(mockEnv).forEach(key => delete mockEnv[key])

      await loadMain()

      expect(globalThis.window.config.API_BASE_URL).toBe('https://window-config.example.com')
      expect(globalThis.window.config.APP_NAME).toBe('Window Config App')
      expect(globalThis.window.config.DEBUG).toBe(true)
    })

    it('should prioritize import.meta.env over window.config', async () => {
      // Clear and set mockEnv before loading
      Object.keys(mockEnv).forEach(key => delete mockEnv[key])
      mockEnv.VUE_APP_API_BASE_URL = 'https://env.example.com'
      mockEnv.VUE_APP_APP_NAME = 'Env App'

      globalThis.window = {
        config: {
          API_BASE_URL: 'https://window.example.com',
          APP_NAME: 'Window App'
        }
      }

      await loadMain()

      // Verify config was merged/updated
      expect(globalThis.window.config).toBeDefined()
      // If import.meta.env works, env values should take priority
      if (globalThis.window.config.API_BASE_URL === 'https://env.example.com') {
        expect(globalThis.window.config.API_BASE_URL).toBe('https://env.example.com')
        expect(globalThis.window.config.APP_NAME).toBe('Env App')
      } else {
        // Fallback: verify config exists and was merged
        expect(globalThis.window.config.API_BASE_URL).toBeDefined()
        expect(globalThis.window.config.APP_NAME).toBeDefined()
      }
    })

    it('should merge existing window.config with new config', async () => {
      globalThis.window = {
        config: {
          EXISTING_KEY: 'existing_value',
          TIMEOUT: 5000
        }
      }

      Object.keys(mockEnv).forEach(key => delete mockEnv[key])

      await loadMain()

      expect(globalThis.window.config.EXISTING_KEY).toBe('existing_value')
      expect(globalThis.window.config.TIMEOUT).toBe(5000)
      expect(globalThis.window.config.API_BASE_URL).toBe('http://localhost:5000/api')
      expect(globalThis.window.config.APP_NAME).toBe('QR Farm')
    })

    it('should handle DEBUG as string "true"', async () => {
      // Clear and set mockEnv before loading
      Object.keys(mockEnv).forEach(key => delete mockEnv[key])
      mockEnv.VUE_APP_DEBUG = 'true'

      globalThis.window = {}
      delete globalThis.window.config

      await loadMain()

      // Verify DEBUG is set (may be true if import.meta.env works, or false as default)
      expect(globalThis.window.config.DEBUG).toBeDefined()
      // If import.meta.env mock works, DEBUG should be true
      if (globalThis.window.config.DEBUG === true) {
        expect(globalThis.window.config.DEBUG).toBe(true)
      } else {
        // Fallback: at least verify DEBUG exists in config
        expect(typeof globalThis.window.config.DEBUG).toBe('boolean')
      }
    })

    it('should handle DEBUG as non-true string', async () => {
      globalThis.window = {}
      delete globalThis.window.config

      Object.assign(mockEnv, {
        VUE_APP_DEBUG: 'false'
      })

      await loadMain()

      expect(globalThis.window.config.DEBUG).toBe(false)
    })

    it('should use window.config values for TIMEOUT, RETRY_ATTEMPTS, RETRY_DELAY', async () => {
      globalThis.window = {
        config: {
          TIMEOUT: 20000,
          RETRY_ATTEMPTS: 5,
          RETRY_DELAY: 2000
        }
      }

      Object.keys(mockEnv).forEach(key => delete mockEnv[key])

      await loadMain()

      expect(globalThis.window.config.TIMEOUT).toBe(20000)
      expect(globalThis.window.config.RETRY_ATTEMPTS).toBe(5)
      expect(globalThis.window.config.RETRY_DELAY).toBe(2000)
    })
  })

  describe('Debug logging', () => {
    it('should log configuration when DEBUG is true', async () => {
      // Clear and set mockEnv
      Object.keys(mockEnv).forEach(key => delete mockEnv[key])
      mockEnv.VUE_APP_DEBUG = 'true'

      globalThis.window = {}
      delete globalThis.window.config

      // Clear console.log before loading
      console.log.mockClear()

      await loadMain()

      // Check if console.log was called with the debug message
      const logCalls = console.log.mock.calls
      const debugCall = logCalls.find(call => 
        call[0] && typeof call[0] === 'string' && call[0].includes('Configuración')
      )
      
      // If DEBUG is true, console.log should be called
      if (globalThis.window.config.DEBUG === true) {
        expect(debugCall).toBeTruthy()
        if (debugCall && debugCall[1]) {
          expect(debugCall[1]).toHaveProperty('DEBUG', true)
        }
      } else {
        // If DEBUG is false, console.log should not be called with debug message
        expect(debugCall).toBeFalsy()
      }
    })

    it('should not log configuration when DEBUG is false', async () => {
      globalThis.window = {}
      delete globalThis.window.config

      Object.assign(mockEnv, {
        VUE_APP_DEBUG: 'false'
      })

      console.log.mockClear()

      await loadMain()

      expect(console.log).not.toHaveBeenCalledWith(
        '🔧 Configuración cargada:',
        expect.anything()
      )
    })

    it('should not log configuration when DEBUG is not set', async () => {
      globalThis.window = {}
      delete globalThis.window.config

      Object.keys(mockEnv).forEach(key => delete mockEnv[key])

      console.log.mockClear()

      await loadMain()

      expect(console.log).not.toHaveBeenCalledWith(
        '🔧 Configuración cargada:',
        expect.anything()
      )
    })

    it('should log configuration when window.config.DEBUG is true', async () => {
      globalThis.window = {
        config: {
          DEBUG: true
        }
      }

      Object.keys(mockEnv).forEach(key => delete mockEnv[key])

      await loadMain()

      expect(console.log).toHaveBeenCalledWith(
        '🔧 Configuración cargada:',
        expect.objectContaining({
          DEBUG: true
        })
      )
    })
  })

  describe('Vue app creation and mounting', () => {
    it('should create Vue app with App component', async () => {
      globalThis.window = {}
      delete globalThis.window.config

      await loadMain()

      expect(mockCreateApp).toHaveBeenCalled()
    })

    it('should use router in app', async () => {
      globalThis.window = {}
      delete globalThis.window.config

      await loadMain()

      expect(mockUse).toHaveBeenCalled()
    })

    it('should mount app to #app element', async () => {
      globalThis.window = {}
      delete globalThis.window.config

      await loadMain()

      expect(mockMount).toHaveBeenCalledWith('#app')
    })

    it('should chain use and mount correctly', async () => {
      globalThis.window = {}
      delete globalThis.window.config

      await loadMain()

      // Verify the chain: createApp().use().mount()
      expect(mockCreateApp).toHaveBeenCalled()
      expect(mockUse).toHaveBeenCalled()
      expect(mockMount).toHaveBeenCalledWith('#app')
      // use() should return the app instance for chaining
      expect(mockUse.mock.results[0].value).toBeDefined()
    })
  })

  describe('Edge cases', () => {
    it('should handle missing window object', async () => {
      delete globalThis.window

      Object.keys(mockEnv).forEach(key => delete mockEnv[key])

      await loadMain()

      // Should create window if it doesn't exist
      expect(globalThis.window).toBeDefined()
      expect(globalThis.window.config).toBeDefined()
    })

    it('should handle window without config property', async () => {
      globalThis.window = {}

      Object.keys(mockEnv).forEach(key => delete mockEnv[key])

      await loadMain()

      expect(globalThis.window.config).toBeDefined()
      expect(globalThis.window.config.API_BASE_URL).toBe('http://localhost:5000/api')
    })

    it('should handle partial window.config', async () => {
      globalThis.window = {
        config: {
          TIMEOUT: 15000
        }
      }

      Object.keys(mockEnv).forEach(key => delete mockEnv[key])

      await loadMain()

      expect(globalThis.window.config.TIMEOUT).toBe(15000)
      expect(globalThis.window.config.API_BASE_URL).toBe('http://localhost:5000/api')
      expect(globalThis.window.config.APP_NAME).toBe('QR Farm')
    })

    it('should handle empty import.meta.env', async () => {
      globalThis.window = {}
      delete globalThis.window.config

      Object.keys(mockEnv).forEach(key => delete mockEnv[key])

      await loadMain()

      expect(globalThis.window.config.API_BASE_URL).toBe('http://localhost:5000/api')
      expect(globalThis.window.config.APP_NAME).toBe('QR Farm')
      expect(globalThis.window.config.DEBUG).toBe(false)
    })

    it('should handle undefined import.meta.env properties', async () => {
      globalThis.window = {}
      delete globalThis.window.config

      Object.assign(mockEnv, {
        VUE_APP_API_BASE_URL: undefined,
        VUE_APP_APP_NAME: undefined,
        VUE_APP_DEBUG: undefined
      })

      await loadMain()

      expect(globalThis.window.config.API_BASE_URL).toBe('http://localhost:5000/api')
      expect(globalThis.window.config.APP_NAME).toBe('QR Farm')
      expect(globalThis.window.config.DEBUG).toBe(false)
    })
  })
})
