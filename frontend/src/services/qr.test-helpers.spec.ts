import { beforeEach, vi, describe, it, expect } from 'vitest'
import {
  createMockGanadoResponse,
  createMockNestedGanadoResponse,
  createMockAxiosError,
  createEmbeddedPayload,
  setupAxiosMocks,
  resetMocks
} from './qr.test-helpers'
import api from './api.js'
import type { GanadoResource } from './qr'

// Mock api.js
vi.mock('./api.js', () => ({
  default: {
    get: vi.fn()
  }
}))

describe('qr.test-helpers', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('createMockGanadoResponse', () => {
    it('should create a mock Ganado response with default values', () => {
      const response = createMockGanadoResponse()

      expect(response).toHaveProperty('data')
      expect(response.data).toHaveProperty('data')
      expect(response.data.data.id).toBe('1')
      expect(response.data.data.nombre).toBe('Vaca Test')
      expect(response.data.data.raza).toBe('Holstein')
      expect(response.data.data.estado).toBe('saludable')
      expect(response.data.data.estado_salud).toBe('bueno')
      expect(response.data.data.codigo_qr).toBe('QR123')
    })

    it('should create a mock Ganado response with overrides', () => {
      const overrides: Partial<GanadoResource> = {
        id: '2',
        nombre: 'Vaca Override',
        raza: 'Angus',
        estado: 'enfermo',
        codigo_qr: 'QR456'
      }

      const response = createMockGanadoResponse(overrides)

      expect(response.data.data.id).toBe('2')
      expect(response.data.data.nombre).toBe('Vaca Override')
      expect(response.data.data.raza).toBe('Angus')
      expect(response.data.data.estado).toBe('enfermo')
      expect(response.data.data.codigo_qr).toBe('QR456')
    })

    it('should create a mock Ganado response with partial overrides', () => {
      const response = createMockGanadoResponse({ nombre: 'Vaca Parcial' })

      expect(response.data.data.id).toBe('1')
      expect(response.data.data.nombre).toBe('Vaca Parcial')
      expect(response.data.data.raza).toBe('Holstein')
    })

    it('should create a mock Ganado response with null values', () => {
      const response = createMockGanadoResponse({
        nombre: null,
        raza: null,
        codigo_qr: null
      })

      expect(response.data.data.nombre).toBeNull()
      expect(response.data.data.raza).toBeNull()
      expect(response.data.data.codigo_qr).toBeNull()
    })
  })

  describe('createMockNestedGanadoResponse', () => {
    it('should create a mock nested Ganado response with default values', () => {
      const response = createMockNestedGanadoResponse()

      expect(response).toHaveProperty('data')
      expect(response.data).toHaveProperty('status', 'success')
      expect(response.data).toHaveProperty('data')
      expect(response.data.data.id).toBe('1')
      expect(response.data.data.nombre).toBe('Vaca Test')
      expect(response.data.data.propietario).toBeDefined()
      expect(response.data.data.propietario.nombre).toBe('Juan Pérez')
      expect(response.data.data.propietario.telefono).toBe('1234567890')
      expect(response.data.data.potrero).toBeDefined()
      expect(response.data.data.potrero.nombre).toBe('Potrero 1')
      expect(response.data.data.vacunas).toEqual([])
      expect(response.data.data.historial).toEqual([])
    })

    it('should create a mock nested Ganado response with id override', () => {
      const response = createMockNestedGanadoResponse({ id: '999' })

      expect(response.data.data.id).toBe('999')
      expect(response.data.data.nombre).toBe('Vaca Test')
    })

    it('should create a mock nested Ganado response with nombre override', () => {
      const response = createMockNestedGanadoResponse({ nombre: 'Vaca Custom' })

      expect(response.data.data.id).toBe('1')
      expect(response.data.data.nombre).toBe('Vaca Custom')
    })

    it('should create a mock nested Ganado response with propietario override', () => {
      const response = createMockNestedGanadoResponse({
        propietario: {
          nombre: 'Pedro García',
          telefono: '9876543210',
          rol: 'dueño'
        }
      })

      expect(response.data.data.propietario.nombre).toBe('Pedro García')
      expect(response.data.data.propietario.telefono).toBe('9876543210')
      expect(response.data.data.propietario.rol).toBe('dueño')
    })

    it('should create a mock nested Ganado response with partial propietario override', () => {
      const response = createMockNestedGanadoResponse({
        propietario: {
          nombre: 'María López'
        }
      })

      expect(response.data.data.propietario.nombre).toBe('María López')
      expect(response.data.data.propietario.telefono).toBe('1234567890')
      expect(response.data.data.propietario.rol).toBe('propietario')
    })

    it('should create a mock nested Ganado response with potrero override', () => {
      const response = createMockNestedGanadoResponse({
        potrero: {
          nombre: 'Potrero 2',
          tipo_pasto: 'Alfalfa',
          capacidad: 50
        }
      })

      expect(response.data.data.potrero.nombre).toBe('Potrero 2')
      expect(response.data.data.potrero.tipo_pasto).toBe('Alfalfa')
      expect(response.data.data.potrero.capacidad).toBe(50)
    })

    it('should create a mock nested Ganado response with vacunas', () => {
      const vacunas = [
        {
          id: '1',
          nombre: 'Vacuna A',
          fecha_aplicacion: '2024-01-01',
          proxima_dosis: null,
          estado: 'aplicada',
          responsable: null
        }
      ]

      const response = createMockNestedGanadoResponse({ vacunas })

      expect(response.data.data.vacunas).toHaveLength(1)
      expect(response.data.data.vacunas[0].nombre).toBe('Vacuna A')
    })

    it('should create a mock nested Ganado response with historial', () => {
      const historial = [
        {
          id: '1',
          fecha: '2024-01-15',
          observaciones: 'Revisión general',
          resultado: 'Saludable',
          veterinario: null
        }
      ]

      const response = createMockNestedGanadoResponse({ historial })

      expect(response.data.data.historial).toHaveLength(1)
      expect(response.data.data.historial[0].resultado).toBe('Saludable')
    })

    it('should create a mock nested Ganado response with all overrides', () => {
      const response = createMockNestedGanadoResponse({
        id: '999',
        nombre: 'Vaca Completa',
        propietario: {
          nombre: 'Test Owner'
        },
        potrero: {
          nombre: 'Test Potrero'
        },
        vacunas: [],
        historial: []
      })

      expect(response.data.data.id).toBe('999')
      expect(response.data.data.nombre).toBe('Vaca Completa')
      expect(response.data.data.propietario.nombre).toBe('Test Owner')
      expect(response.data.data.potrero.nombre).toBe('Test Potrero')
    })
  })

  describe('createMockAxiosError', () => {
    it('should create a mock axios error with status', () => {
      const error = createMockAxiosError({ status: 404 })

      expect(error.response).toBeDefined()
      expect(error.response.status).toBe(404)
    })

    it('should create a mock axios error with request', () => {
      const error = createMockAxiosError({ request: true })

      expect(error.request).toBeDefined()
      expect(error.request).toEqual({})
    })

    it('should create a mock axios error without request', () => {
      const error = createMockAxiosError({ request: false })

      expect(error.request).toBeUndefined()
    })

    it('should create a mock axios error with message', () => {
      const error = createMockAxiosError({ message: 'Custom error' })

      expect(error.message).toBe('Custom error')
    })

    it('should create a mock axios error with isCancel', () => {
      const error = createMockAxiosError({ isCancel: true })

      expect(error.isCancel).toBe(true)
    })

    it('should create a mock axios error with all properties', () => {
      const error = createMockAxiosError({
        status: 500,
        request: true,
        message: 'Server error',
        isCancel: true
      })

      expect(error.response.status).toBe(500)
      expect(error.request).toBeDefined()
      expect(error.message).toBe('Server error')
      expect(error.isCancel).toBe(true)
    })

    it('should create a mock axios error with empty config', () => {
      const error = createMockAxiosError()

      expect(error).toEqual({})
    })

    it('should create a mock axios error with only status 403', () => {
      const error = createMockAxiosError({ status: 403 })

      expect(error.response.status).toBe(403)
      expect(error.request).toBeUndefined()
      expect(error.message).toBeUndefined()
    })

    it('should create a mock axios error with only message', () => {
      const error = createMockAxiosError({ message: 'Network error' })

      expect(error.message).toBe('Network error')
      expect(error.response).toBeUndefined()
    })
  })

  describe('createEmbeddedPayload', () => {
    it('should create a mock embedded payload with default values', () => {
      const payload = createEmbeddedPayload()

      expect(payload.id).toBe('1')
      expect(payload.nombre).toBe('Vaca Test')
      expect(payload.estado).toBe('saludable')
      expect(payload.codigo).toBe('QR123')
    })

    it('should create a mock embedded payload with overrides', () => {
      const payload = createEmbeddedPayload({
        id: '2',
        nombre: 'Vaca Override',
        estado: 'enfermo',
        codigo: 'QR456'
      })

      expect(payload.id).toBe('2')
      expect(payload.nombre).toBe('Vaca Override')
      expect(payload.estado).toBe('enfermo')
      expect(payload.codigo).toBe('QR456')
    })

    it('should create a mock embedded payload with partial overrides', () => {
      const payload = createEmbeddedPayload({ nombre: 'Vaca Parcial' })

      expect(payload.id).toBe('1')
      expect(payload.nombre).toBe('Vaca Parcial')
      expect(payload.estado).toBe('saludable')
    })

    it('should create a mock embedded payload with propietario', () => {
      const payload = createEmbeddedPayload({
        propietario: {
          nombre: 'Juan Pérez',
          contacto: '1234567890',
          rol: 'owner'
        }
      })

      expect(payload.propietario).toBeDefined()
      expect(payload.propietario?.nombre).toBe('Juan Pérez')
      expect(payload.propietario?.contacto).toBe('1234567890')
    })

    it('should create a mock embedded payload with potrero', () => {
      const payload = createEmbeddedPayload({
        potrero: {
          nombre: 'Potrero 1',
          tipo_pasto: 'Bermuda',
          capacidad: 25
        }
      })

      expect(payload.potrero).toBeDefined()
      expect(payload.potrero?.nombre).toBe('Potrero 1')
      expect(payload.potrero?.tipo_pasto).toBe('Bermuda')
    })

    it('should create a mock embedded payload with null potrero', () => {
      const payload = createEmbeddedPayload({
        potrero: null
      })

      expect(payload.potrero).toBeNull()
    })
  })

  describe('setupAxiosMocks', () => {
    it('should setup axios mocks and return mocked functions', async () => {
      const mocks = await setupAxiosMocks()

      expect(mocks).toHaveProperty('isAxiosError')
      expect(mocks).toHaveProperty('isCancel')
      expect(typeof mocks.isAxiosError).toBe('function')
      expect(typeof mocks.isCancel).toBe('function')
    })

    it('should return vi.mocked functions', async () => {
      const mocks = await setupAxiosMocks()

      // Verify they are vi.mocked functions
      expect(vi.isMockFunction(mocks.isAxiosError)).toBe(true)
      expect(vi.isMockFunction(mocks.isCancel)).toBe(true)
    })
  })

  describe('resetMocks', () => {
    it('should reset all mocks', () => {
      // Set up some mock calls
      if (api?.get) {
        api.get.mockResolvedValueOnce({ data: { data: { id: '1' } } })

        // Call resetMocks
        resetMocks()

        // Verify mocks are reset
        expect(api.get).not.toHaveBeenCalled()
      } else {
        // If api is not available, just verify resetMocks doesn't throw
        expect(() => resetMocks()).not.toThrow()
      }
    })

    it('should clear all mocks and reset api.get', () => {
      if (api?.get) {
        // Make some calls
        api.get.mockResolvedValue({ data: { data: { id: '1' } } })
        api.get('/test')

        // Reset
        resetMocks()

        // Verify api.get is reset
        expect(api.get.mock.calls.length).toBe(0)
      } else {
        // If api is not available, just verify resetMocks doesn't throw
        expect(() => resetMocks()).not.toThrow()
      }
    })
  })

  describe('api export', () => {
    it('should export api', () => {
      // api is imported directly from './api.js' which is mocked
      expect(api).toBeDefined()
      expect(api.get).toBeDefined()
      expect(typeof api.get).toBe('function')
    })

    it('should export api with mocked get method', () => {
      // api.get should be a vi.fn() mock
      expect(vi.isMockFunction(api.get)).toBe(true)
    })
  })
})

