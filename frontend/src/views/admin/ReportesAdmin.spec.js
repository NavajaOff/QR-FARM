import { mount } from '@vue/test-utils'
import { beforeEach, vi, describe, it, expect } from 'vitest'
import { nextTick } from 'vue'
import ReportesAdmin from './ReportesAdmin.vue'

const {
  mockResumen,
  mockLoading,
  mockError,
  mockDescargando,
  mockSummaryCards,
  mockSecciones,
  mockTrendInsights,
  mockDescargarReporte,
  mockFormatBadgeClass,
  mockFormatVariacion,
  mockFormatPromedio,
  mockFormatearEstado,
  mockFormatFecha
} = vi.hoisted(() => {
  const mockResumen = { value: null }
  const mockLoading = { value: false }
  const mockError = { value: null }
  const mockDescargando = { value: false }
  const mockSummaryCards = { value: [] }
  const mockSecciones = { value: [] }
  const mockTrendInsights = { value: [] }
  const mockDescargarReporte = vi.fn()
  const mockFormatBadgeClass = vi.fn((v) => v > 0 ? 'badge-soft-success' : v < 0 ? 'badge-soft-danger' : 'badge-soft-muted')
  const mockFormatVariacion = vi.fn((v) => typeof v === 'number' && !isNaN(v) ? v.toFixed(1) : '0.0')
  const mockFormatPromedio = vi.fn((v) => typeof v === 'number' && !isNaN(v) && isFinite(v) ? (Number.isInteger(v) ? v.toString() : v.toFixed(1)) : '0')
  const mockFormatearEstado = vi.fn((e) => e ? e.replace('_', ' ') : 'sin estado')
  const mockFormatFecha = vi.fn((f) => f ? new Date(f).toLocaleDateString() : 'No disponible')
  
  return {
    mockResumen,
    mockLoading,
    mockError,
    mockDescargando,
    mockSummaryCards,
    mockSecciones,
    mockTrendInsights,
    mockDescargarReporte,
    mockFormatBadgeClass,
    mockFormatVariacion,
    mockFormatPromedio,
    mockFormatearEstado,
    mockFormatFecha
  }
})

vi.mock('../../assets/js/reportes-admin.js', () => ({
  default: {
    name: 'ReportesAdmin',
    setup() {
      return {
        resumen: mockResumen,
        loading: mockLoading,
        error: mockError,
        descargando: mockDescargando,
        summaryCards: mockSummaryCards,
        secciones: mockSecciones,
        trendInsights: mockTrendInsights,
        descargarReporte: mockDescargarReporte,
        formatBadgeClass: mockFormatBadgeClass,
        formatVariacion: mockFormatVariacion,
        formatPromedio: mockFormatPromedio,
        formatearEstado: mockFormatearEstado,
        formatFecha: mockFormatFecha
      }
    }
  }
}))

describe('ReportesAdmin.vue', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    mockResumen.value = null
    mockLoading.value = false
    mockError.value = null
    mockDescargando.value = false
    mockSummaryCards.value = []
    mockSecciones.value = []
    mockTrendInsights.value = []
  })

  describe('Component mounting', () => {
    it('should mount correctly', () => {
      wrapper = mount(ReportesAdmin)
      expect(wrapper.exists()).toBe(true)
    })

    it('should render the title', () => {
      wrapper = mount(ReportesAdmin)
      expect(wrapper.text()).toContain('Reportes y Analítica')
    })

    it('should render the subtitle', () => {
      wrapper = mount(ReportesAdmin)
      expect(wrapper.text()).toContain('Resumen consolidado del sistema QR-FARM')
    })
  })

  describe('Loading state', () => {
    it('should show loading spinner when loading is true', async () => {
      mockLoading.value = true
      wrapper = mount(ReportesAdmin)
      await nextTick()
      
      expect(wrapper.text()).toContain('Cargando información...')
      expect(wrapper.find('.spinner-border').exists()).toBe(true)
    })
  })

  describe('Error state', () => {
    it('should show error message when error exists', async () => {
      mockError.value = 'Error al cargar reportes'
      mockLoading.value = false
      wrapper = mount(ReportesAdmin)
      await nextTick()
      
      expect(wrapper.text()).toContain('Error al cargar reportes')
      expect(wrapper.find('.alert-danger').exists()).toBe(true)
    })
  })

  describe('Content display', () => {
    const mockSummaryCardsData = [
      {
        clave: 'usuarios',
        titulo: 'Usuarios',
        total: 50,
        variacion: 5.5,
        promedio: 2.3,
        detalles: ['Activos: 45', 'Inactivos: 5'],
        color: '#0d6efd'
      },
      {
        clave: 'ganado',
        titulo: 'Ganado',
        total: 100,
        variacion: -2.1,
        promedio: 5.0,
        detalles: ['Saludable: 80', 'Enfermo: 20'],
        color: '#198754'
      }
    ]

    it('should display summary cards when resumen exists', async () => {
      mockResumen.value = { usuarios: { totales: { total: 50 } } }
      mockSummaryCards.value = mockSummaryCardsData
      mockLoading.value = false
      mockError.value = null
      wrapper = mount(ReportesAdmin)
      await nextTick()
      
      expect(wrapper.text()).toContain('Usuarios')
      expect(wrapper.text()).toContain('Ganado')
    })

    it('should display card totals', async () => {
      mockResumen.value = { usuarios: { totales: { total: 50 } } }
      mockSummaryCards.value = mockSummaryCardsData
      mockLoading.value = false
      mockError.value = null
      wrapper = mount(ReportesAdmin)
      await nextTick()
      
      expect(wrapper.text()).toContain('50')
      expect(wrapper.text()).toContain('100')
    })

    it('should display download button', async () => {
      mockResumen.value = { usuarios: { totales: { total: 50 } } }
      mockSummaryCards.value = mockSummaryCardsData
      mockLoading.value = false
      mockError.value = null
      wrapper = mount(ReportesAdmin)
      await nextTick()
      
      const downloadButton = wrapper.find('button.btn-danger')
      expect(downloadButton.exists()).toBe(true)
      expect(downloadButton.text()).toContain('Descargar PDF')
    })

    it('should disable download button when descargando', async () => {
      mockResumen.value = { usuarios: { totales: { total: 50 } } }
      mockSummaryCards.value = mockSummaryCardsData
      mockDescargando.value = true
      mockLoading.value = false
      mockError.value = null
      wrapper = mount(ReportesAdmin)
      await nextTick()
      
      const downloadButton = wrapper.find('button.btn-danger')
      expect(downloadButton.attributes('disabled')).toBeDefined()
    })

    it('should call descargarReporte when button is clicked', async () => {
      mockResumen.value = { usuarios: { totales: { total: 50 } } }
      mockSummaryCards.value = mockSummaryCardsData
      mockDescargando.value = false
      mockLoading.value = false
      mockError.value = null
      wrapper = mount(ReportesAdmin)
      await nextTick()
      
      const downloadButton = wrapper.find('button.btn-danger')
      await downloadButton.trigger('click')
      
      expect(mockDescargarReporte).toHaveBeenCalled()
    })
  })
})
