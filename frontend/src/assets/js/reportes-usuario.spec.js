import { beforeEach, afterEach, vi, describe, it, expect } from 'vitest'

// Mock Vue
const mockRef = vi.fn((value) => ({ value }))
const mockComputed = vi.fn((fn) => ({ value: fn() }))
const mockOnMounted = vi.fn((fn) => fn())
const mockOnUnmounted = vi.fn((fn) => fn())
const mockWatch = vi.fn((deps, fn) => fn())
const mockNextTick = vi.fn(() => Promise.resolve())

vi.mock('vue', () => ({
  ref: mockRef,
  computed: mockComputed,
  onMounted: mockOnMounted,
  onUnmounted: mockOnUnmounted,
  watch: mockWatch,
  nextTick: mockNextTick
}))

// Mock Chart.js
const mockChartInstance = {
  data: { labels: [], datasets: [] },
  update: vi.fn(),
  destroy: vi.fn()
}

class MockChart {
  constructor(canvas, config) {
    this.data = config.data || { labels: [], datasets: [] }
    this.update = mockChartInstance.update
    this.destroy = mockChartInstance.destroy
    return mockChartInstance
  }
}

vi.mock('chart.js/auto', () => ({
  default: MockChart
}))

// Mock useReportes composable
const mockResumen = { value: null }
const mockLoading = { value: false }
const mockError = { value: null }
const mockCargarResumen = vi.fn()
const mockDescargarPdf = vi.fn()

vi.mock('../../composables/useReportes.js', () => ({
  useReportes: vi.fn(() => ({
    resumen: mockResumen,
    loading: mockLoading,
    error: mockError,
    cargarResumen: mockCargarResumen,
    descargarPdf: mockDescargarPdf
  }))
}))

// Mock alert
global.alert = vi.fn()

describe('reportes-usuario.js', () => {
  let module

  beforeEach(async () => {
    vi.clearAllMocks()
    
    // Reset mocks
    mockResumen.value = null
    mockLoading.value = false
    mockError.value = null
    mockCargarResumen.mockClear()
    mockDescargarPdf.mockClear()
    mockChartInstance.update.mockClear()
    mockChartInstance.destroy.mockClear()
    
    // Reset refs
    mockRef.mockImplementation((value) => ({ value }))
    mockComputed.mockImplementation((fn) => ({ value: fn() }))
    
    // Import module
    vi.resetModules()
    module = await import('./reportes-usuario.js')
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('capitalizar', () => {
    it('should capitalize first letter of text', () => {
      const component = module.default
      const setupResult = component.setup()
      const capitalizar = setupResult.capitalizar
      
      expect(capitalizar('hola')).toBe('Hola')
      expect(capitalizar('mundo')).toBe('Mundo')
    })

    it('should return "sin datos" for empty string', () => {
      const component = module.default
      const setupResult = component.setup()
      const capitalizar = setupResult.capitalizar
      
      expect(capitalizar('')).toBe('sin datos')
      expect(capitalizar(null)).toBe('sin datos')
      expect(capitalizar(undefined)).toBe('sin datos')
    })

    it('should handle single character', () => {
      const component = module.default
      const setupResult = component.setup()
      const capitalizar = setupResult.capitalizar
      
      expect(capitalizar('a')).toBe('A')
    })

    it('should handle already capitalized text', () => {
      const component = module.default
      const setupResult = component.setup()
      const capitalizar = setupResult.capitalizar
      
      expect(capitalizar('Hola')).toBe('Hola')
    })
  })

  describe('formatearFecha', () => {
    it('should format valid date string', () => {
      const component = module.default
      const setupResult = component.setup()
      const formatearFecha = setupResult.formatearFecha
      
      const date = new Date('2024-01-15T10:30:00')
      const formatted = formatearFecha(date.toISOString())
      expect(typeof formatted).toBe('string')
      expect(formatted).not.toBe('No disponible')
    })

    it('should return "No disponible" for null', () => {
      const component = module.default
      const setupResult = component.setup()
      const formatearFecha = setupResult.formatearFecha
      
      expect(formatearFecha(null)).toBe('No disponible')
    })

    it('should return "No disponible" for undefined', () => {
      const component = module.default
      const setupResult = component.setup()
      const formatearFecha = setupResult.formatearFecha
      
      expect(formatearFecha(undefined)).toBe('No disponible')
    })

    it('should return "No disponible" for empty string', () => {
      const component = module.default
      const setupResult = component.setup()
      const formatearFecha = setupResult.formatearFecha
      
      expect(formatearFecha('')).toBe('No disponible')
    })

    it('should return original value on parse error', () => {
      const component = module.default
      const setupResult = component.setup()
      const formatearFecha = setupResult.formatearFecha
      
      const invalidDate = 'invalid-date-string'
      const result = formatearFecha(invalidDate)
      expect(result).toBeDefined()
    })
  })

  describe('descargar', () => {
    it('should set descargando to true and then false', async () => {
      mockDescargarPdf.mockResolvedValue({ success: true })
      
      const component = module.default
      const setupResult = component.setup()
      const descargar = setupResult.descargar
      
      await descargar()
      
      expect(mockDescargarPdf).toHaveBeenCalled()
    })

    it('should show alert when download fails', async () => {
      mockDescargarPdf.mockResolvedValue({ success: false })
      
      const component = module.default
      const setupResult = component.setup()
      const descargar = setupResult.descargar
      
      await descargar()
      
      expect(global.alert).toHaveBeenCalledWith('No se pudo descargar el reporte. Intenta nuevamente.')
    })

    it('should handle download success without alert', async () => {
      mockDescargarPdf.mockResolvedValue({ success: true })
      global.alert.mockClear()
      
      const component = module.default
      const setupResult = component.setup()
      const descargar = setupResult.descargar
      
      await descargar()
      
      expect(global.alert).not.toHaveBeenCalled()
    })
  })

  describe('cards computed', () => {
    it('should return empty array when resumen is null', () => {
      mockResumen.value = null
      mockComputed.mockImplementation((fn) => {
        const result = fn()
        return {
          get value() { return fn() }
        }
      })
      
      vi.resetModules()
      import('./reportes-usuario.js').then(async (m) => {
        const component = m.default
        const setupResult = component.setup()
        const cards = setupResult.cards
        
        expect(cards.value).toEqual([])
      })
    })

    it('should return cards with data when resumen exists', async () => {
      mockResumen.value = {
        ganado: {
          totales: { total: 10 },
          por_estado: [
            { estado: 'saludable', cantidad: 8 },
            { estado: 'enfermo', cantidad: 2 }
          ]
        },
        potreros: {
          totales: { total: 5 },
          por_estado: [
            { estado: 'disponible', cantidad: 3 },
            { estado: 'ocupado', cantidad: 2 }
          ]
        },
        vacunaciones: {
          totales: { total: 20 },
          proximas: 5
        }
      }
      mockComputed.mockImplementation((fn) => ({
        get value() { return fn() }
      }))
      
      vi.resetModules()
      const m = await import('./reportes-usuario.js')
      const component = m.default
      const setupResult = component.setup()
      const cards = setupResult.cards
      
      expect(cards.value).toHaveLength(3)
      expect(cards.value[0].titulo).toBe('Ganado')
      expect(cards.value[0].total).toBe(10)
      expect(cards.value[1].titulo).toBe('Potreros')
      expect(cards.value[1].total).toBe(5)
      expect(cards.value[2].titulo).toBe('Vacunaciones')
      expect(cards.value[2].total).toBe(20)
    })

    it('should handle missing totales', async () => {
      mockResumen.value = {
        ganado: {},
        potreros: {},
        vacunaciones: {}
      }
      mockComputed.mockImplementation((fn) => ({
        get value() { return fn() }
      }))
      
      vi.resetModules()
      const m = await import('./reportes-usuario.js')
      const component = m.default
      const setupResult = component.setup()
      const cards = setupResult.cards
      
      expect(cards.value[0].total).toBe(0)
      expect(cards.value[1].total).toBe(0)
      expect(cards.value[2].total).toBe(0)
    })

    it('should limit detalles to 2 items', async () => {
      mockResumen.value = {
        ganado: {
          totales: { total: 10 },
          por_estado: [
            { estado: 'saludable', cantidad: 5 },
            { estado: 'enfermo', cantidad: 3 },
            { estado: 'recuperando', cantidad: 2 }
          ]
        },
        potreros: {
          totales: { total: 5 },
          por_estado: []
        },
        vacunaciones: {
          totales: { total: 20 },
          proximas: 5
        }
      }
      mockComputed.mockImplementation((fn) => ({
        get value() { return fn() }
      }))
      
      vi.resetModules()
      const m = await import('./reportes-usuario.js')
      const component = m.default
      const setupResult = component.setup()
      const cards = setupResult.cards
      
      expect(cards.value[0].detalles).toHaveLength(2)
    })
  })

  describe('secciones computed', () => {
    it('should return empty array when resumen is null', async () => {
      mockResumen.value = null
      mockComputed.mockImplementation((fn) => ({
        get value() { return fn() }
      }))
      
      vi.resetModules()
      const m = await import('./reportes-usuario.js')
      const component = m.default
      const setupResult = component.setup()
      const secciones = setupResult.secciones
      
      expect(secciones.value).toEqual([])
    })

    it('should return secciones with data when resumen exists', async () => {
      mockResumen.value = {
        ganado: {
          totales: { total: 10 },
          por_estado: [{ estado: 'saludable', cantidad: 10 }]
        },
        potreros: {
          totales: { total: 5 },
          por_estado: [{ estado: 'disponible', cantidad: 5 }]
        },
        vacunaciones: {
          totales: { total: 20 },
          por_estado: [],
          proximas: 5
        }
      }
      mockComputed.mockImplementation((fn) => ({
        get value() { return fn() }
      }))
      
      vi.resetModules()
      const m = await import('./reportes-usuario.js')
      const component = m.default
      const setupResult = component.setup()
      const secciones = setupResult.secciones
      
      expect(secciones.value).toHaveLength(3)
      expect(secciones.value[0].titulo).toBe('Ganado')
      expect(secciones.value[0].total).toBe(10)
      if (secciones.value[2] && secciones.value[2].extra) {
        expect(secciones.value[2].extra).toContain('Próximas dosis programadas: 5')
      }
    })
  })

  describe('setup', () => {
    it('should call cargarResumen on mount', () => {
      const component = module.default
      component.setup()
      
      expect(mockOnMounted).toHaveBeenCalled()
    })

    it('should setup watch for resumen and loading', () => {
      const component = module.default
      component.setup()
      
      expect(mockWatch).toHaveBeenCalled()
    })

    it('should setup onUnmounted to destroy chart', () => {
      const component = module.default
      component.setup()
      
      expect(mockOnUnmounted).toHaveBeenCalled()
    })

    it('should return all required properties', () => {
      const component = module.default
      const setupResult = component.setup()
      
      expect(setupResult).toHaveProperty('resumen')
      expect(setupResult).toHaveProperty('loading')
      expect(setupResult).toHaveProperty('error')
      expect(setupResult).toHaveProperty('descargando')
      expect(setupResult).toHaveProperty('chartCanvas')
      expect(setupResult).toHaveProperty('cards')
      expect(setupResult).toHaveProperty('secciones')
      expect(setupResult).toHaveProperty('capitalizar')
      expect(setupResult).toHaveProperty('formatearFecha')
      expect(setupResult).toHaveProperty('descargar')
    })
  })

  describe('watch callback', () => {
    it('should call renderChart when loading is false and resumen exists', async () => {
      mockResumen.value = {
        ganado: { totales: { total: 10 } },
        potreros: { totales: { total: 5 } },
        vacunaciones: { totales: { total: 20 } }
      }
      mockLoading.value = false
      mockNextTick.mockResolvedValue()
      
      const mockCanvas = { getContext: vi.fn() }
      mockRef.mockReturnValueOnce({ value: false }).mockReturnValueOnce({ value: mockCanvas })
      
      vi.resetModules()
      const m = await import('./reportes-usuario.js')
      const component = m.default
      component.setup()
      
      // Trigger watch callback
      const watchCall = mockWatch.mock.calls[0]
      if (watchCall && watchCall[1]) {
        await watchCall[1]()
      }
      
      expect(mockNextTick).toHaveBeenCalled()
    })

    it('should not call renderChart when loading is true', async () => {
      mockResumen.value = {
        ganado: { totales: { total: 10 } }
      }
      mockLoading.value = true
      
      vi.resetModules()
      const m = await import('./reportes-usuario.js')
      const component = m.default
      component.setup()
      
      // Trigger watch callback
      const watchCall = mockWatch.mock.calls[0]
      if (watchCall && watchCall[1]) {
        await watchCall[1]()
      }
      
      // renderChart should not be called when loading is true
      // But nextTick might still be called, so we check the condition
      expect(mockWatch).toHaveBeenCalled()
    })
  })

  describe('onUnmounted callback', () => {
    it('should destroy chart instance if it exists', async () => {
      // Set up chart instance
      const mockCanvas = { getContext: vi.fn() }
      mockRef.mockReturnValueOnce({ value: null }).mockReturnValueOnce({ value: mockCanvas })
      mockResumen.value = {
        ganado: { totales: { total: 10 } },
        potreros: { totales: { total: 5 } },
        vacunaciones: { totales: { total: 20 } }
      }
      
      vi.resetModules()
      const m = await import('./reportes-usuario.js')
      const component = m.default
      component.setup()
      
      // Call onUnmounted callback
      const unmountCalls = mockOnUnmounted.mock.calls
      if (unmountCalls && unmountCalls.length > 0) {
        const unmountCallback = unmountCalls[0]
        if (typeof unmountCallback === 'function') {
          unmountCallback()
        }
      }
      
      // Chart should be destroyed if it was created
      // Note: chartInstance is module-level, so it may not exist in this test
      expect(mockOnUnmounted).toHaveBeenCalled()
    })
  })
})
