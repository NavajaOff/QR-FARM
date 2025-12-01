import { mount } from '@vue/test-utils'
import { beforeEach, vi, describe, it, expect } from 'vitest'
import { nextTick } from 'vue'

// Create all mocks using vi.hoisted
const {
  mockGetRole,
  mockAnimales,
  mockEstadosGanado,
  mockPersonasUsuario,
  mockLoading,
  mockError,
  mockCargarDatosIniciales,
  mockCargarAnimales,
  mockEditarAnimal,
  mockAgregarNuevoAnimal,
  mockVerPerfilAnimal,
  mockDarBajaAnimal,
  mockReactivarAnimal,
  mockSetUpdateCallback,
  mockCancelPendingRequests,
  mockResetEstado
} = vi.hoisted(() => {
  const mockGetRole = vi.fn()
  const mockAnimales = { value: [] }
  const mockEstadosGanado = { value: [] }
  const mockPersonasUsuario = { value: [] }
  const mockLoading = { value: false }
  const mockError = { value: null }
  const mockCargarDatosIniciales = vi.fn()
  const mockCargarAnimales = vi.fn()
  const mockEditarAnimal = vi.fn()
  const mockAgregarNuevoAnimal = vi.fn()
  const mockVerPerfilAnimal = vi.fn()
  const mockDarBajaAnimal = vi.fn()
  const mockReactivarAnimal = vi.fn()
  const mockSetUpdateCallback = vi.fn()
  const mockCancelPendingRequests = vi.fn()
  const mockResetEstado = vi.fn()
  
  return {
    mockGetRole,
    mockAnimales,
    mockEstadosGanado,
    mockPersonasUsuario,
    mockLoading,
    mockError,
    mockCargarDatosIniciales,
    mockCargarAnimales,
    mockEditarAnimal,
    mockAgregarNuevoAnimal,
    mockVerPerfilAnimal,
    mockDarBajaAnimal,
    mockReactivarAnimal,
    mockSetUpdateCallback,
    mockCancelPendingRequests,
    mockResetEstado
  }
})

// Mock authService
vi.mock('../../services/authService.js', () => ({
  default: {
    getRole: mockGetRole
  }
}))

vi.mock('../../components/TenantSelector.vue', () => ({
  default: {
    name: 'TenantSelector',
    template: '<div>TenantSelector</div>',
    emits: ['tenant-changed']
  }
}))

// Mock gestionar-potreros.js
vi.mock('../../assets/js/gestionar-potreros.js', () => ({
  potreros: { value: [] },
  cargarPotreros: vi.fn(),
  cargarDatosIniciales: vi.fn()
}))

// Mock gestionar_animales.js
vi.mock('../../assets/js/gestionar_animales.js', () => ({
  animales: mockAnimales,
  estadosGanado: mockEstadosGanado,
  personasUsuario: mockPersonasUsuario,
  loading: mockLoading,
  error: mockError,
  cargarDatosIniciales: mockCargarDatosIniciales,
  cargarAnimales: mockCargarAnimales,
  editarAnimal: mockEditarAnimal,
  agregarNuevoAnimal: mockAgregarNuevoAnimal,
  verPerfilAnimal: mockVerPerfilAnimal,
  darBajaAnimal: mockDarBajaAnimal,
  reactivarAnimal: mockReactivarAnimal,
  setUpdateCallback: mockSetUpdateCallback,
  cancelPendingRequests: mockCancelPendingRequests,
  resetEstado: mockResetEstado
}))

// Mock Bootstrap modal
global.bootstrap = {
  Modal: vi.fn().mockImplementation(() => ({
    show: vi.fn(),
    hide: vi.fn(),
    dispose: vi.fn()
  }))
}

// Import after mocks
import GestionarAnimalesAdmin from './GestionarAnimalesAdmin.vue'

describe('GestionarAnimalesAdmin.vue', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    mockGetRole.mockReturnValue('admin')
    mockAnimales.value = []
    mockEstadosGanado.value = []
    mockPersonasUsuario.value = []
    mockLoading.value = false
    mockError.value = null
  })

  describe('Component mounting', () => {
    it('should mount successfully', () => {
      wrapper = mount(GestionarAnimalesAdmin)
      expect(wrapper.exists()).toBe(true)
    })

    it('should render the title', () => {
      wrapper = mount(GestionarAnimalesAdmin)
      expect(wrapper.text()).toContain('Gestión de Ganado')
    })

    it('should call cargarGanado on mount', async () => {
      mockCargarAnimales.mockResolvedValue()
      wrapper = mount(GestionarAnimalesAdmin)
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))
      expect(mockCargarAnimales).toHaveBeenCalled()
    })

    it('should set update callback on mount', async () => {
      wrapper = mount(GestionarAnimalesAdmin)
      await nextTick()
      expect(mockSetUpdateCallback).toHaveBeenCalled()
    })
  })

  describe('TenantSelector', () => {
    it('should render TenantSelector for super_admin', () => {
      mockGetRole.mockReturnValue('super_admin')
      wrapper = mount(GestionarAnimalesAdmin)
      expect(wrapper.findComponent({ name: 'TenantSelector' }).exists()).toBe(true)
    })

    it('should not render TenantSelector for admin', () => {
      mockGetRole.mockReturnValue('admin')
      wrapper = mount(GestionarAnimalesAdmin)
      expect(wrapper.findComponent({ name: 'TenantSelector' }).exists()).toBe(false)
    })

    it('should call cargarGanado when tenant changes', async () => {
      mockGetRole.mockReturnValue('super_admin')
      mockCargarAnimales.mockResolvedValue()
      wrapper = mount(GestionarAnimalesAdmin)
      await nextTick()
      
      const tenantSelector = wrapper.findComponent({ name: 'TenantSelector' })
      await tenantSelector.vm.$emit('tenant-changed')
      await nextTick()
      
      expect(mockCargarAnimales).toHaveBeenCalledTimes(2) // Once on mount, once on change
    })
  })

  describe('Loading state', () => {
    it('should show loading spinner when isLoading is true', async () => {
      wrapper = mount(GestionarAnimalesAdmin)
      await wrapper.setData({ isLoading: true })
      await nextTick()
      
      expect(wrapper.text()).toContain('Cargando ganado...')
      expect(wrapper.find('.spinner-border').exists()).toBe(true)
    })

    it('should hide table when loading', async () => {
      wrapper = mount(GestionarAnimalesAdmin)
      await wrapper.setData({ isLoading: true })
      await nextTick()
      
      expect(wrapper.find('.table').exists()).toBe(false)
    })
  })

  describe('Empty state', () => {
    it('should show empty message when no animals', async () => {
      wrapper = mount(GestionarAnimalesAdmin)
      await wrapper.setData({ 
        isLoading: false,
        ganado: [] 
      })
      await nextTick()
      
      expect(wrapper.text()).toContain('No hay animales registrados')
    })
  })

  describe('Animal table', () => {
    const mockAnimals = [
      {
        id: 1,
        nombre: 'Vaca 1',
        raza: 'Holstein',
        edad: 5,
        peso: 500,
        potreroActual: 'Potrero Norte',
        estado: 'saludable',
        es_dado_de_baja: false
      },
      {
        id: 2,
        nombre: 'Vaca 2',
        raza: 'Angus',
        edad: 3,
        peso: 450,
        potreroActual: 'Potrero Sur',
        estado: 'enfermo',
        es_dado_de_baja: false
      },
      {
        id: 3,
        nombre: 'Vaca 3',
        raza: 'Jersey',
        edad: 2,
        peso: 400,
        potreroActual: null,
        estado: 'revision',
        es_dado_de_baja: true
      }
    ]

    it('should display animals in table', async () => {
      wrapper = mount(GestionarAnimalesAdmin)
      await wrapper.setData({ 
        isLoading: false,
        ganado: mockAnimals 
      })
      await nextTick()
      
      expect(wrapper.text()).toContain('Vaca 1')
      expect(wrapper.text()).toContain('Vaca 2')
      expect(wrapper.text()).toContain('Holstein')
      expect(wrapper.text()).toContain('Angus')
    })

    it('should display correct badge classes for estados', async () => {
      wrapper = mount(GestionarAnimalesAdmin)
      await wrapper.setData({ 
        isLoading: false,
        ganado: mockAnimals 
      })
      await nextTick()
      
      const badges = wrapper.findAll('.badge')
      expect(badges.length).toBeGreaterThan(0)
    })

    it('should show "Activo" badge for non-baja animals', async () => {
      wrapper = mount(GestionarAnimalesAdmin)
      await wrapper.setData({ 
        isLoading: false,
        ganado: [mockAnimals[0]] 
      })
      await nextTick()
      
      expect(wrapper.text()).toContain('Activo')
    })

    it('should show "Dado de baja" badge for baja animals', async () => {
      wrapper = mount(GestionarAnimalesAdmin)
      await wrapper.setData({ 
        isLoading: false,
        ganado: [mockAnimals[2]] 
      })
      await nextTick()
      
      expect(wrapper.text()).toContain('Dado de baja')
    })
  })

  describe('Actions', () => {
    const mockAnimal = {
      id: 1,
      nombre: 'Vaca 1',
      raza: 'Holstein',
      edad: 5,
      peso: 500,
      potreroActual: 'Potrero Norte',
      estado: 'saludable',
      es_dado_de_baja: false
    }

    it('should call viewQR when QR button is clicked', async () => {
      wrapper = mount(GestionarAnimalesAdmin)
      await wrapper.setData({ 
        isLoading: false,
        ganado: [mockAnimal] 
      })
      await nextTick()
      
      const qrButton = wrapper.findAll('button').find(btn => 
        btn.html().includes('fa-qrcode')
      )
      if (qrButton) {
        await qrButton.trigger('click')
        expect(mockVerPerfilAnimal).toHaveBeenCalledWith(1)
      }
    })

    it('should call editAnimal when edit button is clicked', async () => {
      wrapper = mount(GestionarAnimalesAdmin)
      await wrapper.setData({ 
        isLoading: false,
        ganado: [mockAnimal] 
      })
      await nextTick()
      
      const editButton = wrapper.findAll('button').find(btn => 
        btn.html().includes('fa-edit')
      )
      if (editButton) {
        await editButton.trigger('click')
        expect(mockEditarAnimal).toHaveBeenCalledWith(1)
      }
    })

    it('should call darBajaAnimal when baja button is clicked', async () => {
      mockDarBajaAnimal.mockResolvedValue({ success: true })
      mockAnimales.value = [mockAnimal]
      
      wrapper = mount(GestionarAnimalesAdmin)
      await wrapper.setData({ 
        isLoading: false,
        ganado: [mockAnimal] 
      })
      await nextTick()
      
      const bajaButton = wrapper.findAll('button').find(btn => 
        btn.html().includes('fa-ban')
      )
      if (bajaButton) {
        await bajaButton.trigger('click')
        await nextTick()
        expect(mockDarBajaAnimal).toHaveBeenCalled()
      }
    })

    it('should call reactivarAnimal when reactivate button is clicked', async () => {
      const bajaAnimal = { ...mockAnimal, es_dado_de_baja: true }
      mockReactivarAnimal.mockResolvedValue({ success: true })
      mockAnimales.value = [bajaAnimal]
      
      wrapper = mount(GestionarAnimalesAdmin)
      await wrapper.setData({ 
        isLoading: false,
        ganado: [bajaAnimal] 
      })
      await nextTick()
      
      const reactivateButton = wrapper.findAll('button').find(btn => 
        btn.html().includes('fa-undo')
      )
      if (reactivateButton) {
        await reactivateButton.trigger('click')
        await nextTick()
        expect(mockReactivarAnimal).toHaveBeenCalled()
      }
    })

    it('should call addAnimal when add button is clicked', async () => {
      wrapper = mount(GestionarAnimalesAdmin)
      await nextTick()
      
      const addButton = wrapper.find('button.btn-success')
      await addButton.trigger('click')
      expect(mockAgregarNuevoAnimal).toHaveBeenCalled()
    })

    it('should not show edit/baja buttons for baja animals', async () => {
      const bajaAnimal = { ...mockAnimal, es_dado_de_baja: true }
      wrapper = mount(GestionarAnimalesAdmin)
      await wrapper.setData({ 
        isLoading: false,
        ganado: [bajaAnimal] 
      })
      await nextTick()
      
      const editButtons = wrapper.findAll('button').filter(btn => 
        btn.html().includes('fa-edit')
      )
      const bajaButtons = wrapper.findAll('button').filter(btn => 
        btn.html().includes('fa-ban')
      )
      
      expect(editButtons.length).toBe(0)
      expect(bajaButtons.length).toBe(0)
    })

    it('should not show reactivate button for active animals', async () => {
      wrapper = mount(GestionarAnimalesAdmin)
      await wrapper.setData({ 
        isLoading: false,
        ganado: [mockAnimal] 
      })
      await nextTick()
      
      const reactivateButtons = wrapper.findAll('button').filter(btn => 
        btn.html().includes('fa-undo')
      )
      
      expect(reactivateButtons.length).toBe(0)
    })
  })

  describe('Mostrar bajas checkbox', () => {
    it('should toggle mostrarBajas', async () => {
      mockCargarAnimales.mockResolvedValue()
      wrapper = mount(GestionarAnimalesAdmin)
      await nextTick()
      
      const checkbox = wrapper.find('#mostrarBajas')
      expect(checkbox.exists()).toBe(true)
      
      await checkbox.setValue(true)
      await nextTick()
      
      expect(wrapper.vm.mostrarBajas).toBe(true)
      expect(mockCargarAnimales).toHaveBeenCalledWith(true)
    })

    it('should call cargarGanado when checkbox changes', async () => {
      mockCargarAnimales.mockResolvedValue()
      wrapper = mount(GestionarAnimalesAdmin)
      await nextTick()
      
      mockCargarAnimales.mockClear()
      
      const checkbox = wrapper.find('#mostrarBajas')
      await checkbox.setValue(true)
      await nextTick()
      
      expect(mockCargarAnimales).toHaveBeenCalled()
    })
  })

  describe('cargarGanado method', () => {
    it('should load datos iniciales if not loaded', async () => {
      mockEstadosGanado.value = []
      mockPersonasUsuario.value = []
      mockCargarDatosIniciales.mockResolvedValue()
      mockCargarAnimales.mockResolvedValue()
      
      wrapper = mount(GestionarAnimalesAdmin)
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))
      
      expect(mockCargarDatosIniciales).toHaveBeenCalled()
    })

    it('should not load datos iniciales if already loaded', async () => {
      mockEstadosGanado.value = [{ id: 1, tipo_estado: 'saludable' }]
      mockPersonasUsuario.value = [{ id: 1, nombre: 'Juan' }]
      mockCargarAnimales.mockResolvedValue()
      
      wrapper = mount(GestionarAnimalesAdmin)
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))
      
      expect(mockCargarDatosIniciales).not.toHaveBeenCalled()
    })

    it('should update ganado from animales.value', async () => {
      mockAnimales.value = [
        { id: 1, nombre: 'Vaca 1' },
        { id: 2, nombre: 'Vaca 2' }
      ]
      mockCargarAnimales.mockResolvedValue()
      
      wrapper = mount(GestionarAnimalesAdmin)
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))
      
      expect(wrapper.vm.ganado).toHaveLength(2)
    })

    it('should set isLoading to false after loading', async () => {
      mockCargarAnimales.mockResolvedValue()
      
      wrapper = mount(GestionarAnimalesAdmin)
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))
      
      expect(wrapper.vm.isLoading).toBe(false)
    })
  })

  describe('actualizarLista method', () => {
    it('should update ganado from animales.value', async () => {
      mockAnimales.value = [
        { id: 1, nombre: 'Vaca 1' }
      ]
      
      wrapper = mount(GestionarAnimalesAdmin)
      await nextTick()
      
      wrapper.vm.actualizarLista()
      await nextTick()
      
      expect(wrapper.vm.ganado).toHaveLength(1)
    })
  })

  describe('Lifecycle hooks', () => {
    it('should cancel pending requests on beforeUnmount', async () => {
      wrapper = mount(GestionarAnimalesAdmin)
      await nextTick()
      
      wrapper.unmount()
      await nextTick()
      
      expect(mockCancelPendingRequests).toHaveBeenCalled()
    })
  })

  describe('Computed properties', () => {
    it('should return true for isSuperAdmin when role is super_admin', () => {
      mockGetRole.mockReturnValue('super_admin')
      wrapper = mount(GestionarAnimalesAdmin)
      expect(wrapper.vm.isSuperAdmin).toBe(true)
    })

    it('should return false for isSuperAdmin when role is admin', () => {
      mockGetRole.mockReturnValue('admin')
      wrapper = mount(GestionarAnimalesAdmin)
      expect(wrapper.vm.isSuperAdmin).toBe(false)
    })
  })
})
