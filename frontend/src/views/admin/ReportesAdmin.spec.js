import { mount } from '@vue/test-utils'
import { beforeEach, vi, describe, it, expect } from 'vitest'
import { nextTick } from 'vue'
import ReportesAdmin from './ReportesAdmin.vue'

const mockRefs = vi.hoisted(() => {
  const { ref } = require('vue')
  return {
    resumen: ref(null),
    loading: ref(false),
    error: ref(null),
    descargando: ref(false),
    summaryCards: ref([]),
    secciones: ref([]),
    trendInsights: ref([]),
    descargarReporte: vi.fn(),
    formatBadgeClass: vi.fn((v) => v > 0 ? 'badge-soft-success' : v < 0 ? 'badge-soft-danger' : 'badge-soft-muted'),
    formatVariacion: vi.fn((v) => typeof v === 'number' && !isNaN(v) ? v.toFixed(1) : '0.0'),
    formatPromedio: vi.fn((v) => typeof v === 'number' && !isNaN(v) && isFinite(v) ? (Number.isInteger(v) ? v.toString() : v.toFixed(1)) : '0'),
    formatearEstado: vi.fn((e) => e ? e.replace('_', ' ') : 'sin estado'),
    formatFecha: vi.fn((f) => f ? new Date(f).toLocaleDateString() : 'No disponible')
  }
})

const mockUseReportes = vi.fn(() => ({
  resumen: mockRefs.resumen,
  loading: mockRefs.loading,
  error: mockRefs.error,
  cargarResumen: vi.fn(),
  descargarPdf: vi.fn().mockResolvedValue({ success: true })
}))

vi.mock('../../composables/useReportes.js', () => ({
  useReportes: () => mockUseReportes()
}))

describe('ReportesAdmin.vue', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    mockUseReportes.mockReturnValue({
      resumen: mockRefs.resumen,
      loading: mockRefs.loading,
      error: mockRefs.error,
      cargarResumen: vi.fn(),
      descargarPdf: vi.fn().mockResolvedValue({ success: true })
    })
    mockRefs.resumen.value = null
    mockRefs.loading.value = false
    mockRefs.error.value = null
    mockRefs.descargando.value = false
    mockRefs.summaryCards.value = []
    mockRefs.secciones.value = []
    mockRefs.trendInsights.value = []
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
      mockRefs.loading.value = true
      wrapper = mount(ReportesAdmin)
      await nextTick()

      expect(wrapper.text()).toContain('Cargando información...')
      expect(wrapper.find('.spinner-border').exists()).toBe(true)
    })
  })

  describe('Error state', () => {
    it('should show error message when error exists', async () => {
      mockRefs.loading.value = false
      mockRefs.error.value = 'Error al cargar reportes'
      mockRefs.resumen.value = null
      wrapper = mount(ReportesAdmin)
      await nextTick()
      await wrapper.vm.$nextTick()

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
      mockRefs.loading.value = false
      mockRefs.error.value = null
      mockRefs.resumen.value = { usuarios: { totales: { total: 50 } } }
      mockRefs.summaryCards.value = mockSummaryCardsData
      wrapper = mount(ReportesAdmin)
      await nextTick()
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('Usuarios')
      expect(wrapper.text()).toContain('Ganado')
    })

    it('should display card totals', async () => {
      mockRefs.loading.value = false
      mockRefs.error.value = null
      mockRefs.resumen.value = {
        usuarios: {
          totales: { total: 50, activos: 45, inactivos: 5 },
          por_estado: []
        },
        ganado: {
          totales: { total: 100 },
          por_estado: [{ estado: 'saludable', cantidad: 80 }, { estado: 'enfermo', cantidad: 20 }]
        },
        potreros: {
          totales: { total: 0 },
          por_estado: []
        },
        vacunaciones: {
          totales: { total: 0 },
          proximas: 0,
          por_estado: []
        },
        tendencias: {}
      }
      wrapper = mount(ReportesAdmin)
      await nextTick()
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('50')
      expect(wrapper.text()).toContain('100')
    })

    it('should display download button', async () => {
      mockRefs.resumen.value = { usuarios: { totales: { total: 50 } } }
      mockRefs.summaryCards.value = mockSummaryCardsData
      mockRefs.loading.value = false
      mockRefs.error.value = null
      wrapper = mount(ReportesAdmin)
      await nextTick()

      const downloadButton = wrapper.find('button.btn-danger')
      expect(downloadButton.exists()).toBe(true)
      expect(downloadButton.text()).toContain('Descargar PDF')
    })

    it('should disable download button when descargando', async () => {
      const mockDescargarPdf = vi.fn().mockImplementation(() => {
        return new Promise((resolve) => {
          setTimeout(() => resolve({ success: true }), 100)
        })
      })
      
      mockUseReportes.mockReturnValueOnce({
        resumen: mockRefs.resumen,
        loading: mockRefs.loading,
        error: mockRefs.error,
        cargarResumen: vi.fn(),
        descargarPdf: mockDescargarPdf
      })

      mockRefs.loading.value = false
      mockRefs.error.value = null
      mockRefs.resumen.value = { usuarios: { totales: { total: 50 } } }
      wrapper = mount(ReportesAdmin)
      await nextTick()
      await wrapper.vm.$nextTick()

      const downloadButton = wrapper.find('button.btn-danger')
      await downloadButton.trigger('click')
      await nextTick()

      expect(downloadButton.attributes('disabled')).toBeDefined()
    })

    it('should call descargarReporte when button is clicked', async () => {
      const mockDescargarPdf = vi.fn().mockResolvedValue({ success: true })
      
      mockUseReportes.mockReturnValueOnce({
        resumen: mockRefs.resumen,
        loading: mockRefs.loading,
        error: mockRefs.error,
        cargarResumen: vi.fn(),
        descargarPdf: mockDescargarPdf
      })

      mockRefs.loading.value = false
      mockRefs.error.value = null
      mockRefs.resumen.value = { usuarios: { totales: { total: 50 } } }
      wrapper = mount(ReportesAdmin)
      await nextTick()
      await wrapper.vm.$nextTick()

      const downloadButton = wrapper.find('button.btn-danger')
      await downloadButton.trigger('click')
      await nextTick()

      expect(mockDescargarPdf).toHaveBeenCalled()
    })
  })
})
