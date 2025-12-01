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

// Mock the ReportesUsuario component
vi.mock('../../components/ReportesUsuario.vue', () => ({
  default: {
    name: 'ReportesUsuario',
    template: '<div class="reportes-usuario-component">Mocked Reportes Component</div>'
  }
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

  it('should render the subtitle', () => {
    wrapper = mount(ReportesUsuario, {
      global: {
        stubs: {
          'reportes-usuario': {
            template: '<div>Mocked Reportes Component</div>'
          }
        }
      }
    })
    expect(wrapper.text()).toContain('Resumen de ganado, potreros y vacunaciones')
  })

  it('should render the ReportesUsuario component', () => {
    wrapper = mount(ReportesUsuario, {
      global: {
        stubs: {
          'reportes-usuario': {
            template: '<div class="reportes-usuario-component">Mocked Reportes Component</div>'
          }
        }
      }
    })
    const reportesComponent = wrapper.find('.reportes-usuario-component')
    expect(reportesComponent.exists()).toBe(true)
  })

  it('should have correct component structure', () => {
    wrapper = mount(ReportesUsuario, {
      global: {
        stubs: {
          'reportes-usuario': {
            template: '<div>Mocked Reportes Component</div>'
          }
        }
      }
    })
    expect(wrapper.find('.container-fluid').exists()).toBe(true)
    expect(wrapper.find('.row').exists()).toBe(true)
    expect(wrapper.find('.col-12').exists()).toBe(true)
  })

  it('should render icon in title', () => {
    wrapper = mount(ReportesUsuario, {
      global: {
        stubs: {
          'reportes-usuario': {
            template: '<div>Mocked Reportes Component</div>'
          }
        }
      }
    })
    const icon = wrapper.find('.fa-chart-line')
    expect(icon.exists()).toBe(true)
  })
})

