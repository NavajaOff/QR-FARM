import { mount } from '@vue/test-utils'
import { vi } from 'vitest'
import ReportesAdmin from './ReportesAdmin.vue'

vi.mock('../../assets/js/reportes-admin.js', () => ({
  default: {
    name: 'ReportesAdmin',
    data() {
      return {
        loading: false,
        error: null,
        resumen: null,
        descargando: false
      }
    },
    computed: {
      summaryCards: () => [],
      trendInsights: () => [],
      secciones: () => []
    },
    methods: {
      descargarReporte: vi.fn(),
      formatBadgeClass: vi.fn(),
      formatVariacion: vi.fn(),
      formatPromedio: vi.fn(),
      formatearEstado: vi.fn(),
      formatFecha: vi.fn()
    }
  }
}))

describe('ReportesAdmin', () => {
  it('should mount correctly', () => {
    const wrapper = mount(ReportesAdmin)
    expect(wrapper.exists()).toBe(true)
  })
})