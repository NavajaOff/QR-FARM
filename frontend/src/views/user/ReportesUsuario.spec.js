import { mount } from '@vue/test-utils'
import { beforeEach, vi, describe, it, expect } from 'vitest'
import ReportesUsuario from './ReportesUsuario.vue'

// Mock the composable
vi.mock('../../composables/useReportes.js', () => ({
  useReportes: vi.fn(() => ({
    resumen: { value: null },
    loading: { value: false },
    error: { value: null },
    cargarResumen: vi.fn(),
    descargarPdf: vi.fn()
  }))
}))

// Mock Chart.js
vi.mock('chart.js/auto', () => ({
  default: vi.fn()
}))

describe('ReportesUsuario.vue', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should export a Vue component', () => {
    expect(ReportesUsuario).toBeDefined()
    expect(ReportesUsuario.name).toBe('ReportesUsuario')
  })

  it('should mount successfully', () => {
    wrapper = mount(ReportesUsuario, {
      global: {
        stubs: {
          'reportes-usuario': {
            template: '<div>Mocked Reportes Component</div>'
          }
        }
      }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('should render the title', () => {
    wrapper = mount(ReportesUsuario, {
      global: {
        stubs: {
          'reportes-usuario': {
            template: '<div>Mocked Reportes Component</div>'
          }
        }
      }
    })
    expect(wrapper.text()).toContain('Reportes de Mis Recursos')
  })
})

