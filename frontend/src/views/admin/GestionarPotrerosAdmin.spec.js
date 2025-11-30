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
  currentIndex: { value: 0 },
  accordionOpen: { value: true },
  potreros: { value: [] },
  tiposPasto: { value: [] },
  estadosPotrero: { value: [] },
  personasUsuario: { value: [] },
  loading: { value: false },
  error: { value: null },
  cargarDatosIniciales: vi.fn(),
  cargarPotreros: vi.fn(),
  crearPotrero: vi.fn(),
  editarPotrero: vi.fn().mockResolvedValue(undefined),
  prevPotrero: vi.fn(),
  nextPotrero: vi.fn(),
  toggleAccordion: vi.fn(),
  estadoClass: vi.fn(() => ''),
  actualizarProximaLimpieza: vi.fn()
}))

// Mock gestionar-potreros-admin.js
vi.mock('../../assets/js/gestionar-potreros-admin.js', () => ({
  default: {
    name: 'GestionarPotreros',
    setup: vi.fn(() => ({
      currentIndex: { value: 0 },
      accordionOpen: { value: true },
      potreros: { value: [] },
      tiposPasto: { value: [] },
      estadosPotrero: { value: [] },
      personasUsuario: { value: [] },
      loading: { value: false },
      error: { value: null },
      cargarDatosIniciales: vi.fn(),
      cargarPotreros: vi.fn(),
      crearPotrero: vi.fn(),
      editarPotrero: vi.fn(),
      prevPotrero: vi.fn(),
      nextPotrero: vi.fn(),
      toggleAccordion: vi.fn(),
      estadoClass: vi.fn(() => ''),
      actualizarProximaLimpieza: vi.fn()
    })),
    computed: {},
    methods: {}
  }
}))

// Import after mocks
import GestionarPotrerosAdmin from './GestionarPotrerosAdmin.vue'

describe('GestionarPotrerosAdmin.vue', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should mount successfully', () => {
    wrapper = mount(GestionarPotrerosAdmin)
    expect(wrapper.exists()).toBe(true)
  })

  it('should render the title', () => {
    wrapper = mount(GestionarPotrerosAdmin)
    expect(wrapper.text()).toContain('Gestionar Potreros')
  })
})

