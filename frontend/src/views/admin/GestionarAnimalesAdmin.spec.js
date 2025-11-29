import { mount } from '@vue/test-utils'
import { beforeEach, vi, describe, it, expect } from 'vitest'

vi.mock('../../components/TenantSelector.vue', () => ({
  default: {
    name: 'TenantSelector',
    template: '<div>TenantSelector</div>'
  }
}))

// Mock gestionar-potreros.js to avoid parsing errors
vi.mock('../../assets/js/gestionar-potreros.js', () => ({
  potreros: { value: [] },
  cargarPotreros: vi.fn(),
  cargarDatosIniciales: vi.fn()
}))

// Mock gestionar_animales.js to avoid complex dependencies
vi.mock('../../assets/js/gestionar_animales.js', () => ({
  animales: { value: [] },
  estadosGanado: { value: [] },
  personasUsuario: { value: [] },
  loading: { value: false },
  error: { value: null },
  cargarDatosIniciales: vi.fn(),
  cargarAnimales: vi.fn(),
  editarAnimal: vi.fn(),
  agregarNuevoAnimal: vi.fn(),
  verPerfilAnimal: vi.fn(),
  darBajaAnimal: vi.fn(),
  reactivarAnimal: vi.fn(),
  setUpdateCallback: vi.fn(),
  cancelPendingRequests: vi.fn(),
  resetEstado: vi.fn()
}))

// Import after mocks
import GestionarAnimalesAdmin from './GestionarAnimalesAdmin.vue'

describe('GestionarAnimalesAdmin.vue', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should mount successfully', () => {
    wrapper = mount(GestionarAnimalesAdmin)
    expect(wrapper.exists()).toBe(true)
  })

  it('should render the title', () => {
    wrapper = mount(GestionarAnimalesAdmin)
    expect(wrapper.text()).toContain('Gestión de Ganado')
  })
})

