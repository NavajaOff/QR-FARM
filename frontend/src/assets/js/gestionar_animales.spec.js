import { vi } from 'vitest'
import {
  currentIndex,
  accordionOpen,
  animales,
  estadosGanado,
  personasUsuario,
  loading,
  error,
  cargarDatosIniciales,
  cargarAnimales,
  calcularEdad,
  formatDate,
  estadoClass,
  iconClass,
  prevAnimal,
  nextAnimal,
  toggleAccordion,
  resetEstado
} from './gestionar_animales.js'

// Mock axios
vi.mock('axios', () => ({
  default: {
    get: vi.fn(),
    CancelToken: {
      source: vi.fn(() => ({
        token: { reason: null },
        cancel: vi.fn()
      }))
    },
    isCancel: vi.fn(() => false)
  },
  __esModule: true
}))

// Mock fetch
globalThis.fetch = vi.fn()

// Mock Swal
globalThis.Swal = {
  fire: vi.fn()
}

// Mock socket.io-client
vi.mock('socket.io-client', () => ({
  default: vi.fn(() => ({
    on: vi.fn(),
    emit: vi.fn()
  }))
}))

// Mock gestionar-potreros.js
vi.mock('./gestionar-potreros.js', () => ({
  potreros: { value: [] },
  cargarDatosIniciales: vi.fn(),
  cargarPotreros: vi.fn()
}))

describe('gestionar_animales.js', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    console.error = vi.fn()
    console.log = vi.fn()

    // Reset reactive values
    currentIndex.value = 0
    accordionOpen.value = true
    animales.value = []
    estadosGanado.value = []
    personasUsuario.value = []
    loading.value = true
    error.value = null
  })

  describe('Reactive Variables', () => {
    it('should initialize reactive variables', () => {
      expect(currentIndex.value).toBe(0)
      expect(accordionOpen.value).toBe(true)
      expect(animales.value).toEqual([])
      expect(estadosGanado.value).toEqual([])
      expect(personasUsuario.value).toEqual([])
      expect(loading.value).toBe(true)
      expect(error.value).toBeNull()
    })
  })

  describe('calcularEdad Function', () => {
    it('should calculate age correctly', () => {
      const birthDate = '2020-01-01'
      const age = calcularEdad(birthDate)
      const expectedAge = new Date().getFullYear() - 2020
      expect(age).toBe(expectedAge)
    })

    it('should return NaN for invalid date', () => {
      const age = calcularEdad(null)
      expect(Number.isNaN(age)).toBe(true)
    })
  })

  describe('formatDate Function', () => {
    it('should format date correctly', () => {
      const dateString = '2023-10-15'
      const formatted = formatDate(dateString)
      expect(formatted).toMatch(/^\d{2}\/\d{2}\/\d{4}$/)
    })

    it('should return empty string for invalid date', () => {
      const formatted = formatDate(null)
      expect(formatted).toBe('')
    })
  })

  describe('estadoClass Function', () => {
    it('should return correct class for saludable', () => {
      expect(estadoClass('saludable')).toBe('bg-success')
    })

    it('should return correct class for revision', () => {
      expect(estadoClass('revision')).toBe('bg-warning')
    })

    it('should return correct class for enfermo', () => {
      expect(estadoClass('enfermo')).toBe('bg-danger')
    })

    it('should return default class for unknown estado', () => {
      expect(estadoClass('unknown')).toBe('bg-secondary')
    })
  })

  describe('iconClass Function', () => {
    it('should return correct class for activo', () => {
      expect(iconClass({ estado: 'activo' })).toBe('text-success')
    })

    it('should return correct class for en_tratamiento', () => {
      expect(iconClass({ estado: 'en_tratamiento' })).toBe('text-warning')
    })

    it('should return default class for unknown estado', () => {
      expect(iconClass({ estado: 'unknown' })).toBe('text-danger')
    })
  })

  describe('Navigation Functions', () => {
    beforeEach(() => {
      animales.value = [
        { id: 1, nombre: 'Animal 1' },
        { id: 2, nombre: 'Animal 2' },
        { id: 3, nombre: 'Animal 3' }
      ]
    })

    it('should navigate to previous animal', () => {
      currentIndex.value = 1
      prevAnimal()
      expect(currentIndex.value).toBe(0)
      expect(accordionOpen.value).toBe(true)
    })

    it('should navigate to next animal', () => {
      currentIndex.value = 1
      nextAnimal()
      expect(currentIndex.value).toBe(2)
      expect(accordionOpen.value).toBe(true)
    })

    it('should wrap around to last animal when going previous from first', () => {
      currentIndex.value = 0
      prevAnimal()
      expect(currentIndex.value).toBe(2)
    })

    it('should wrap around to first animal when going next from last', () => {
      currentIndex.value = 2
      nextAnimal()
      expect(currentIndex.value).toBe(0)
    })

    it('should not navigate if only one animal', () => {
      animales.value = [{ id: 1, nombre: 'Animal 1' }]
      currentIndex.value = 0
      prevAnimal()
      expect(currentIndex.value).toBe(0)
    })
  })

  describe('toggleAccordion Function', () => {
    it('should toggle accordion state', () => {
      expect(accordionOpen.value).toBe(true)
      toggleAccordion()
      expect(accordionOpen.value).toBe(false)
      toggleAccordion()
      expect(accordionOpen.value).toBe(true)
    })
  })

  describe('resetEstado Function', () => {
    it('should reset all state variables', () => {
      // Set some values
      loading.value = false
      error.value = 'test error'
      animales.value = [{ id: 1 }]
      estadosGanado.value = [{ estado: 'test' }]
      personasUsuario.value = [{ id: 1 }]

      resetEstado()

      expect(loading.value).toBe(true)
      expect(error.value).toBeNull()
      expect(animales.value).toEqual([])
      expect(estadosGanado.value).toEqual([])
      expect(personasUsuario.value).toEqual([])
    })
  })

  describe('cargarAnimales Function', () => {
    it('should load animals successfully', async () => {
      const mockResponse = {
        data: {
          success: true,
          data: [
            {
              id: 1,
              nombre: 'Test Animal',
              peso: 450,
              raza: 'Holstein',
              fecha_nacimiento: '2020-01-01',
              sexo: 'hembra',
              id_estado: 1,
              id_potrero: 1,
              id_persona: 1,
              estado_tipo: 'saludable',
              codigo_qr: 'QR123'
            }
          ]
        }
      }

      const axios = (await import('axios')).default
      axios.get.mockResolvedValue(mockResponse)

      await cargarAnimales()

      expect(animales.value).toHaveLength(1)
      expect(animales.value[0].nombre).toBe('Test Animal')
      expect(loading.value).toBe(false)
    })

    it('should handle API errors', async () => {
      // Mock axios to reject
      const axios = (await import('axios')).default
      axios.get.mockRejectedValue(new Error('Network error'))

      await cargarAnimales()

      expect(error.value).toBe('Network error')
      expect(loading.value).toBe(false)
    })

    it('should filter animals based on incluirBajas', async () => {
      const mockResponse = {
        data: {
          success: true,
          data: [
            { id: 1, id_estado: 1 }, // activo
            { id: 2, id_estado: 4 }  // dado de baja
          ]
        }
      }

      const axios = (await import('axios')).default
      axios.get.mockResolvedValue(mockResponse)

      await cargarAnimales(false) // incluirBajas = false
      expect(animales.value).toHaveLength(1)
      expect(animales.value[0].id).toBe(1)

      await cargarAnimales(true) // incluirBajas = true
      expect(animales.value).toHaveLength(1)
      expect(animales.value[0].id).toBe(2)
    })
  })

  describe('cargarDatosIniciales Function', () => {
    it('should load initial data', async () => {
      const mockPotreros = await import('./gestionar-potreros.js')
      mockPotreros.cargarDatosIniciales.mockResolvedValue()

      const axios = (await import('axios')).default
      axios.get.mockResolvedValue({ data: { success: true, data: [] } })

      await cargarDatosIniciales()

      expect(mockPotreros.cargarDatosIniciales).toHaveBeenCalled()
      expect(loading.value).toBe(false)
    })
  })
})
