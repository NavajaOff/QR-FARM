import { mount } from '@vue/test-utils'
import { vi } from 'vitest'
import reportesUsuario from './reportes-usuario.js'

// Mock import.meta.env
vi.stubGlobal('import.meta', {
  env: {
    VITE_BACKEND_URL: 'http://localhost:5000'
  }
})

// Mock api.js
vi.mock('../../services/api.js', () => ({
  reporteAPI: {
    getResumen: vi.fn(),
    descargarPdf: vi.fn()
  }
}))

// Mock de useReportes
vi.mock('../../composables/useReportes.js', () => ({
  useReportes: () => ({
    resumen: { value: null },
    loading: { value: false },
    error: { value: null },
    cargarResumen: vi.fn(),
    descargarPdf: vi.fn()
  })
}))

// Mock de Chart.js
vi.mock('chart.js/auto', () => ({
  default: vi.fn(() => ({
    destroy: vi.fn(),
    update: vi.fn(),
    data: { labels: [], datasets: [] }
  }))
}))

describe('reportes-usuario.js', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
  })

  const createWrapper = (options = {}) => {
    return mount(reportesUsuario, {
      template: '<div><canvas ref="chartCanvas"></canvas></div>',
      ...options
    })
  }

  describe('Component Definition', () => {
    it('should export a Vue component', () => {
      expect(reportesUsuario).toBeDefined()
      expect(reportesUsuario.name).toBe('ReportesUsuario')
    })

    it('should have setup function', () => {
      expect(typeof reportesUsuario.setup).toBe('function')
    })
  })

  describe('capitalizar Function', () => {
    it('should capitalize text', () => {
      const result = reportesUsuario.setup().capitalizar('hello')
      expect(result).toBe('Hello')
    })

    it('should handle empty text', () => {
      const result = reportesUsuario.setup().capitalizar('')
      expect(result).toBe('sin datos')
    })

    it('should handle null text', () => {
      const result = reportesUsuario.setup().capitalizar(null)
      expect(result).toBe('sin datos')
    })
  })

  describe('formatearFecha Function', () => {
    it('should format date', () => {
      const result = reportesUsuario.setup().formatearFecha('2023-01-01')
      expect(result).toMatch(/\d/)
    })

    it('should handle invalid date', () => {
      const result = reportesUsuario.setup().formatearFecha(null)
      expect(result).toBe('No disponible')
    })
  })

  describe('cards Computed', () => {
    it('should return empty array when no resumen', () => {
      const { cards } = reportesUsuario.setup()
      expect(cards.value).toEqual([])
    })

    it('should return cards data when resumen exists', () => {
      const { useReportes } = require('../../composables/useReportes.js')
      const mockResumen = {
        ganado: {
          totales: { total: 10 },
          por_estado: [
            { estado: 'activo', cantidad: 8 },
            { estado: 'inactivo', cantidad: 2 }
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

      useReportes.mockReturnValue({
        resumen: { value: mockResumen },
        loading: { value: false },
        error: { value: null },
        cargarResumen: vi.fn(),
        descargarPdf: vi.fn()
      })

      const { cards } = reportesUsuario.setup()
      expect(cards.value).toHaveLength(3)
      expect(cards.value[0].titulo).toBe('Ganado')
      expect(cards.value[0].total).toBe(10)
    })
  })

  describe('secciones Computed', () => {
    it('should return empty array when no resumen', () => {
      const { secciones } = reportesUsuario.setup()
      expect(secciones.value).toEqual([])
    })

    it('should return secciones data when resumen exists', () => {
      const { useReportes } = require('../../composables/useReportes.js')
      const mockResumen = {
        ganado: {
          totales: { total: 10 },
          por_estado: [{ estado: 'activo', cantidad: 8 }]
        },
        potreros: {
          totales: { total: 5 },
          por_estado: [{ estado: 'disponible', cantidad: 3 }]
        },
        vacunaciones: {
          totales: { total: 20 },
          por_estado: [{ estado: 'aplicado', cantidad: 15 }],
          proximas: 5
        }
      }

      useReportes.mockReturnValue({
        resumen: { value: mockResumen },
        loading: { value: false },
        error: { value: null },
        cargarResumen: vi.fn(),
        descargarPdf: vi.fn()
      })

      const { secciones } = reportesUsuario.setup()
      expect(secciones.value).toHaveLength(3)
      expect(secciones.value[0].titulo).toBe('Ganado')
      expect(secciones.value[0].total).toBe(10)
    })
  })

  describe('descargar Function', () => {
    it('should call descargarPdf and handle success', async () => {
      const { useReportes } = require('../../composables/useReportes.js')
      const mockDescargarPdf = vi.fn().mockResolvedValue({ success: true })

      useReportes.mockReturnValue({
        resumen: { value: null },
        loading: { value: false },
        error: { value: null },
        cargarResumen: vi.fn(),
        descargarPdf: mockDescargarPdf
      })

      const { descargar, descargando } = reportesUsuario.setup()
      await descargar()

      expect(mockDescargarPdf).toHaveBeenCalled()
      expect(descargando.value).toBe(false)
    })

    it('should handle download failure', async () => {
      const { useReportes } = require('../../composables/useReportes.js')
      const mockDescargarPdf = vi.fn().mockResolvedValue({ success: false })
      const alertSpy = vi.spyOn(globalThis, 'alert').mockImplementation(() => {})

      useReportes.mockReturnValue({
        resumen: { value: null },
        loading: { value: false },
        error: { value: null },
        cargarResumen: vi.fn(),
        descargarPdf: mockDescargarPdf
      })

      const { descargar } = reportesUsuario.setup()
      await descargar()

      expect(alertSpy).toHaveBeenCalledWith('No se pudo descargar el reporte. Intenta nuevamente.')
    })
  })

  describe('generarDatosGrafica Function', () => {
    it('should return empty data when no resumen', () => {
      const { useReportes } = require('../../composables/useReportes.js')
      useReportes.mockReturnValue({
        resumen: { value: null },
        loading: { value: false },
        error: { value: null },
        cargarResumen: vi.fn(),
        descargarPdf: vi.fn()
      })

      // Access the internal function through setup
      const setupResult = reportesUsuario.setup()
      // Since it's internal, we test the computed that uses it indirectly
      expect(setupResult.cards.value).toEqual([])
    })

    it('should generate chart data when resumen exists', () => {
      const { useReportes } = require('../../composables/useReportes.js')
      const mockResumen = {
        ganado: { totales: { total: 10 } },
        potreros: { totales: { total: 5 } },
        vacunaciones: { totales: { total: 20 } }
      }

      useReportes.mockReturnValue({
        resumen: { value: mockResumen },
        loading: { value: false },
        error: { value: null },
        cargarResumen: vi.fn(),
        descargarPdf: vi.fn()
      })

      const { cards } = reportesUsuario.setup()
      expect(cards.value).toHaveLength(3)
      expect(cards.value[0].total).toBe(10)
      expect(cards.value[1].total).toBe(5)
      expect(cards.value[2].total).toBe(20)
    })
  })

  describe('Component Integration', () => {
    it('should mount correctly', () => {
      wrapper = createWrapper()
      expect(wrapper.vm).toBeDefined()
    })
  })
})