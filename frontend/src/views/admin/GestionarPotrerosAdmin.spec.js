import { mount } from '@vue/test-utils'
import { beforeEach, vi, describe, it, expect } from 'vitest'
import { ref } from 'vue'

// Mock authService
vi.mock('../../services/authService.js', () => ({
  default: {
    getRole: vi.fn(() => 'admin')
  }
}))

// Mock TenantSelector
vi.mock('../../components/TenantSelector.vue', () => ({
  default: {
    name: 'TenantSelector',
    template: '<div>TenantSelector</div>'
  }
}))

// Create reactive refs for testing
const mockCurrentIndex = ref(0)
const mockAccordionOpen = ref(true)
const mockPotreros = ref([])
const mockLoading = ref(false)
const mockError = ref(null)

const mockCargarPotreros = vi.fn()
const mockCrearPotrero = vi.fn()
const mockEditarPotrero = vi.fn()
const mockPrevPotrero = vi.fn()
const mockNextPotrero = vi.fn()
const mockToggleAccordion = vi.fn()
const mockEstadoClass = vi.fn(() => 'badge-success')
const mockCargarDatosIniciales = vi.fn()

// Mock gestionar-potreros.js
vi.mock('../../assets/js/gestionar-potreros.js', () => ({
  currentIndex: mockCurrentIndex,
  accordionOpen: mockAccordionOpen,
  potreros: mockPotreros,
  tiposPasto: { value: [] },
  estadosPotrero: { value: [] },
  personasUsuario: { value: [] },
  loading: mockLoading,
  error: mockError,
  cargarDatosIniciales: mockCargarDatosIniciales,
  cargarPotreros: mockCargarPotreros,
  crearPotrero: mockCrearPotrero,
  editarPotrero: mockEditarPotrero,
  prevPotrero: mockPrevPotrero,
  nextPotrero: mockNextPotrero,
  toggleAccordion: mockToggleAccordion,
  estadoClass: mockEstadoClass,
  actualizarProximaLimpieza: vi.fn()
}))

// Mock gestionar-potreros-admin.js
vi.mock('../../assets/js/gestionar-potreros-admin.js', () => ({
  default: {
    name: 'GestionarPotreros',
    setup: vi.fn(() => ({
      currentIndex: mockCurrentIndex,
      accordionOpen: mockAccordionOpen,
      potreros: mockPotreros,
      tiposPasto: { value: [] },
      estadosPotrero: { value: [] },
      personasUsuario: { value: [] },
      loading: mockLoading,
      error: mockError,
      cargarDatosIniciales: mockCargarDatosIniciales,
      cargarPotreros: mockCargarPotreros,
      crearPotrero: mockCrearPotrero,
      editarPotrero: mockEditarPotrero,
      prevPotrero: mockPrevPotrero,
      nextPotrero: mockNextPotrero,
      toggleAccordion: mockToggleAccordion,
      estadoClass: mockEstadoClass,
      actualizarProximaLimpieza: vi.fn()
    })),
    computed: {},
    methods: {}
  }
}))

// Import after mocks
import GestionarPotrerosAdmin from './GestionarPotrerosAdmin.vue'
import authService from '../../services/authService.js'

describe('GestionarPotrerosAdmin.vue', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    mockCurrentIndex.value = 0
    mockAccordionOpen.value = true
    mockPotreros.value = []
    mockLoading.value = false
    mockError.value = null
    authService.getRole.mockReturnValue('admin')
  })

  const createWrapper = () => {
    return mount(GestionarPotrerosAdmin)
  }

  describe('Component Rendering', () => {
    it('should mount successfully', () => {
      wrapper = createWrapper()
      expect(wrapper.exists()).toBe(true)
    })

    it('should render the title', () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('Gestionar Potreros')
    })

    it('should render TenantSelector when user is super_admin', async () => {
      authService.getRole.mockReturnValue('super_admin')
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      
      const tenantSelector = wrapper.findComponent({ name: 'TenantSelector' })
      expect(tenantSelector.exists()).toBe(true)
    })

    it('should not render TenantSelector when user is not super_admin', async () => {
      authService.getRole.mockReturnValue('admin')
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      
      const tenantSelector = wrapper.findComponent({ name: 'TenantSelector' })
      expect(tenantSelector.exists()).toBe(false)
    })
  })

  describe('Loading State', () => {
    it('should show loading spinner when loading is true', async () => {
      mockLoading.value = true
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const spinner = wrapper.find('.spinner-border')
      expect(spinner.exists()).toBe(true)
      expect(wrapper.text()).toContain('Cargando potreros...')
    })
  })

  describe('Error State', () => {
    it('should show error message when error exists', async () => {
      mockError.value = 'Error al cargar potreros'
      mockLoading.value = false
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const errorAlert = wrapper.find('.alert-danger')
      expect(errorAlert.exists()).toBe(true)
      expect(errorAlert.text()).toContain('Error al cargar potreros')
    })

    it('should call cargarPotreros when retry button is clicked', async () => {
      mockError.value = 'Error al cargar potreros'
      mockLoading.value = false
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const retryButton = wrapper.find('button.btn-outline-danger')
      expect(retryButton.exists()).toBe(true)
      
      await retryButton.trigger('click')
      expect(mockCargarPotreros).toHaveBeenCalled()
    })
  })

  describe('Empty State', () => {
    it('should show empty state when potreros array is empty', async () => {
      mockPotreros.value = []
      mockLoading.value = false
      mockError.value = null
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('No hay potreros registrados')
      expect(wrapper.text()).toContain('Aún no se han creado potreros en el sistema.')
    })

    it('should call crearPotrero when "Crear Primer Potrero" button is clicked', async () => {
      mockPotreros.value = []
      mockLoading.value = false
      mockError.value = null
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const createButton = wrapper.find('button.btn-success')
      expect(createButton.exists()).toBe(true)
      expect(createButton.text()).toContain('Crear Primer Potrero')
      
      await createButton.trigger('click')
      expect(mockCrearPotrero).toHaveBeenCalled()
    })
  })

  describe('Potreros Display', () => {
    it('should display potrero card when potreros exist', async () => {
      mockPotreros.value = [{
        id: 1,
        nombre: 'Potrero 1',
        estado: 'disponible',
        capacidad: 25,
        ocupacion: 10,
        hectareas: 5,
        fechaUso: '2024-01-15',
        responsable: 'Juan Pérez',
        proximaLimpieza: '2024-12-31',
        area: 50000,
        ultimaLimpieza: '2024-01-01',
        descripcion: 'Potrero principal'
      }]
      mockLoading.value = false
      mockError.value = null
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const card = wrapper.find('.card')
      expect(card.exists()).toBe(true)
      expect(card.text()).toContain('Potrero 1')
    })

    it('should display potrero details correctly', async () => {
      mockPotreros.value = [{
        id: 1,
        nombre: 'Potrero 1',
        estado: 'disponible',
        capacidad: 25,
        ocupacion: 10,
        hectareas: 5,
        fechaUso: '2024-01-15',
        responsable: 'Juan Pérez',
        proximaLimpieza: '2024-12-31',
        area: 50000,
        ultimaLimpieza: '2024-01-01',
        descripcion: 'Potrero principal'
      }]
      mockLoading.value = false
      mockError.value = null
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('Estado:')
      expect(wrapper.text()).toContain('Capacidad:')
      expect(wrapper.text()).toContain('Ocupación:')
      expect(wrapper.text()).toContain('Hectáreas:')
      expect(wrapper.text()).toContain('Fecha de último uso:')
      expect(wrapper.text()).toContain('Responsable:')
      expect(wrapper.text()).toContain('Próxima limpieza:')
      expect(wrapper.text()).toContain('Área:')
      expect(wrapper.text()).toContain('Última limpieza:')
      expect(wrapper.text()).toContain('Descripción:')
    })

    it('should show "No definida" for missing capacidad', async () => {
      mockPotreros.value = [{
        id: 1,
        nombre: 'Potrero 1',
        capacidad: null
      }]
      mockLoading.value = false
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('No definida')
    })

    it('should show "No registrada" for missing fechaUso', async () => {
      mockPotreros.value = [{
        id: 1,
        nombre: 'Potrero 1',
        fechaUso: null
      }]
      mockLoading.value = false
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('No registrada')
    })

    it('should show "No programada" for missing proximaLimpieza', async () => {
      mockPotreros.value = [{
        id: 1,
        nombre: 'Potrero 1',
        proximaLimpieza: null
      }]
      mockLoading.value = false
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('No programada')
    })

    it('should not show descripcion section when descripcion is missing', async () => {
      mockPotreros.value = [{
        id: 1,
        nombre: 'Potrero 1',
        descripcion: null
      }]
      mockLoading.value = false
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      // Descripción section should not be visible when descripcion is null/undefined
      const descripcionSection = wrapper.find('.row.g-3.mb-3')
      // The v-if="potreros[currentIndex].descripcion" should hide it
      expect(wrapper.html()).not.toContain('Descripción:')
    })
  })

  describe('Navigation Buttons', () => {
    it('should call prevPotrero when previous button is clicked', async () => {
      mockPotreros.value = [
        { id: 1, nombre: 'Potrero 1' },
        { id: 2, nombre: 'Potrero 2' }
      ]
      mockLoading.value = false
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const prevButton = wrapper.findAll('button.btn-outline-secondary')[0]
      await prevButton.trigger('click')
      expect(mockPrevPotrero).toHaveBeenCalled()
    })

    it('should call nextPotrero when next button is clicked', async () => {
      mockPotreros.value = [
        { id: 1, nombre: 'Potrero 1' },
        { id: 2, nombre: 'Potrero 2' }
      ]
      mockLoading.value = false
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const nextButton = wrapper.findAll('button.btn-outline-secondary')[1]
      await nextButton.trigger('click')
      expect(mockNextPotrero).toHaveBeenCalled()
    })

    it('should disable navigation buttons when only one potrero exists', async () => {
      mockPotreros.value = [{ id: 1, nombre: 'Potrero 1' }]
      mockLoading.value = false
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const buttons = wrapper.findAll('button.btn-outline-secondary')
      buttons.forEach(button => {
        expect(button.attributes('disabled')).toBeDefined()
      })
    })
  })

  describe('Accordion Toggle', () => {
    it('should call toggleAccordion when accordion button is clicked', async () => {
      mockPotreros.value = [{ id: 1, nombre: 'Potrero 1' }]
      mockLoading.value = false
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const toggleButton = wrapper.find('button.btn-light.btn-sm')
      await toggleButton.trigger('click')
      expect(mockToggleAccordion).toHaveBeenCalled()
    })

    it('should show chevron-up icon when accordion is open', async () => {
      mockAccordionOpen.value = true
      mockPotreros.value = [{ id: 1, nombre: 'Potrero 1' }]
      mockLoading.value = false
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const toggleButton = wrapper.find('button.btn-light.btn-sm')
      const icon = toggleButton.find('i.fa-chevron-up')
      expect(icon.exists()).toBe(true)
    })

    it('should show chevron-down icon when accordion is closed', async () => {
      mockAccordionOpen.value = false
      mockPotreros.value = [{ id: 1, nombre: 'Potrero 1' }]
      mockLoading.value = false
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const toggleButton = wrapper.find('button.btn-light.btn-sm')
      const icon = toggleButton.find('i.fa-chevron-down')
      expect(icon.exists()).toBe(true)
    })
  })

  describe('Action Buttons', () => {
    it('should call editarPotrero when edit button is clicked', async () => {
      mockPotreros.value = [{ id: 1, nombre: 'Potrero 1' }]
      mockLoading.value = false
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const editButton = wrapper.find('button.btn-primary')
      await editButton.trigger('click')
      expect(mockEditarPotrero).toHaveBeenCalledWith(1)
    })

    it('should call crearPotrero when create button is clicked', async () => {
      mockPotreros.value = [{ id: 1, nombre: 'Potrero 1' }]
      mockLoading.value = false
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const createButtons = wrapper.findAll('button.btn-success')
      const createButton = createButtons.find(btn => btn.text().includes('Crear Potrero'))
      await createButton.trigger('click')
      expect(mockCrearPotrero).toHaveBeenCalled()
    })
  })

  describe('Tenant Change Handler', () => {
    it('should call cargarPotreros when tenant changes', async () => {
      authService.getRole.mockReturnValue('super_admin')
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const tenantSelector = wrapper.findComponent({ name: 'TenantSelector' })
      await tenantSelector.vm.$emit('tenant-changed')
      
      expect(mockCargarPotreros).toHaveBeenCalled()
    })
  })

  describe('Computed Properties', () => {
    it('should return true for isSuperAdmin when role is super_admin', async () => {
      authService.getRole.mockReturnValue('super_admin')
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.isSuperAdmin).toBe(true)
    })

    it('should return false for isSuperAdmin when role is not super_admin', async () => {
      authService.getRole.mockReturnValue('admin')
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.isSuperAdmin).toBe(false)
    })
  })
})

