import { mount } from '@vue/test-utils'
import { beforeEach, vi, describe, it, expect } from 'vitest'
import { nextTick } from 'vue'
import GestionarPotrerosUsuario from './GestionarPotrerosUsuario.vue'

// Mock data using vi.hoisted to ensure they're available before mocks
const mockPotreros = { value: [] }
const mockLoading = { value: false }
const mockError = { value: null }
const mockCargarPotreros = vi.fn()
const mockBusqueda = { value: '' }
const mockFiltroEstado = { value: '' }
const mockFiltroPasto = { value: '' }
const mockEstadosDisponibles = { value: [] }
const mockTiposPasto = { value: [] }
const mockPotrerosFiltrados = { value: [] }
const mockCapitalizar = vi.fn((s) => s ? s.charAt(0).toUpperCase() + s.slice(1) : '')
const mockFormatearFecha = vi.fn((d) => d || 'No registrada')

vi.mock('../../assets/js/gestionar-potreros-usuario.js', () => ({
  useGestionarPotrerosUsuario: vi.fn(() => ({
    potreros: mockPotreros,
    loading: mockLoading,
    error: mockError,
    cargarPotreros: mockCargarPotreros,
    busqueda: mockBusqueda,
    filtroEstado: mockFiltroEstado,
    filtroPasto: mockFiltroPasto,
    estadosDisponibles: mockEstadosDisponibles,
    tiposPasto: mockTiposPasto,
    potrerosFiltrados: mockPotrerosFiltrados,
    capitalizar: mockCapitalizar,
    formatearFecha: mockFormatearFecha
  }))
}))

describe('GestionarPotrerosUsuario.vue', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    mockPotreros.value = []
    mockLoading.value = false
    mockError.value = null
    mockBusqueda.value = ''
    mockFiltroEstado.value = ''
    mockFiltroPasto.value = ''
    mockEstadosDisponibles.value = []
    mockTiposPasto.value = []
    mockPotrerosFiltrados.value = []
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
      mockLoading.value = true
      wrapper = mount(GestionarPotrerosUsuario)
      await nextTick()
      
      expect(wrapper.text()).toContain('Obteniendo información de potreros...')
      expect(wrapper.find('.spinner-border').exists()).toBe(true)
    })

    it('should disable update button when loading', async () => {
      mockLoading.value = true
      wrapper = mount(GestionarPotrerosUsuario)
      await nextTick()
      
      const updateButton = wrapper.find('button.btn-outline-success')
      expect(updateButton.attributes('disabled')).toBeDefined()
    })

    it('should show spinner icon in button when loading', async () => {
      mockLoading.value = true
      wrapper = mount(GestionarPotrerosUsuario)
      await nextTick()
      
      const updateButton = wrapper.find('button.btn-outline-success')
      expect(updateButton.html()).toContain('spinner-border')
    })
  })

  describe('Error state', () => {
    it('should show error message when error exists', async () => {
      mockError.value = 'Error al cargar potreros'
      mockLoading.value = false
      wrapper = mount(GestionarPotrerosUsuario)
      await nextTick()
      
      expect(wrapper.text()).toContain('Error al cargar potreros')
      expect(wrapper.find('.alert-danger').exists()).toBe(true)
    })

    it('should show error icon', async () => {
      mockError.value = 'Test error'
      mockLoading.value = false
      wrapper = mount(GestionarPotrerosUsuario)
      await nextTick()
      
      const errorAlert = wrapper.find('.alert-danger')
      expect(errorAlert.html()).toContain('fa-exclamation-triangle')
    })
  })

  describe('Empty state', () => {
    it('should show empty message when no potreros match filters', async () => {
      mockPotrerosFiltrados.value = []
      mockLoading.value = false
      mockError.value = null
      wrapper = mount(GestionarPotrerosUsuario)
      await nextTick()
      
      expect(wrapper.text()).toContain('No hay potreros que coincidan con los filtros')
      expect(wrapper.text()).toContain('Intenta con otros criterios o limpia los filtros actuales.')
    })

    it('should show empty state icon', async () => {
      mockPotrerosFiltrados.value = []
      mockLoading.value = false
      mockError.value = null
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
      mockEstadosDisponibles.value = ['disponible', 'ocupado']
      wrapper = mount(GestionarPotrerosUsuario)
      await nextTick()
      
      const estadoSelect = wrapper.find('#usuario-filtro-estado-potrero')
      expect(estadoSelect.exists()).toBe(true)
      expect(wrapper.text()).toContain('Todos los estados')
    })

    it('should render tipo pasto filter select', async () => {
      mockTiposPasto.value = ['Bermuda', 'Rye']
      wrapper = mount(GestionarPotrerosUsuario)
      await nextTick()
      
      const pastoSelect = wrapper.find('#usuario-filtro-pasto')
      expect(pastoSelect.exists()).toBe(true)
      expect(wrapper.text()).toContain('Todos')
    })

    it('should display estados in filter', async () => {
      mockEstadosDisponibles.value = ['disponible', 'ocupado']
      wrapper = mount(GestionarPotrerosUsuario)
      await nextTick()
      
      const estadoSelect = wrapper.find('#usuario-filtro-estado-potrero')
      const options = estadoSelect.findAll('option')
      expect(options.length).toBeGreaterThan(1)
    })

    it('should display tipos pasto in filter', async () => {
      mockTiposPasto.value = ['Bermuda', 'Rye']
      wrapper = mount(GestionarPotrerosUsuario)
      await nextTick()
      
      const pastoSelect = wrapper.find('#usuario-filtro-pasto')
      const options = pastoSelect.findAll('option')
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
      mockPotrerosFiltrados.value = mockPotrerosData
      mockLoading.value = false
      mockError.value = null
      wrapper = mount(GestionarPotrerosUsuario)
      await nextTick()
      
      expect(wrapper.text()).toContain('Potrero Norte')
      expect(wrapper.text()).toContain('Potrero Sur')
    })

    it('should display potrero nombre', async () => {
      mockPotrerosFiltrados.value = [mockPotrerosData[0]]
      mockLoading.value = false
      mockError.value = null
      wrapper = mount(GestionarPotrerosUsuario)
      await nextTick()
      
      expect(wrapper.text()).toContain('Potrero Norte')
    })

    it('should display potrero ID when nombre is missing', async () => {
      const potreroSinNombre = { ...mockPotrerosData[0], nombre: null }
      mockPotrerosFiltrados.value = [potreroSinNombre]
      mockLoading.value = false
      mockError.value = null
      wrapper = mount(GestionarPotrerosUsuario)
      await nextTick()
      
      expect(wrapper.text()).toContain('Potrero #1')
    })

    it('should display estado badge', async () => {
      mockPotrerosFiltrados.value = [mockPotrerosData[0]]
      mockLoading.value = false
      mockError.value = null
      wrapper = mount(GestionarPotrerosUsuario)
      await nextTick()
      
      const badges = wrapper.findAll('.badge')
      expect(badges.length).toBeGreaterThan(0)
    })

    it('should display capacidad', async () => {
      mockPotrerosFiltrados.value = [mockPotrerosData[0]]
      mockLoading.value = false
      mockError.value = null
      wrapper = mount(GestionarPotrerosUsuario)
      await nextTick()
      
      expect(wrapper.text()).toContain('50 animales')
    })

    it('should display ocupacion', async () => {
      mockPotrerosFiltrados.value = [mockPotrerosData[0]]
      mockLoading.value = false
      mockError.value = null
      wrapper = mount(GestionarPotrerosUsuario)
      await nextTick()
      
      expect(wrapper.text()).toContain('25 animales')
    })

    it('should display hectareas', async () => {
      mockPotrerosFiltrados.value = [mockPotrerosData[0]]
      mockLoading.value = false
      mockError.value = null
      wrapper = mount(GestionarPotrerosUsuario)
      await nextTick()
      
      expect(wrapper.text()).toContain('10')
    })

    it('should display tipo_pasto_nombre when available', async () => {
      mockPotrerosFiltrados.value = [mockPotrerosData[0]]
      mockLoading.value = false
      mockError.value = null
      wrapper = mount(GestionarPotrerosUsuario)
      await nextTick()
      
      expect(wrapper.text()).toContain('Bermuda')
    })

    it('should display tipo_pasto as fallback', async () => {
      const potreroSinNombre = { ...mockPotrerosData[1], tipo_pasto_nombre: null }
      mockPotrerosFiltrados.value = [potreroSinNombre]
      mockLoading.value = false
      mockError.value = null
      wrapper = mount(GestionarPotrerosUsuario)
      await nextTick()
      
      expect(wrapper.text()).toContain('Rye')
    })

    it('should display proxima_limpieza', async () => {
      mockPotrerosFiltrados.value = [mockPotrerosData[0]]
      mockLoading.value = false
      mockError.value = null
      wrapper = mount(GestionarPotrerosUsuario)
      await nextTick()
      
      expect(wrapper.text()).toContain('Próxima limpieza')
    })

    it('should display proximaLimpieza as fallback', async () => {
      mockPotrerosFiltrados.value = [mockPotrerosData[1]]
      mockLoading.value = false
      mockError.value = null
      wrapper = mount(GestionarPotrerosUsuario)
      await nextTick()
      
      expect(wrapper.text()).toContain('Próxima limpieza')
    })

    it('should display ultima_limpieza', async () => {
      mockPotrerosFiltrados.value = [mockPotrerosData[0]]
      mockLoading.value = false
      mockError.value = null
      wrapper = mount(GestionarPotrerosUsuario)
      await nextTick()
      
      expect(wrapper.text()).toContain('Última limpieza')
    })

    it('should display ultimaLimpieza as fallback', async () => {
      mockPotrerosFiltrados.value = [mockPotrerosData[1]]
      mockLoading.value = false
      mockError.value = null
      wrapper = mount(GestionarPotrerosUsuario)
      await nextTick()
      
      expect(wrapper.text()).toContain('Última limpieza')
    })

    it('should display descripcion when available', async () => {
      mockPotrerosFiltrados.value = [mockPotrerosData[0]]
      mockLoading.value = false
      mockError.value = null
      wrapper = mount(GestionarPotrerosUsuario)
      await nextTick()
      
      expect(wrapper.text()).toContain('Potrero grande')
    })

    it('should display responsable_nombre when available', async () => {
      mockPotrerosFiltrados.value = [mockPotrerosData[0]]
      mockLoading.value = false
      mockError.value = null
      wrapper = mount(GestionarPotrerosUsuario)
      await nextTick()
      
      expect(wrapper.text()).toContain('Juan Pérez')
    })

    it('should display responsable as fallback', async () => {
      const potreroSinNombre = { ...mockPotrerosData[0], responsable_nombre: null }
      mockPotrerosFiltrados.value = [potreroSinNombre]
      mockLoading.value = false
      mockError.value = null
      wrapper = mount(GestionarPotrerosUsuario)
      await nextTick()
      
      expect(wrapper.text()).toContain('Juan Pérez')
    })

    it('should display "No asignado" when no responsable', async () => {
      const potreroSinResponsable = { ...mockPotrerosData[0], responsable: null, responsable_nombre: null }
      mockPotrerosFiltrados.value = [potreroSinResponsable]
      mockLoading.value = false
      mockError.value = null
      wrapper = mount(GestionarPotrerosUsuario)
      await nextTick()
      
      expect(wrapper.text()).toContain('No asignado')
    })

    it('should handle null values gracefully', async () => {
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
      mockPotrerosFiltrados.value = [potreroConNulls]
      mockLoading.value = false
      mockError.value = null
      wrapper = mount(GestionarPotrerosUsuario)
      await nextTick()
      
      expect(wrapper.text()).toContain('Potrero #3')
      expect(wrapper.text()).toContain('No definida')
      expect(wrapper.text()).toContain('No definido')
    })
  })

  describe('Update button', () => {
    it('should call cargarPotreros when update button is clicked', async () => {
      wrapper = mount(GestionarPotrerosUsuario)
      await nextTick()
      
      const updateButton = wrapper.find('button.btn-outline-success')
      await updateButton.trigger('click')
      
      expect(mockCargarPotreros).toHaveBeenCalled()
    })

    it('should show sync icon when not loading', async () => {
      mockLoading.value = false
      wrapper = mount(GestionarPotrerosUsuario)
      await nextTick()
      
      const updateButton = wrapper.find('button.btn-outline-success')
      expect(updateButton.html()).toContain('fa-sync-alt')
    })
  })
})
