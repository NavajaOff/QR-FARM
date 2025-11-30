import { beforeEach, vi, describe, it, expect } from 'vitest'
import { fetchQrResource, transformEmbeddedPayload } from './qr'
import api from './api.js'

vi.mock('./api.js', () => ({
  default: {
    get: vi.fn()
  }
}))

vi.mock('axios', async () => {
  const actual = await vi.importActual('axios')
  return {
    ...actual,
    default: {
      ...actual.default,
      isAxiosError: vi.fn(),
      isCancel: vi.fn()
    },
    isAxiosError: vi.fn(),
    isCancel: vi.fn()
  }
})

describe('qr service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('fetchQrResource', () => {
    it('should fetch QR resource successfully', async () => {
      const mockResponse = {
        data: {
          status: 'success',
          data: {
            id: '1',
            nombre: 'Vaca Test',
            raza: 'Holstein',
            estado: 'saludable'
          }
        }
      }
      api.get.mockResolvedValue(mockResponse)

      const result = await fetchQrResource({
        endpoint: '/api/ganado',
        resourceId: '1'
      })

      expect(result.id).toBe('1')
      expect(result.nombre).toBe('Vaca Test')
      expect(api.get).toHaveBeenCalled()
    })

    it('should throw error when endpoint is empty', async () => {
      await expect(
        fetchQrResource({
          endpoint: '',
          resourceId: '1'
        })
      ).rejects.toThrow('endpoint')
    })

    it('should throw error when endpoint is only whitespace', async () => {
      await expect(
        fetchQrResource({
          endpoint: '   ',
          resourceId: '1'
        })
      ).rejects.toThrow('endpoint')
    })

    it('should throw error when resourceId is empty', async () => {
      await expect(
        fetchQrResource({
          endpoint: '/api/ganado',
          resourceId: ''
        })
      ).rejects.toThrow('identificador')
    })

    it('should throw error when resourceId and alternatives are all empty', async () => {
      await expect(
        fetchQrResource({
          endpoint: '/api/ganado',
          resourceId: '',
          alternatives: ['', '   ']
        })
      ).rejects.toThrow('identificador')
    })

    it('should handle 404 error', async () => {
      const { isAxiosError } = await import('axios')
      const mockError = {
        response: { status: 404 }
      }
      vi.mocked(isAxiosError).mockReturnValue(true)
      api.get.mockRejectedValue(mockError)

      await expect(
        fetchQrResource({
          endpoint: '/api/ganado',
          resourceId: '999'
        })
      ).rejects.toThrow('registrado')
    })

    it('should handle 403 error', async () => {
      const { isAxiosError } = await import('axios')
      const mockError = {
        response: { status: 403 }
      }
      vi.mocked(isAxiosError).mockReturnValue(true)
      api.get.mockRejectedValue(mockError)

      await expect(
        fetchQrResource({
          endpoint: '/api/ganado',
          resourceId: '1'
        })
      ).rejects.toThrow('autorizado')
    })

    it('should handle 500 error', async () => {
      const { isAxiosError } = await import('axios')
      const mockError = {
        response: { status: 500 }
      }
      vi.mocked(isAxiosError).mockReturnValue(true)
      api.get.mockRejectedValue(mockError)

      await expect(
        fetchQrResource({
          endpoint: '/api/ganado',
          resourceId: '1'
        })
      ).rejects.toThrow('servidor')
    })

    it('should handle network error', async () => {
      const { isAxiosError } = await import('axios')
      const mockError = {
        request: {}
      }
      vi.mocked(isAxiosError).mockReturnValue(true)
      api.get.mockRejectedValue(mockError)

      await expect(
        fetchQrResource({
          endpoint: '/api/ganado',
          resourceId: '1'
        })
      ).rejects.toThrow('conexión')
    })

    it('should handle axios error with message', async () => {
      const { isAxiosError } = await import('axios')
      const mockError = {
        message: 'Custom error message'
      }
      vi.mocked(isAxiosError).mockReturnValue(true)
      api.get.mockRejectedValue(mockError)

      await expect(
        fetchQrResource({
          endpoint: '/api/ganado',
          resourceId: '1'
        })
      ).rejects.toThrow('Custom error message')
    })

    it('should handle request cancellation', async () => {
      const axiosDefault = await import('axios')
      const { isAxiosError } = await import('axios')
      const mockError = {
        message: 'Request cancelled'
      }
      vi.mocked(isAxiosError).mockReturnValue(false)
      vi.mocked(axiosDefault.default.isCancel).mockReturnValue(true)
      api.get.mockRejectedValue(mockError)

      await expect(
        fetchQrResource({
          endpoint: '/api/ganado',
          resourceId: '1',
          signal: new AbortController().signal
        })
      ).rejects.toThrow('cancelada')
    })

    it('should handle non-axios error', async () => {
      const { isAxiosError } = await import('axios')
      const axiosDefault = await import('axios')
      const mockError = new Error('Unknown error')
      vi.mocked(isAxiosError).mockReturnValue(false)
      vi.mocked(axiosDefault.default.isCancel).mockReturnValue(false)
      api.get.mockRejectedValue(mockError)

      await expect(
        fetchQrResource({
          endpoint: '/api/ganado',
          resourceId: '1'
        })
      ).rejects.toThrow('consultar')
    })

    it('should try alternatives when first resourceId fails with 404', async () => {
      const { isAxiosError } = await import('axios')
      const axiosDefault = await import('axios')
      const mockError404 = {
        response: { status: 404 }
      }
      const mockSuccess = {
        data: {
          data: {
            id: '2',
            nombre: 'Vaca Alternative'
          }
        }
      }
      vi.mocked(isAxiosError).mockReturnValue(true)
      vi.mocked(axiosDefault.default.isCancel).mockReturnValue(false)
      api.get
        .mockRejectedValueOnce(mockError404)
        .mockResolvedValueOnce(mockSuccess)

      const result = await fetchQrResource({
        endpoint: '/api/ganado',
        resourceId: '1',
        alternatives: ['2']
      })

      expect(result.id).toBe('2')
      expect(api.get).toHaveBeenCalledTimes(2)
    })

    it('should handle endpoint with {id} placeholder', async () => {
      const mockResponse = {
        data: {
          data: {
            id: '1',
            nombre: 'Test'
          }
        }
      }
      api.get.mockResolvedValue(mockResponse)

      await fetchQrResource({
        endpoint: '/api/ganado/{id}',
        resourceId: '1'
      })

      expect(api.get).toHaveBeenCalledWith('/api/ganado/1', expect.any(Object))
    })

    it('should handle endpoint ending with slash', async () => {
      const mockResponse = {
        data: {
          data: {
            id: '1',
            nombre: 'Test'
          }
        }
      }
      api.get.mockResolvedValue(mockResponse)

      await fetchQrResource({
        endpoint: '/api/ganado/',
        resourceId: '1'
      })

      expect(api.get).toHaveBeenCalledWith('/api/ganado/1', expect.any(Object))
    })

    it('should handle resourceId as number', async () => {
      const mockResponse = {
        data: {
          data: {
            id: '123',
            nombre: 'Test'
          }
        }
      }
      api.get.mockResolvedValue(mockResponse)

      const result = await fetchQrResource({
        endpoint: '/api/ganado',
        resourceId: 123
      })

      expect(result.id).toBe('123')
    })

    it('should handle alternatives with numbers and strings', async () => {
      const mockResponse = {
        data: {
          data: {
            id: '456',
            nombre: 'Test'
          }
        }
      }
      api.get.mockResolvedValue(mockResponse)

      const result = await fetchQrResource({
        endpoint: '/api/ganado',
        resourceId: '1',
        alternatives: [123, '456', '  789  ']
      })

      expect(result.id).toBe('456')
    })

    it('should remove duplicate alternatives', async () => {
      const mockResponse = {
        data: {
          data: {
            id: '1',
            nombre: 'Test'
          }
        }
      }
      api.get.mockResolvedValue(mockResponse)

      await fetchQrResource({
        endpoint: '/api/ganado',
        resourceId: '1',
        alternatives: ['1', '1', '2', '2']
      })

      // Should only try unique values
      expect(api.get).toHaveBeenCalledTimes(1)
    })

    it('should parse complete ganado response', async () => {
      const mockResponse = {
        data: {
          data: {
            id: '1',
            nombre: 'Vaca Test',
            raza: 'Holstein',
            estado: 'saludable',
            estado_salud: 'bueno',
            codigo_qr: 'QR123',
            propietario: {
              nombre: 'Juan Pérez',
              telefono: '1234567890',
              rol: 'propietario'
            },
            potrero: {
              nombre: 'Potrero 1',
              tipo_pasto: 'Bermuda',
              capacidad: 25
            },
            vacunas: [
              {
                id: '1',
                nombre: 'Vacuna A',
                fecha_aplicacion: '2024-01-01',
                estado: 'aplicada'
              }
            ],
            historial: [
              {
                id: '1',
                fecha: '2024-01-15',
                observaciones: 'Revisión general',
                resultado: 'Saludable'
              }
            ]
          }
        }
      }
      api.get.mockResolvedValue(mockResponse)

      const result = await fetchQrResource({
        endpoint: '/api/ganado',
        resourceId: '1'
      })

      expect(result.id).toBe('1')
      expect(result.nombre).toBe('Vaca Test')
      expect(result.raza).toBe('Holstein')
      expect(result.estado).toBe('saludable')
      expect(result.propietario.nombre).toBe('Juan Pérez')
      expect(result.potrero.nombre).toBe('Potrero 1')
      expect(result.vacunas).toHaveLength(1)
      expect(result.historial).toHaveLength(1)
    })

    it('should handle response without nested data', async () => {
      const mockResponse = {
        data: {
          id: '1',
          nombre: 'Direct Data'
        }
      }
      api.get.mockResolvedValue(mockResponse)

      const result = await fetchQrResource({
        endpoint: '/api/ganado',
        resourceId: '1'
      })

      expect(result.id).toBe('1')
      expect(result.nombre).toBe('Direct Data')
    })

    it('should throw error for invalid response structure', async () => {
      const mockResponse = {
        data: null
      }
      api.get.mockResolvedValue(mockResponse)

      // parseGanadoResponse will throw, but it's not an axios error
      // The error should propagate directly
      await expect(
        fetchQrResource({
          endpoint: '/api/ganado',
          resourceId: '1'
        })
      ).rejects.toThrow()
    })

    it('should throw error when response has no id', async () => {
      const mockResponse = {
        data: {
          data: {
            nombre: 'Test'
            // id is missing
          }
        }
      }
      api.get.mockResolvedValue(mockResponse)

      await expect(
        fetchQrResource({
          endpoint: '/api/ganado',
          resourceId: '1'
        })
      ).rejects.toThrow('identificador')
    })
  })

  describe('transformEmbeddedPayload', () => {
    it('should transform embedded payload successfully', () => {
      const payload = {
        id: '1',
        nombre: 'Vaca Test',
        estado: 'saludable',
        codigo: 'QR123'
      }

      const result = transformEmbeddedPayload(payload)

      expect(result.id).toBe('1')
      expect(result.nombre).toBe('Vaca Test')
      expect(result.codigo_qr).toBe('QR123')
    })

    it('should throw error when id is missing', () => {
      const payload = {
        nombre: 'Vaca Test'
      }

      expect(() => transformEmbeddedPayload(payload)).toThrow('identificador')
    })

    it('should throw error when id is null', () => {
      const payload = {
        id: null,
        nombre: 'Vaca Test'
      }

      expect(() => transformEmbeddedPayload(payload)).toThrow('identificador')
    })

    it('should throw error when id is empty string', () => {
      const payload = {
        id: '',
        nombre: 'Vaca Test'
      }

      expect(() => transformEmbeddedPayload(payload)).toThrow('identificador')
    })

    it('should handle id as number', () => {
      const payload = {
        id: 123,
        nombre: 'Vaca Test'
      }

      const result = transformEmbeddedPayload(payload)

      expect(result.id).toBe('123')
    })

    it('should transform complete embedded payload', () => {
      const payload = {
        id: '1',
        nombre: 'Vaca Test',
        estado: 'saludable',
        estado_salud: 'bueno',
        codigo: 'QR123',
        sexo: 'hembra',
        peso: 450,
        fecha_nacimiento: '2020-01-15',
        propietario: {
          nombre: 'Juan Pérez',
          contacto: '1234567890',
          rol: 'propietario'
        },
        potrero: {
          nombre: 'Potrero 1',
          tipo_pasto: 'Bermuda',
          capacidad: 25,
          estado: 'disponible'
        }
      }

      const result = transformEmbeddedPayload(payload)

      expect(result.id).toBe('1')
      expect(result.nombre).toBe('Vaca Test')
      expect(result.estado).toBe('saludable')
      expect(result.estado_salud).toBe('bueno')
      expect(result.codigo_qr).toBe('QR123')
      expect(result.sexo).toBe('hembra')
      expect(result.peso).toBe(450)
      expect(result.propietario.nombre).toBe('Juan Pérez')
      expect(result.propietario.telefono).toBe('1234567890')
      expect(result.potrero.nombre).toBe('Potrero 1')
      expect(result.vacunas).toEqual([])
      expect(result.historial).toEqual([])
    })

    it('should handle null potrero', () => {
      const payload = {
        id: '1',
        nombre: 'Vaca Test',
        potrero: null
      }

      const result = transformEmbeddedPayload(payload)

      expect(result.potrero.nombre).toBeNull()
      expect(result.potrero.tipo_pasto).toBeNull()
      expect(result.potrero.capacidad).toBeNull()
    })

    it('should handle missing potrero', () => {
      const payload = {
        id: '1',
        nombre: 'Vaca Test'
      }

      const result = transformEmbeddedPayload(payload)

      expect(result.potrero.nombre).toBeNull()
      expect(result.potrero.tipo_pasto).toBeNull()
    })

    it('should handle empty string values', () => {
      const payload = {
        id: '1',
        nombre: '   ',
        estado: '',
        codigo: ''
      }

      const result = transformEmbeddedPayload(payload)

      expect(result.nombre).toBeNull()
      expect(result.codigo_qr).toBeNull()
    })

    it('should handle null and undefined values', () => {
      const payload = {
        id: '1',
        nombre: null,
        estado: undefined,
        codigo: null
      }

      const result = transformEmbeddedPayload(payload)

      expect(result.nombre).toBeNull()
      expect(result.codigo_qr).toBeNull()
    })

    it('should use estado_salud as fallback for estado', () => {
      const payload = {
        id: '1',
        estado_salud: 'bueno'
      }

      const result = transformEmbeddedPayload(payload)

      expect(result.estado).toBe('bueno')
      expect(result.estado_salud).toBe('bueno')
    })

    it('should handle date strings in fecha_nacimiento', () => {
      const payload = {
        id: '1',
        fecha_nacimiento: '2020-01-15T00:00:00Z'
      }

      const result = transformEmbeddedPayload(payload)

      expect(result.fecha_nacimiento).toBeTruthy()
      expect(typeof result.fecha_nacimiento).toBe('string')
    })

    it('should handle numeric peso', () => {
      const payload = {
        id: '1',
        peso: 450.5
      }

      const result = transformEmbeddedPayload(payload)

      expect(result.peso).toBe(450.5)
    })

    it('should handle string peso', () => {
      const payload = {
        id: '1',
        peso: '450'
      }

      const result = transformEmbeddedPayload(payload)

      expect(result.peso).toBe(450)
    })

    it('should handle invalid peso', () => {
      const payload = {
        id: '1',
        peso: 'invalid'
      }

      const result = transformEmbeddedPayload(payload)

      expect(result.peso).toBeNull()
    })
  })
})
