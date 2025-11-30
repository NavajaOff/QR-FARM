import { mount } from '@vue/test-utils'
import { vi } from 'vitest'
import { registroVacunacionBase } from './registro-vacunacion-base.js'

// Mock de API
vi.mock('../../services/api.js', () => ({
  vacunacionAPI: {
    getAll: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn()
  },
  ganadoAPI: {
    getAll: vi.fn()
  },
  userAPI: {
    getAll: vi.fn()
  }
}))

// Mock de fetch
globalThis.fetch = vi.fn()

// Mock de Swal
globalThis.Swal = {
  fire: vi.fn()
}

describe('registro-vacunacion-base.js', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    console.error = vi.fn()
    console.log = vi.fn()

    // Mock fetch response
    globalThis.fetch.mockResolvedValue({
      json: () => Promise.resolve({ data: [] })
    })
  })

  const createWrapper = (options = {}) => {
    const component = {
      ...registroVacunacionBase,
      name: 'TestComponent',
      template: '<div></div>',
      ...options
    }

    return mount(component)
  }

  describe('Data Function', () => {
    it('should return default data', () => {
      const data = registroVacunacionBase.data()
      expect(data.filtros).toEqual({
        animal: '',
        vacuna: '',
        fechaDesde: '',
        fechaHasta: ''
      })
      expect(data.vacunaciones).toEqual([])
      expect(data.animales).toEqual([])
      expect(data.tiposVacuna).toEqual([])
      expect(data.personas).toEqual([])
      expect(data.loading).toBe(false)
    })
  })

  describe('Computed filteredVacunaciones', () => {
    it('should filter by animal name', () => {
      wrapper = createWrapper()
      wrapper.vm.vacunaciones = [
        { id: 1, idAnimal: 1, nombre: 'Animal 1', tipoVacuna: 'Vacuna A', fechaAplicacion: '2023-01-01T00:00:00' },
        { id: 2, idAnimal: 2, nombre: 'Animal 2', tipoVacuna: 'Vacuna B', fechaAplicacion: '2023-01-02T00:00:00' }
      ]
      wrapper.vm.filtros.animal = 'Animal 1'

      expect(wrapper.vm.filteredVacunaciones).toHaveLength(1)
      expect(wrapper.vm.filteredVacunaciones[0].id).toBe(1)
    })

    it('should filter by vaccine type', () => {
      wrapper = createWrapper()
      wrapper.vm.vacunaciones = [
        { id: 1, tipoVacuna: 'Vacuna A' },
        { id: 2, tipoVacuna: 'Vacuna B' }
      ]
      wrapper.vm.filtros.vacuna = 'Vacuna A'

      expect(wrapper.vm.filteredVacunaciones).toHaveLength(1)
      expect(wrapper.vm.filteredVacunaciones[0].id).toBe(1)
    })

    it('should filter by date range', () => {
      wrapper = createWrapper()
      wrapper.vm.vacunaciones = [
        { id: 1, fechaAplicacion: '2023-01-01T00:00:00' },
        { id: 2, fechaAplicacion: '2023-01-15T00:00:00' },
        { id: 3, fechaAplicacion: '2023-01-30T00:00:00' }
      ]
      wrapper.vm.filtros.fechaDesde = '2023-01-10'
      wrapper.vm.filtros.fechaHasta = '2023-01-20'

      expect(wrapper.vm.filteredVacunaciones).toHaveLength(1)
      expect(wrapper.vm.filteredVacunaciones[0].id).toBe(2)
    })
  })

  describe('cargarDatos Method', () => {
    it('should load data successfully', async () => {
      const { vacunacionAPI, ganadoAPI, userAPI } = await import('../../services/api.js')
      vacunacionAPI.getAll.mockResolvedValue({ data: { data: [{ id: 1 }] } })
      ganadoAPI.getAll.mockResolvedValue({ data: { data: [{ id: 1 }] } })
      userAPI.getAll.mockResolvedValue({ data: { data: [{ id: 1 }] } })

      wrapper = createWrapper()
      await wrapper.vm.cargarDatos()

      expect(wrapper.vm.vacunaciones).toEqual([{ id: 1 }])
      expect(wrapper.vm.animales).toEqual([{ id: 1 }])
      expect(wrapper.vm.personas).toEqual([{ id: 1 }])
      expect(wrapper.vm.loading).toBe(false)
    })

    it('should handle errors', async () => {
      const { vacunacionAPI } = await import('../../services/api.js')
      vacunacionAPI.getAll.mockRejectedValue(new Error('API error'))

      wrapper = createWrapper()
      await wrapper.vm.cargarDatos()

      expect(Swal.fire).toHaveBeenCalledWith('Error', 'No se pudieron cargar los datos', 'error')
      expect(wrapper.vm.loading).toBe(false)
    })
  })

  describe('obtenerTiposVacuna Method', () => {
    it('should fetch vaccine types', async () => {
      globalThis.fetch.mockResolvedValue({
        json: () => Promise.resolve({ data: [{ id: 1, nombre: 'Vacuna A' }] })
      })

      wrapper = createWrapper()
      await wrapper.vm.obtenerTiposVacuna()

      expect(wrapper.vm.tiposVacuna).toEqual([{ id: 1, nombre: 'Vacuna A' }])
    })

    it('should handle fetch errors', async () => {
      globalThis.fetch.mockRejectedValue(new Error('Fetch error'))

      wrapper = createWrapper()
      await wrapper.vm.obtenerTiposVacuna()

      expect(console.error).toHaveBeenCalled()
    })
  })

  describe('estadoClass Method', () => {
    it('should return correct classes', () => {
      wrapper = createWrapper()

      expect(wrapper.vm.estadoClass('aplicado')).toBe('bg-success')
      expect(wrapper.vm.estadoClass('pendiente')).toBe('bg-warning')
      expect(wrapper.vm.estadoClass('unknown')).toBe('bg-secondary')
    })
  })

  describe('estadoLabel Method', () => {
    it('should return correct labels', () => {
      wrapper = createWrapper()

      expect(wrapper.vm.estadoLabel('aplicado')).toBe('Aplicado')
      expect(wrapper.vm.estadoLabel('pendiente')).toBe('Pendiente')
      expect(wrapper.vm.estadoLabel('unknown')).toBe('unknown')
      expect(wrapper.vm.estadoLabel(null)).toBe('Sin estado')
    })
  })

  describe('formatDate Method', () => {
    it('should format date correctly', () => {
      wrapper = createWrapper()

      expect(wrapper.vm.formatDate('2023-01-01T00:00:00')).toBe('2023-01-01')
      expect(wrapper.vm.formatDate(null)).toBe('No definida')
    })
  })

  describe('generarReporte Method', () => {
    it('should show info message', () => {
      wrapper = createWrapper()
      wrapper.vm.generarReporte()

      expect(Swal.fire).toHaveBeenCalledWith('Reporte PDF', 'Funcionalidad de reporte próximamente', 'info')
    })
  })

  describe('verVacunacion Method', () => {
    it('should show vaccination details', () => {
      wrapper = createWrapper()
      wrapper.vm.vacunaciones = [{
        id: 1,
        nombre: 'Animal 1',
        tipoVacuna: 'Vacuna A',
        fechaAplicacion: '2023-01-01T00:00:00',
        proximaDosis: '2023-02-01T00:00:00',
        responsable: 'Persona 1',
        estado: 'aplicado'
      }]

      wrapper.vm.verVacunacion(1)

      expect(Swal.fire).toHaveBeenCalled()
    })

    it('should do nothing if vaccination not found', () => {
      wrapper = createWrapper()
      wrapper.vm.verVacunacion(999)

      expect(Swal.fire).not.toHaveBeenCalled()
    })
  })

  describe('eliminarVacunacion Method', () => {
    beforeEach(() => {
      vi.useFakeTimers()
    })

    afterEach(() => {
      vi.useRealTimers()
    })

    it('should delete vaccination after confirmation', async () => {
      const { vacunacionAPI } = await import('../../services/api.js')
      Swal.fire.mockResolvedValue({ isConfirmed: true })
      vacunacionAPI.delete.mockResolvedValue({})

      wrapper = createWrapper()
      await wrapper.vm.eliminarVacunacion(1)

      expect(vacunacionAPI.delete).toHaveBeenCalledWith(1)
      expect(Swal.fire).toHaveBeenCalledWith('Eliminado', 'La vacunación ha sido eliminada correctamente', 'success')
    })

    it('should not delete if not confirmed', async () => {
      const { vacunacionAPI } = await import('../../services/api.js')
      Swal.fire.mockResolvedValue({ isConfirmed: false })

      wrapper = createWrapper()
      await wrapper.vm.eliminarVacunacion(1)

      expect(vacunacionAPI.delete).not.toHaveBeenCalled()
    })
  })
})