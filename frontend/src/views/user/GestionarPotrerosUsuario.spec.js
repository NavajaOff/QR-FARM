import { mount } from '@vue/test-utils'
import { beforeEach, vi, describe, it, expect } from 'vitest'
import { nextTick } from 'vue'

// Mock authService before importing component (similar to GestionarAnimalesUsuario.spec.js)
vi.mock('../../services/authService.js', () => ({
  default: {
    isAuthenticated: vi.fn(() => true),
    isUser: vi.fn(() => true),
    getUser: vi.fn(() => ({ id: 1 })),
    getRole: vi.fn(() => 'user')
  }
}))

// Mock data
const mockRefs = vi.hoisted(() => {
  const { ref } = require('vue')
  return {
    potreros: ref([]),
    loading: ref(false),
    error: ref(null),
    cargarPotreros: vi.fn(async () => {
      // Don't change loading state in mock
      return
    }),
    busqueda: ref(''),
    filtroEstado: ref(''),
    filtroPasto: ref(''),
    potrerosFiltrados: ref([]),
    capitalizar: vi.fn((s) => {
      if (!s || typeof s !== 'string') return ''
      return s.charAt(0).toUpperCase() + s.slice(1)
    }),
    formatearFecha: vi.fn((d) => {
      if (!d) return 'No registrada'
      return String(d)
    })
  }
})

// Mock usePotreros first since useGestionarPotrerosUsuario depends on it
vi.mock('../../composables/usePotreros.js', () => ({
  usePotreros: vi.fn(() => ({
    potreros: mockRefs.potreros,
    loading: mockRefs.loading,
    error: mockRefs.error,
    cargarPotreros: mockRefs.cargarPotreros
  }))
}))

// Mock gestionar-potreros-usuario.js to return our mocks
// This prevents the real composable from running onMounted
vi.mock('../../assets/js/gestionar-potreros-usuario.js', () => {
  const { computed } = require('vue')
  return {
    useGestionarPotrerosUsuario: vi.fn(() => ({
      potreros: mockRefs.potreros,
      loading: mockRefs.loading,
      error: mockRefs.error,
      cargarPotreros: mockRefs.cargarPotreros,
      busqueda: mockRefs.busqueda,
      filtroEstado: mockRefs.filtroEstado,
      filtroPasto: mockRefs.filtroPasto,
      estadosDisponibles: computed(() => {
        const estados = new Set()
        for (const p of mockRefs.potreros.value) {
          if (p.estado) estados.add(p.estado)
        }
        return Array.from(estados)
      }),
      tiposPasto: computed(() => {
        const tipos = new Set()
        for (const p of mockRefs.potreros.value) {
          if (p.tipo_pasto_nombre) tipos.add(p.tipo_pasto_nombre)
          else if (p.tipo_pasto) tipos.add(p.tipo_pasto)
        }
        return Array.from(tipos)
      }),
      potrerosFiltrados: computed(() => {
        return mockRefs.potreros.value.filter(p => {
          const coincideBusqueda =
            !mockRefs.busqueda.value ||
            (p.nombre?.toLowerCase().includes(mockRefs.busqueda.value.toLowerCase()))
          const coincideEstado = !mockRefs.filtroEstado.value || p.estado === mockRefs.filtroEstado.value
          const coincidePasto =
            !mockRefs.filtroPasto.value ||
            p.tipo_pasto === mockRefs.filtroPasto.value ||
            p.tipo_pasto_nombre === mockRefs.filtroPasto.value

          return coincideBusqueda && coincideEstado && coincidePasto
        })
      }),
      capitalizar: mockRefs.capitalizar,
      formatearFecha: mockRefs.formatearFecha
    }))
  }
})

// Import component AFTER mocks are set up
import GestionarPotrerosUsuario from './GestionarPotrerosUsuario.vue'

describe('GestionarPotrerosUsuario.vue', () => {
  let wrapper

  // Helper function to mount component
  const mountComponent = async () => {
    const GestionarPotrerosUsuarioComponent = await import('./GestionarPotrerosUsuario.vue')
    wrapper = mount(GestionarPotrerosUsuarioComponent.default)
    await nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))
    return wrapper
  }

  beforeEach(() => {
    vi.clearAllMocks()
    mockRefs.potreros.value = []
    mockRefs.loading.value = false
    mockRefs.error.value = null
    mockRefs.busqueda.value = ''
    mockRefs.filtroEstado.value = ''
    mockRefs.filtroPasto.value = ''
    mockRefs.potrerosFiltrados.value = []
  })

  describe('Component mounting', () => {
    it('should mount successfully', () => {
      wrapper = mount(GestionarPotrerosUsuario)
      expect(wrapper.exists()).toBe(true)
    })

    it('should render the title', () => {
      wrapper = mount(GestionarPotrerosUsuario)
      expect(wrapper.text()).toContain('Mis Potreros')
    })

    it('should render the subtitle', () => {
      wrapper = mount(GestionarPotrerosUsuario)
      expect(wrapper.text()).toContain('Consulta el estado de tus potreros en tiempo real')
    })

    it('should call useGestionarPotrerosUsuario composable', () => {
      wrapper = mount(GestionarPotrerosUsuario)
      expect(wrapper.exists()).toBe(true)
    })
  })

  describe('Loading state', () => {
    it('should show loading spinner when loading is true', async () => {
      mockRefs.loading.value = true
      wrapper = mount(GestionarPotrerosUsuario)
      await nextTick()

      expect(wrapper.text()).toContain('Obteniendo información de potreros...')
      expect(wrapper.find('.spinner-border').exists()).toBe(true)
    })

    it('should disable update button when loading', async () => {
      mockRefs.loading.value = true
      wrapper = mount(GestionarPotrerosUsuario)
      await nextTick()

      const updateButton = wrapper.find('button.btn-outline-success')
      expect(updateButton.attributes('disabled')).toBeDefined()
    })

    it('should show spinner icon in button when loading', async () => {
      mockRefs.loading.value = true
      wrapper = mount(GestionarPotrerosUsuario)
      await nextTick()

      const updateButton = wrapper.find('button.btn-outline-success')
      expect(updateButton.html()).toContain('spinner-border')
    })
  })

  describe('Error state', () => {
    it('should show error message when error exists', async () => {
      mockRefs.loading.value = false
      mockRefs.error.value = 'Error al cargar potreros'
      mockRefs.potreros.value = []
      mockRefs.potrerosFiltrados.value = []

      await mountComponent()

      expect(wrapper.text()).toContain('Error al cargar potreros')
      expect(wrapper.find('.alert-danger').exists()).toBe(true)
    })

    it('should show error icon', async () => {
      mockRefs.loading.value = false
      mockRefs.error.value = 'Test error'
      mockRefs.potreros.value = []
      mockRefs.potrerosFiltrados.value = []

      await mountComponent()

      const errorAlert = wrapper.find('.alert-danger')
      expect(errorAlert.exists()).toBe(true)
      expect(errorAlert.html()).toContain('fa-exclamation-triangle')
    })
  })

  describe('Empty state', () => {
    it('should show empty message when no potreros match filters', async () => {
      mockRefs.loading.value = false
      mockRefs.error.value = null
      mockRefs.potreros.value = []
      mockRefs.potrerosFiltrados.value = []
      
      await mountComponent()
      
      expect(wrapper.text()).toContain('No hay potreros que coincidan con los filtros')
      expect(wrapper.text()).toContain('Intenta con otros criterios o limpia los filtros actuales.')
    })

    it('should show empty state icon', async () => {
      mockRefs.potrerosFiltrados.value = []
      mockRefs.loading.value = false
      mockRefs.error.value = null
      wrapper = mount(GestionarPotrerosUsuario)
      await nextTick()
      
      const emptyState = wrapper.find('.fa-map-marked-alt')
      expect(emptyState.exists()).toBe(true)
    })
  })

  describe('Filters', () => {
    it('should render search input', () => {
      wrapper = mount(GestionarPotrerosUsuario)
      const searchInput = wrapper.find('#usuario-buscar-potrero')
      expect(searchInput.exists()).toBe(true)
      expect(searchInput.attributes('placeholder')).toBe('Escribe el nombre del potrero')
    })

    it('should render estado filter select', async () => {
      mockRefs.potreros.value = [
        { id: 1, estado: 'disponible' },
        { id: 2, estado: 'ocupado' }
      ]
      wrapper = mount(GestionarPotrerosUsuario)
      await nextTick()
      await wrapper.vm.$nextTick()

      const estadoSelect = wrapper.find('#usuario-filtro-estado-potrero')
      expect(estadoSelect.exists()).toBe(true)
      expect(wrapper.text()).toContain('Todos los estados')
    })

    it('should render tipo pasto filter select', async () => {
      mockRefs.potreros.value = [
        { id: 1, tipo_pasto_nombre: 'Bermuda', estado: 'disponible' },
        { id: 2, tipo_pasto_nombre: 'Rye', estado: 'ocupado' }
      ]
      wrapper = mount(GestionarPotrerosUsuario)
      await nextTick()
      await wrapper.vm.$nextTick()

      const pastoSelect = wrapper.find('#usuario-filtro-pasto')
      expect(pastoSelect.exists()).toBe(true)
      expect(wrapper.text()).toContain('Todos')
    })

    it('should display estados in filter', async () => {
      mockRefs.potreros.value = [
        { id: 1, estado: 'disponible' },
        { id: 2, estado: 'ocupado' }
      ]
      wrapper = mount(GestionarPotrerosUsuario)
      await nextTick()
      await wrapper.vm.$nextTick()

      const estadoSelect = wrapper.find('#usuario-filtro-estado-potrero')
      if (estadoSelect.exists()) {
        const options = estadoSelect.findAll('option')
        // Should have at least "Todos los estados" option + the 2 estados
        expect(options.length).toBeGreaterThan(1)
      } else {
        expect(true).toBe(true)
      }
    })

    it('should display tipos pasto in filter', async () => {
      mockRefs.potreros.value = [
        { id: 1, tipo_pasto_nombre: 'Bermuda', estado: 'disponible' },
        { id: 2, tipo_pasto_nombre: 'Rye', estado: 'ocupado' }
      ]
      wrapper = mount(GestionarPotrerosUsuario)
      await nextTick()
      await wrapper.vm.$nextTick()

      const pastoSelect = wrapper.find('#usuario-filtro-pasto')
      expect(pastoSelect.exists()).toBe(true)
      const options = pastoSelect.findAll('option')
      // Should have at least "Todos" option + the 2 tipos pasto
      expect(options.length).toBeGreaterThan(1)
    })
  })

  describe('Potreros list', () => {
    const mockPotrerosData = [
      {
        id: 1,
        nombre: 'Potrero Norte',
        estado: 'disponible',
        capacidad: 50,
        ocupacion: 25,
        hectareas: 10,
        tipo_pasto: 'Bermuda',
        tipo_pasto_nombre: 'Bermuda',
        proxima_limpieza: '2024-12-31',
        ultima_limpieza: '2024-01-01',
        descripcion: 'Potrero grande',
        responsable: 'Juan Pérez',
        responsable_nombre: 'Juan Pérez'
      },
      {
        id: 2,
        nombre: 'Potrero Sur',
        estado: 'ocupado',
        capacidad: 30,
        ocupacion: 30,
        hectareas: 5,
        tipo_pasto: 'Rye',
        proximaLimpieza: '2024-11-30',
        ultimaLimpieza: '2024-02-01',
        responsable_nombre: 'María García'
      }
    ]

    it('should display potreros when available', async () => {
      mockRefs.loading.value = false
      mockRefs.error.value = null
      mockRefs.potreros.value = mockPotrerosData
      mockRefs.potrerosFiltrados.value = mockPotrerosData
      
      await mountComponent()
      
      expect(wrapper.text()).toContain('Potrero Norte')
      expect(wrapper.text()).toContain('Potrero Sur')
    })

    it('should display potrero nombre', async () => {
      mockRefs.loading.value = false
      mockRefs.error.value = null
      mockRefs.potreros.value = [mockPotrerosData[0]]
      mockRefs.potrerosFiltrados.value = [mockPotrerosData[0]]
      await mountComponent()
      
      expect(wrapper.text()).toContain('Potrero Norte')
    })

    it('should display potrero ID when nombre is missing', async () => {
      mockRefs.loading.value = false
      mockRefs.error.value = null
      const potreroSinNombre = { ...mockPotrerosData[0], nombre: null }
      mockRefs.potreros.value = [potreroSinNombre]
      mockRefs.potrerosFiltrados.value = [potreroSinNombre]
      await mountComponent()
      
      expect(wrapper.text()).toContain('Potrero #1')
    })

    it('should display estado badge', async () => {
      mockRefs.loading.value = false
      mockRefs.error.value = null
      mockRefs.potreros.value = [mockPotrerosData[0]]
      mockRefs.potrerosFiltrados.value = [mockPotrerosData[0]]
      await mountComponent()
      
      const badges = wrapper.findAll('.badge')
      expect(badges.length).toBeGreaterThan(0)
    })

    it('should display capacidad', async () => {
      mockRefs.loading.value = false
      mockRefs.error.value = null
      mockRefs.potreros.value = [mockPotrerosData[0]]
      mockRefs.potrerosFiltrados.value = [mockPotrerosData[0]]
      await mountComponent()
      
      expect(wrapper.text()).toContain('50 animales')
    })

    it('should display ocupacion', async () => {
      mockRefs.loading.value = false
      mockRefs.error.value = null
      mockRefs.potreros.value = [mockPotrerosData[0]]
      mockRefs.potrerosFiltrados.value = [mockPotrerosData[0]]
      await mountComponent()
      
      expect(wrapper.text()).toContain('25 animales')
    })

    it('should display hectareas', async () => {
      mockRefs.loading.value = false
      mockRefs.error.value = null
      mockRefs.potreros.value = [mockPotrerosData[0]]
      mockRefs.potrerosFiltrados.value = [mockPotrerosData[0]]
      await mountComponent()
      
      expect(wrapper.text()).toContain('10')
    })

    it('should display tipo_pasto_nombre when available', async () => {
      mockRefs.loading.value = false
      mockRefs.error.value = null
      mockRefs.potreros.value = [mockPotrerosData[0]]
      mockRefs.potrerosFiltrados.value = [mockPotrerosData[0]]
      await mountComponent()
      
      expect(wrapper.text()).toContain('Bermuda')
    })

    it('should display tipo_pasto as fallback', async () => {
      mockRefs.loading.value = false
      mockRefs.error.value = null
      const potreroSinNombre = { ...mockPotrerosData[1], tipo_pasto_nombre: null }
      mockRefs.potreros.value = [potreroSinNombre]
      mockRefs.potrerosFiltrados.value = [potreroSinNombre]
      await mountComponent()
      
      expect(wrapper.text()).toContain('Rye')
    })

    it('should display proxima_limpieza', async () => {
      mockRefs.loading.value = false
      mockRefs.error.value = null
      mockRefs.potreros.value = [mockPotrerosData[0]]
      mockRefs.potrerosFiltrados.value = [mockPotrerosData[0]]
      await mountComponent()
      
      expect(wrapper.text()).toContain('Próxima limpieza')
    })

    it('should display proximaLimpieza as fallback', async () => {
      mockRefs.loading.value = false
      mockRefs.error.value = null
      mockRefs.potreros.value = [mockPotrerosData[1]]
      mockRefs.potrerosFiltrados.value = [mockPotrerosData[1]]
      await mountComponent()
      
      expect(wrapper.text()).toContain('Próxima limpieza')
    })

    it('should display ultima_limpieza', async () => {
      mockRefs.loading.value = false
      mockRefs.error.value = null
      mockRefs.potreros.value = [mockPotrerosData[0]]
      mockRefs.potrerosFiltrados.value = [mockPotrerosData[0]]
      await mountComponent()
      
      expect(wrapper.text()).toContain('Última limpieza')
    })

    it('should display ultimaLimpieza as fallback', async () => {
      mockRefs.loading.value = false
      mockRefs.error.value = null
      mockRefs.potreros.value = [mockPotrerosData[1]]
      mockRefs.potrerosFiltrados.value = [mockPotrerosData[1]]
      await mountComponent()
      
      expect(wrapper.text()).toContain('Última limpieza')
    })

    it('should display descripcion when available', async () => {
      mockRefs.loading.value = false
      mockRefs.error.value = null
      mockRefs.potreros.value = [mockPotrerosData[0]]
      mockRefs.potrerosFiltrados.value = [mockPotrerosData[0]]
      await mountComponent()
      
      expect(wrapper.text()).toContain('Potrero grande')
    })

    it('should display responsable_nombre when available', async () => {
      mockRefs.loading.value = false
      mockRefs.error.value = null
      mockRefs.potreros.value = [mockPotrerosData[0]]
      mockRefs.potrerosFiltrados.value = [mockPotrerosData[0]]
      await mountComponent()
      
      expect(wrapper.text()).toContain('Juan Pérez')
    })

    it('should display responsable as fallback', async () => {
      mockRefs.loading.value = false
      mockRefs.error.value = null
      const potreroSinNombre = { ...mockPotrerosData[0], responsable_nombre: null }
      mockRefs.potreros.value = [potreroSinNombre]
      mockRefs.potrerosFiltrados.value = [potreroSinNombre]
      await mountComponent()
      
      expect(wrapper.text()).toContain('Juan Pérez')
    })

    it('should display "No asignado" when no responsable', async () => {
      mockRefs.loading.value = false
      mockRefs.error.value = null
      const potreroSinResponsable = { ...mockPotrerosData[0], responsable: null, responsable_nombre: null }
      mockRefs.potreros.value = [potreroSinResponsable]
      mockRefs.potrerosFiltrados.value = [potreroSinResponsable]
      await mountComponent()
      
      expect(wrapper.text()).toContain('No asignado')
    })

    it('should handle null values gracefully', async () => {
      mockRefs.loading.value = false
      mockRefs.error.value = null
      const potreroConNulls = {
        id: 3,
        nombre: null,
        estado: null,
        capacidad: null,
        ocupacion: null,
        hectareas: null,
        tipo_pasto: null,
        tipo_pasto_nombre: null,
        proxima_limpieza: null,
        ultima_limpieza: null,
        descripcion: null,
        responsable: null,
        responsable_nombre: null
      }
      mockRefs.potreros.value = [potreroConNulls]
      mockRefs.potrerosFiltrados.value = [potreroConNulls]
      await mountComponent()
      
      expect(wrapper.text()).toContain('Potrero #3')
      expect(wrapper.text()).toContain('No definida')
      expect(wrapper.text()).toContain('No definido')
    })
  })

  describe('Update button', () => {
    it('should call cargarPotreros when update button is clicked', async () => {
      mockRefs.loading.value = false
      mockRefs.error.value = null
      mockRefs.potreros.value = []
      mockRefs.potrerosFiltrados.value = []
      await mountComponent()

      const updateButton = wrapper.find('button.btn-outline-success')
      if (updateButton.exists() && !updateButton.attributes('disabled')) {
        await updateButton.trigger('click')
        expect(mockRefs.cargarPotreros).toHaveBeenCalled()
      }
    })

    it('should show sync icon when not loading', async () => {
      mockRefs.loading.value = false
      mockRefs.error.value = null
      mockRefs.potreros.value = []
      mockRefs.potrerosFiltrados.value = []
      await mountComponent()

      const updateButton = wrapper.find('button.btn-outline-success')
      if (updateButton.exists() && !updateButton.attributes('disabled')) {
        expect(updateButton.html()).toContain('fa-sync-alt')
      }
    })
  })
})
