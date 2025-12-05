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

    it('should handle peso as null', () => {
      const payload = {
        id: '1',
        peso: null
      }

      const result = transformEmbeddedPayload(payload)

      expect(result.peso).toBeNull()
    })

    it('should handle peso as undefined', () => {
      const payload = {
        id: '1',
        peso: undefined
      }

      const result = transformEmbeddedPayload(payload)

      expect(result.peso).toBeNull()
    })

    it('should handle peso as boolean false', () => {
      const payload = {
        id: '1',
        peso: false
      }

      const result = transformEmbeddedPayload(payload)

      // toNullableNumber convierte false a 0
      expect(result.peso).toBe(0)
    })

    it('should handle peso as boolean true', () => {
      const payload = {
        id: '1',
        peso: true
      }

      const result = transformEmbeddedPayload(payload)

      // toNullableNumber convierte true a 1
      expect(result.peso).toBe(1)
    })

    it('should handle peso as object', () => {
      const payload = {
        id: '1',
        peso: { value: 450 }
      }

      const result = transformEmbeddedPayload(payload)

      expect(result.peso).toBeNull()
    })

    it('should handle date strings in fecha_nacimiento that are already ISO', () => {
      const payload = {
        id: '1',
        fecha_nacimiento: '2020-01-15T00:00:00.000Z'
      }

      const result = transformEmbeddedPayload(payload)

      expect(result.fecha_nacimiento).toBeTruthy()
    })

    it('should handle invalid date strings in fecha_nacimiento', () => {
      const payload = {
        id: '1',
        fecha_nacimiento: 'invalid-date'
      }

      const result = transformEmbeddedPayload(payload)

      expect(result.fecha_nacimiento).toBe('invalid-date')
    })

    it('should handle fecha_nacimiento as number', () => {
      const payload = {
        id: '1',
        fecha_nacimiento: 1579046400000 // Unix timestamp
      }

      const result = transformEmbeddedPayload(payload)

      expect(result.fecha_nacimiento).toBeTruthy()
    })

    it('should handle fecha_nacimiento as Date object', () => {
      const payload = {
        id: '1',
        fecha_nacimiento: new Date('2020-01-15')
      }

      const result = transformEmbeddedPayload(payload)

      expect(result.fecha_nacimiento).toBeTruthy()
    })

    it('should handle invalid fecha_nacimiento number', () => {
      const payload = {
        id: '1',
        fecha_nacimiento: Number.NaN
      }

      const result = transformEmbeddedPayload(payload)

      expect(result.fecha_nacimiento).toBeNull()
    })

    it('should handle propietario with contacto instead of telefono', () => {
      const payload = {
        id: '1',
        propietario: {
          nombre: 'Juan',
          contacto: '1234567890',
          rol: 'owner'
        }
      }

      const result = transformEmbeddedPayload(payload)

      expect(result.propietario.telefono).toBe('1234567890')
    })

    it('should handle propietario with both contacto and telefono', () => {
      const payload = {
        id: '1',
        propietario: {
          nombre: 'Juan',
          contacto: '1234567890',
          telefono: '0987654321',
          rol: 'owner'
        }
      }

      const result = transformEmbeddedPayload(payload)

      expect(result.propietario.telefono).toBe('1234567890') // contacto takes precedence
    })

    it('should handle empty propietario values', () => {
      const payload = {
        id: '1',
        propietario: {
          nombre: '   ',
          contacto: '',
          rol: null
        }
      }

      const result = transformEmbeddedPayload(payload)

      expect(result.propietario.nombre).toBeNull()
      expect(result.propietario.telefono).toBeNull()
      expect(result.propietario.rol).toBeNull()
    })

    it('should handle potrero with all fields null', () => {
      const payload = {
        id: '1',
        potrero: {
          nombre: null,
          tipo_pasto: null,
          ultima_limpieza: null,
          fecha_ultimo_uso: null,
          proxima_limpieza: null,
          capacidad: null,
          estado: null
        }
      }

      const result = transformEmbeddedPayload(payload)

      expect(result.potrero.nombre).toBeNull()
      expect(result.potrero.tipo_pasto).toBeNull()
      expect(result.potrero.capacidad).toBeNull()
    })

    it('should handle potrero with date fields', () => {
      const payload = {
        id: '1',
        potrero: {
          nombre: 'Potrero 1',
          ultima_limpieza: '2024-01-15',
          fecha_ultimo_uso: '2024-01-10',
          proxima_limpieza: '2024-12-31',
          capacidad: 25,
          estado: 'disponible'
        }
      }

      const result = transformEmbeddedPayload(payload)

      expect(result.potrero.nombre).toBe('Potrero 1')
      expect(result.potrero.ultima_limpieza).toBeTruthy()
      expect(result.potrero.fecha_ultimo_uso).toBeTruthy()
      expect(result.potrero.proxima_limpieza).toBeTruthy()
      expect(result.potrero.capacidad).toBe(25)
    })

    it('should handle potrero capacidad as string number', () => {
      const payload = {
        id: '1',
        potrero: {
          capacidad: '25'
        }
      }

      const result = transformEmbeddedPayload(payload)

      expect(result.potrero.capacidad).toBe(25)
    })

    it('should handle potrero capacidad as invalid string', () => {
      const payload = {
        id: '1',
        potrero: {
          capacidad: 'invalid'
        }
      }

      const result = transformEmbeddedPayload(payload)

      expect(result.potrero.capacidad).toBeNull()
    })

    it('should handle potrero capacidad as Infinity', () => {
      const payload = {
        id: '1',
        potrero: {
          capacidad: Infinity
        }
      }

      const result = transformEmbeddedPayload(payload)

      expect(result.potrero.capacidad).toBeNull()
    })

    it('should handle potrero capacidad as -Infinity', () => {
      const payload = {
        id: '1',
        potrero: {
          capacidad: -Infinity
        }
      }

      const result = transformEmbeddedPayload(payload)

      expect(result.potrero.capacidad).toBeNull()
    })

    it('should handle potrero capacidad as NaN', () => {
      const payload = {
        id: '1',
        potrero: {
          capacidad: Number.NaN
        }
      }

      const result = transformEmbeddedPayload(payload)

      expect(result.potrero.capacidad).toBeNull()
    })

    it('should handle id as number zero', () => {
      const payload = {
        id: 0,
        nombre: 'Test'
      }

      // toNullableString convierte 0 a "0", que es válido (no es null ni undefined)
      const result = transformEmbeddedPayload(payload)
      expect(result.id).toBe('0')
    })

    it('should handle id as string zero', () => {
      const payload = {
        id: '0',
        nombre: 'Test'
      }

      // "0" es un string válido, no se considera vacío
      const result = transformEmbeddedPayload(payload)
      expect(result.id).toBe('0')
    })

    it('should handle id as empty string after trim', () => {
      const payload = {
        id: '   ',
        nombre: 'Test'
      }

      expect(() => transformEmbeddedPayload(payload)).toThrow('identificador')
    })

    it('should handle id as boolean', () => {
      const payload = {
        id: true,
        nombre: 'Test'
      }

      const result = transformEmbeddedPayload(payload)

      expect(result.id).toBe('true')
    })

    it('should handle id as object', () => {
      const payload = {
        id: { value: '1' },
        nombre: 'Test'
      }

      const result = transformEmbeddedPayload(payload)

      expect(result.id).toBe('{"value":"1"}')
    })

    it('should handle nombre as boolean', () => {
      const payload = {
        id: '1',
        nombre: false
      }

      const result = transformEmbeddedPayload(payload)

      expect(result.nombre).toBe('false')
    })

    it('should handle nombre as number', () => {
      const payload = {
        id: '1',
        nombre: 123
      }

      const result = transformEmbeddedPayload(payload)

      expect(result.nombre).toBe('123')
    })

    it('should handle estado_salud without estado', () => {
      const payload = {
        id: '1',
        estado_salud: 'bueno'
      }

      const result = transformEmbeddedPayload(payload)

      expect(result.estado).toBe('bueno')
      expect(result.estado_salud).toBe('bueno')
    })

    it('should handle estado without estado_salud', () => {
      const payload = {
        id: '1',
        estado: 'saludable'
      }

      const result = transformEmbeddedPayload(payload)

      expect(result.estado).toBe('saludable')
      expect(result.estado_salud).toBeNull()
    })

    it('should handle codigo as number', () => {
      const payload = {
        id: '1',
        codigo: 12345
      }

      const result = transformEmbeddedPayload(payload)

      expect(result.codigo_qr).toBe('12345')
    })

    it('should handle codigo as boolean', () => {
      const payload = {
        id: '1',
        codigo: true
      }

      const result = transformEmbeddedPayload(payload)

      expect(result.codigo_qr).toBe('true')
    })

    it('should handle codigo as object', () => {
      const payload = {
        id: '1',
        codigo: { value: 'QR123' }
      }

      const result = transformEmbeddedPayload(payload)

      expect(result.codigo_qr).toBe('{"value":"QR123"}')
    })

    it('should handle sexo as number', () => {
      const payload = {
        id: '1',
        sexo: 1
      }

      const result = transformEmbeddedPayload(payload)

      expect(result.sexo).toBe('1')
    })

    it('should handle sexo as boolean', () => {
      const payload = {
        id: '1',
        sexo: false
      }

      const result = transformEmbeddedPayload(payload)

      expect(result.sexo).toBe('false')
    })

    it('should handle fetchQrResource with alternatives that all fail with non-404', async () => {
      const { isAxiosError } = await import('axios')
      const mockError500 = {
        response: { status: 500 }
      }
      vi.mocked(isAxiosError).mockReturnValue(true)
      api.get
        .mockRejectedValueOnce(mockError500)
        .mockRejectedValueOnce(mockError500)

      await expect(
        fetchQrResource({
          endpoint: '/api/ganado',
          resourceId: '1',
          alternatives: ['2']
        })
      ).rejects.toThrow('servidor')
    })

    it('should handle fetchQrResource with alternatives where second succeeds', async () => {
      const { isAxiosError } = await import('axios')
      const mockError404 = {
        response: { status: 404 },
        isAxiosError: true
      }
      const mockSuccess = {
        data: {
          status: 'success',
          data: {
            id: '2',
            nombre: 'Vaca Alternative'
          }
        }
      }
      vi.mocked(isAxiosError).mockImplementation((error: any) => {
        return error?.isAxiosError === true || error?.response !== undefined
      })
      api.get.mockReset()
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

    it('should handle fetchQrResource with all alternatives failing 404', async () => {
      const { isAxiosError } = await import('axios')
      const mockError404 = {
        response: { status: 404 },
        isAxiosError: true
      }
      vi.mocked(isAxiosError).mockImplementation((error: any) => {
        return error?.isAxiosError === true || error?.response !== undefined
      })
      api.get.mockReset()
      // Con el nuevo código, se priorizan alternatives primero: ['2', '3', '1']
      // Para candidatos numéricos, se intenta primero por QR y luego por ID
      // Para '2': QR -> 404, ID -> 404
      // Para '3': QR -> 404, ID -> 404  
      // Para '1': QR -> 404, ID -> 404
      // Total: 6 llamadas (pero el orden es ['2', '3', '1'] según alternatives primero)
      api.get
        .mockRejectedValueOnce(mockError404) // '2' QR (alternatives primero)
        .mockRejectedValueOnce(mockError404) // '2' ID
        .mockRejectedValueOnce(mockError404) // '3' QR
        .mockRejectedValueOnce(mockError404) // '3' ID
        .mockRejectedValueOnce(mockError404) // '1' QR (resourceId)
        .mockRejectedValueOnce(mockError404) // '1' ID

      await expect(
        fetchQrResource({
          endpoint: '/api/ganado',
          resourceId: '1',
          alternatives: ['2', '3']
        })
      ).rejects.toThrow(/registrado|consultar/)
    })

    it('should handle fetchQrResource with empty alternatives array', async () => {
      const mockResponse = {
        data: {
          status: 'success',
          data: {
            id: '1',
            nombre: 'Test'
          }
        }
      }
      api.get.mockReset()
      api.get.mockResolvedValue(mockResponse)

      const result = await fetchQrResource({
        endpoint: '/api/ganado',
        resourceId: '1',
        alternatives: []
      })

      expect(result.id).toBe('1')
      expect(api.get).toHaveBeenCalledTimes(1)
    })

    it('should handle fetchQrResource with alternative as number', async () => {
      const { isAxiosError } = await import('axios')
      const mockError404 = {
        response: { status: 404 },
        isAxiosError: true
      }
      const mockResponse = {
        data: {
          status: 'success',
          data: {
            id: '123',
            nombre: 'Test'
          }
        }
      }
      vi.mocked(isAxiosError).mockImplementation((error: any) => {
        return error?.isAxiosError === true || error?.response !== undefined
      })
      api.get.mockReset()
      api.get
        .mockRejectedValueOnce(mockError404)
        .mockResolvedValueOnce(mockResponse)

      const result = await fetchQrResource({
        endpoint: '/api/ganado',
        resourceId: '1',
        alternatives: [123]
      })

      expect(result.id).toBe('123')
    })

    it('should handle fetchQrResource with alternative as number zero', async () => {
      const { isAxiosError } = await import('axios')
      const mockError404 = {
        response: { status: 404 },
        isAxiosError: true
      }
      vi.mocked(isAxiosError).mockImplementation((error: any) => {
        return error?.isAxiosError === true || error?.response !== undefined
      })
      api.get.mockReset()
      // '0' se convierte a "0", que es numérico, así que intenta QR e ID
      // '1' también es numérico, así que intenta QR e ID
      // Total: 4 llamadas
      api.get
        .mockRejectedValueOnce(mockError404) // '0' QR
        .mockRejectedValueOnce(mockError404) // '0' ID
        .mockRejectedValueOnce(mockError404) // '1' QR
        .mockRejectedValueOnce(mockError404) // '1' ID

      await expect(
        fetchQrResource({
          endpoint: '/api/ganado',
          resourceId: '1',
          alternatives: [0]
        })
      ).rejects.toThrow(/registrado|consultar|obligatorio/)
    })

    it('should handle fetchQrResource with whitespace in alternatives', async () => {
      const mockResponse = {
        data: {
          data: {
            id: '1',
            nombre: 'Test'
          }
        }
      }
      api.get.mockResolvedValue(mockResponse)

      const result = await fetchQrResource({
        endpoint: '/api/ganado',
        resourceId: '1',
        alternatives: ['   ', '  2  ', '2']
      })

      expect(result.id).toBe('1')
      // Should filter whitespace and duplicates
      expect(api.get).toHaveBeenCalledTimes(1)
    })

    it('should handle fetchQrResource with non-string non-number alternative', async () => {
      const mockResponse = {
        data: {
          data: {
            id: '1',
            nombre: 'Test'
          }
        }
      }
      api.get.mockResolvedValue(mockResponse)

      const result = await fetchQrResource({
        endpoint: '/api/ganado',
        resourceId: '1',
        alternatives: [null, undefined, {}, []]
      })

      expect(result.id).toBe('1')
      expect(api.get).toHaveBeenCalledTimes(1)
    })

    it('should handle parseGanadoResponse with nested data structure', async () => {
      const mockResponse = {
        data: {
          status: 'success',
          data: {
            id: '1',
            nombre: 'Vaca Test'
          }
        }
      }
      api.get.mockResolvedValue(mockResponse)

      const result = await fetchQrResource({
        endpoint: '/api/ganado',
        resourceId: '1'
      })

      expect(result.id).toBe('1')
    })

    it('should handle parseGanadoResponse when data.data is null', async () => {
      const mockResponse = {
        data: {
          status: 'success',
          data: null
        }
      }
      api.get.mockResolvedValue(mockResponse)

      await expect(
        fetchQrResource({
          endpoint: '/api/ganado',
          resourceId: '1'
        })
      ).rejects.toThrow('válida')
    })

    it('should handle parseGanadoResponse when response is not object', async () => {
      const mockResponse = {
        data: null
      }
      api.get.mockResolvedValue(mockResponse)

      await expect(
        fetchQrResource({
          endpoint: '/api/ganado',
          resourceId: '1'
        })
      ).rejects.toThrow('válida')
    })

    it('should handle parseGanadoResponse when data.data.id is missing', async () => {
      const mockResponse = {
        data: {
          data: {
            nombre: 'Test'
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

    it('should handle parseGanadoResponse with estado_salud as fallback', async () => {
      const mockResponse = {
        data: {
          data: {
            id: '1',
            nombre: 'Test',
            estado_salud: 'bueno'
          }
        }
      }
      api.get.mockResolvedValue(mockResponse)

      const result = await fetchQrResource({
        endpoint: '/api/ganado',
        resourceId: '1'
      })

      expect(result.estado).toBe('bueno')
      expect(result.estado_salud).toBe('bueno')
    })

    it('should handle parseOwner with contacto field', async () => {
      const mockResponse = {
        data: {
          data: {
            id: '1',
            nombre: 'Test',
            propietario: {
              nombre: 'Juan',
              contacto: '1234567890',
              rol: 'owner'
            }
          }
        }
      }
      api.get.mockResolvedValue(mockResponse)

      const result = await fetchQrResource({
        endpoint: '/api/ganado',
        resourceId: '1'
      })

      expect(result.propietario.telefono).toBe('1234567890')
    })

    it('should handle parseOwner with both telefono and contacto', async () => {
      const mockResponse = {
        data: {
          data: {
            id: '1',
            nombre: 'Test',
            propietario: {
              nombre: 'Juan',
              telefono: '0987654321',
              contacto: '1234567890',
              rol: 'owner'
            }
          }
        }
      }
      api.get.mockResolvedValue(mockResponse)

      const result = await fetchQrResource({
        endpoint: '/api/ganado',
        resourceId: '1'
      })

      // parseOwner usa data.telefono ?? data.contacto, así que telefono tiene prioridad si existe
      expect(result.propietario.telefono).toBe('0987654321')
    })

    it('should handle parseVacunas with nombre_vacuna fallback', async () => {
      const mockResponse = {
        data: {
          data: {
            id: '1',
            nombre: 'Test',
            vacunas: [
              {
                id: '1',
                nombre_vacuna: 'Vacuna A',
                fecha_aplicacion: '2024-01-01'
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

      expect(result.vacunas).toHaveLength(1)
      expect(result.vacunas[0].nombre).toBe('Vacuna A')
    })

    it('should handle parseVacunas with invalid items', async () => {
      const mockResponse = {
        data: {
          data: {
            id: '1',
            nombre: 'Test',
            vacunas: [
              null,
              undefined,
              'invalid',
              123,
              { id: '1', nombre: 'Valid' }
            ]
          }
        }
      }
      api.get.mockResolvedValue(mockResponse)

      const result = await fetchQrResource({
        endpoint: '/api/ganado',
        resourceId: '1'
      })

      expect(result.vacunas).toHaveLength(1)
      expect(result.vacunas[0].nombre).toBe('Valid')
    })

    it('should handle parseHistorial with diagnostico fallback', async () => {
      const mockResponse = {
        data: {
          data: {
            id: '1',
            nombre: 'Test',
            historial: [
              {
                id: '1',
                fecha: '2024-01-15',
                diagnostico: 'Saludable'
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

      expect(result.historial).toHaveLength(1)
      expect(result.historial[0].resultado).toBe('Saludable')
    })

    it('should handle parseHistorial with invalid items', async () => {
      const mockResponse = {
        data: {
          data: {
            id: '1',
            nombre: 'Test',
            historial: [
              null,
              undefined,
              'invalid',
              123,
              { id: '1', fecha: '2024-01-15', resultado: 'Valid' }
            ]
          }
        }
      }
      api.get.mockResolvedValue(mockResponse)

      const result = await fetchQrResource({
        endpoint: '/api/ganado',
        resourceId: '1'
      })

      expect(result.historial).toHaveLength(1)
      expect(result.historial[0].resultado).toBe('Valid')
    })

    it('should handle parsePotrero with all fields', async () => {
      const mockResponse = {
        data: {
          data: {
            id: '1',
            nombre: 'Test',
            potrero: {
              nombre: 'Potrero 1',
              tipo_pasto: 'Bermuda',
              ultima_limpieza: '2024-01-15',
              fecha_ultimo_uso: '2024-01-10',
              proxima_limpieza: '2024-12-31',
              capacidad: 25,
              estado: 'disponible'
            }
          }
        }
      }
      api.get.mockResolvedValue(mockResponse)

      const result = await fetchQrResource({
        endpoint: '/api/ganado',
        resourceId: '1'
      })

      expect(result.potrero.nombre).toBe('Potrero 1')
      expect(result.potrero.tipo_pasto).toBe('Bermuda')
      expect(result.potrero.capacidad).toBe(25)
      expect(result.potrero.estado).toBe('disponible')
    })

    it('should handle parsePotrero with invalid potrero data', async () => {
      const mockResponse = {
        data: {
          data: {
            id: '1',
            nombre: 'Test',
            potrero: 'invalid'
          }
        }
      }
      api.get.mockResolvedValue(mockResponse)

      const result = await fetchQrResource({
        endpoint: '/api/ganado',
        resourceId: '1'
      })

      expect(result.potrero.nombre).toBeNull()
      expect(result.potrero.tipo_pasto).toBeNull()
    })

    it('should handle parseOwner with invalid owner data', async () => {
      const mockResponse = {
        data: {
          data: {
            id: '1',
            nombre: 'Test',
            propietario: 'invalid'
          }
        }
      }
      api.get.mockResolvedValue(mockResponse)

      const result = await fetchQrResource({
        endpoint: '/api/ganado',
        resourceId: '1'
      })

      expect(result.propietario.nombre).toBeNull()
      expect(result.propietario.telefono).toBeNull()
    })

    it('should handle edad as string number', async () => {
      const mockResponse = {
        data: {
          data: {
            id: '1',
            nombre: 'Test',
            edad: '5'
          }
        }
      }
      api.get.mockResolvedValue(mockResponse)

      const result = await fetchQrResource({
        endpoint: '/api/ganado',
        resourceId: '1'
      })

      expect(result.edad).toBe(5)
    })

    it('should handle edad as invalid string', async () => {
      const mockResponse = {
        data: {
          data: {
            id: '1',
            nombre: 'Test',
            edad: 'invalid'
          }
        }
      }
      api.get.mockResolvedValue(mockResponse)

      const result = await fetchQrResource({
        endpoint: '/api/ganado',
        resourceId: '1'
      })

      expect(result.edad).toBeNull()
    })

    it('should handle edad as null', async () => {
      const mockResponse = {
        data: {
          data: {
            id: '1',
            nombre: 'Test',
            edad: null
          }
        }
      }
      api.get.mockResolvedValue(mockResponse)

      const result = await fetchQrResource({
        endpoint: '/api/ganado',
        resourceId: '1'
      })

      expect(result.edad).toBeNull()
    })

    it('should handle codigo_qr as number', async () => {
      const mockResponse = {
        data: {
          data: {
            id: '1',
            nombre: 'Test',
            codigo_qr: 12345
          }
        }
      }
      api.get.mockResolvedValue(mockResponse)

      const result = await fetchQrResource({
        endpoint: '/api/ganado',
        resourceId: '1'
      })

      expect(result.codigo_qr).toBe('12345')
    })

    it('should handle codigo_qr as empty string', async () => {
      const mockResponse = {
        data: {
          data: {
            id: '1',
            nombre: 'Test',
            codigo_qr: '   '
          }
        }
      }
      api.get.mockResolvedValue(mockResponse)

      const result = await fetchQrResource({
        endpoint: '/api/ganado',
        resourceId: '1'
      })

      expect(result.codigo_qr).toBeNull()
    })

    it('should handle raza as boolean', async () => {
      const mockResponse = {
        data: {
          data: {
            id: '1',
            nombre: 'Test',
            raza: true
          }
        }
      }
      api.get.mockResolvedValue(mockResponse)

      const result = await fetchQrResource({
        endpoint: '/api/ganado',
        resourceId: '1'
      })

      expect(result.raza).toBe('true')
    })

    it('should handle sexo as null', async () => {
      const mockResponse = {
        data: {
          data: {
            id: '1',
            nombre: 'Test',
            sexo: null
          }
        }
      }
      api.get.mockResolvedValue(mockResponse)

      const result = await fetchQrResource({
        endpoint: '/api/ganado',
        resourceId: '1'
      })

      expect(result.sexo).toBeNull()
    })

    it('should handle fecha_nacimiento as empty string', async () => {
      const mockResponse = {
        data: {
          data: {
            id: '1',
            nombre: 'Test',
            fecha_nacimiento: '   '
          }
        }
      }
      api.get.mockResolvedValue(mockResponse)

      const result = await fetchQrResource({
        endpoint: '/api/ganado',
        resourceId: '1'
      })

      expect(result.fecha_nacimiento).toBeNull()
    })

    it('should handle potrero capacidad as string number', async () => {
      const mockResponse = {
        data: {
          data: {
            id: '1',
            nombre: 'Test',
            potrero: {
              capacidad: '25'
            }
          }
        }
      }
      api.get.mockResolvedValue(mockResponse)

      const result = await fetchQrResource({
        endpoint: '/api/ganado',
        resourceId: '1'
      })

      expect(result.potrero.capacidad).toBe(25)
    })

    it('should handle potrero ultima_limpieza as number', async () => {
      const mockResponse = {
        data: {
          data: {
            id: '1',
            nombre: 'Test',
            potrero: {
              ultima_limpieza: 1705276800000
            }
          }
        }
      }
      api.get.mockResolvedValue(mockResponse)

      const result = await fetchQrResource({
        endpoint: '/api/ganado',
        resourceId: '1'
      })

      expect(result.potrero.ultima_limpieza).toBeTruthy()
    })

    it('should handle potrero fecha_ultimo_uso as Date object', async () => {
      const dateObj = new Date('2024-01-15')
      const mockResponse = {
        data: {
          data: {
            id: '1',
            nombre: 'Test',
            potrero: {
              fecha_ultimo_uso: dateObj.toISOString()
            }
          }
        }
      }
      api.get.mockResolvedValue(mockResponse)

      const result = await fetchQrResource({
        endpoint: '/api/ganado',
        resourceId: '1'
      })

      expect(result.potrero.fecha_ultimo_uso).toBeTruthy()
    })

    it('should handle vacunas fecha_aplicacion as number', async () => {
      const mockResponse = {
        data: {
          data: {
            id: '1',
            nombre: 'Test',
            vacunas: [
              {
                id: '1',
                nombre: 'Vacuna A',
                fecha_aplicacion: 1705276800000
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

      expect(result.vacunas[0].fecha_aplicacion).toBeTruthy()
    })

    it('should handle historial fecha as empty string', async () => {
      const mockResponse = {
        data: {
          data: {
            id: '1',
            nombre: 'Test',
            historial: [
              {
                id: '1',
                fecha: '   ',
                resultado: 'Test'
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

      expect(result.historial[0].fecha).toBeNull()
    })

    it('should handle historial resultado and diagnostico both null', async () => {
      const mockResponse = {
        data: {
          data: {
            id: '1',
            nombre: 'Test',
            historial: [
              {
                id: '1',
                fecha: '2024-01-15',
                resultado: null,
                diagnostico: null
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

      expect(result.historial[0].resultado).toBeNull()
    })

    it('should handle vacunas nombre and nombre_vacuna both null', async () => {
      const mockResponse = {
        data: {
          data: {
            id: '1',
            nombre: 'Test',
            vacunas: [
              {
                id: '1',
                nombre: null,
                nombre_vacuna: null
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

      expect(result.vacunas[0].nombre).toBeNull()
    })

    it('should handle sanitizeEndpoint with whitespace only', async () => {
      await expect(
        fetchQrResource({
          endpoint: '   ',
          resourceId: '1'
        })
      ).rejects.toThrow('endpoint')
    })

    it('should handle buildUrl with endpoint containing special characters', async () => {
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
        endpoint: '/api/ganado/with-special-chars',
        resourceId: 'test@123'
      })

      expect(api.get).toHaveBeenCalledWith(
        '/api/ganado/with-special-chars/test%40123',
        expect.any(Object)
      )
    })

    it('should handle buildUrl with endpoint ending with multiple slashes', async () => {
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
        endpoint: '/api/ganado///',
        resourceId: '1'
      })

      // buildUrl solo remueve el último slash, así que quedan // antes del id
      expect(api.get).toHaveBeenCalledWith(
        '/api/ganado///1',
        expect.any(Object)
      )
    })

    it('should handle axios error without response or request', async () => {
      const { isAxiosError } = await import('axios')
      const mockError = {
        message: 'Custom axios error'
      }
      vi.mocked(isAxiosError).mockReturnValue(true)
      api.get.mockRejectedValue(mockError)

      await expect(
        fetchQrResource({
          endpoint: '/api/ganado',
          resourceId: '1'
        })
      ).rejects.toThrow('Custom axios error')
    })

    it('should handle axios error with status 400', async () => {
      const { isAxiosError } = await import('axios')
      const mockError = {
        response: { status: 400 }
      }
      vi.mocked(isAxiosError).mockReturnValue(true)
      api.get.mockRejectedValue(mockError)

      // mapAxiosError no tiene caso específico para 400, va al else que retorna error desconocido
      await expect(
        fetchQrResource({
          endpoint: '/api/ganado',
          resourceId: '1'
        })
      ).rejects.toThrow('desconocido')
    })

    it('should handle axios error with status 401', async () => {
      const { isAxiosError } = await import('axios')
      const mockError = {
        response: { status: 401 }
      }
      vi.mocked(isAxiosError).mockReturnValue(true)
      api.get.mockRejectedValue(mockError)

      // mapAxiosError no tiene caso específico para 401, va al else que retorna error desconocido
      await expect(
        fetchQrResource({
          endpoint: '/api/ganado',
          resourceId: '1'
        })
      ).rejects.toThrow('desconocido')
    })

    it('should handle axios error with status 502', async () => {
      const { isAxiosError } = await import('axios')
      const mockError = {
        response: { status: 502 }
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

    it('should handle axios error with status 503', async () => {
      const { isAxiosError } = await import('axios')
      const mockError = {
        response: { status: 503 }
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

    it('should handle axios error with empty message', async () => {
      const { isAxiosError } = await import('axios')
      const mockError = {
        message: ''
      }
      vi.mocked(isAxiosError).mockReturnValue(true)
      api.get.mockRejectedValue(mockError)

      await expect(
        fetchQrResource({
          endpoint: '/api/ganado',
          resourceId: '1'
        })
      ).rejects.toThrow()
    })

    it('should handle axios error without message property', async () => {
      const { isAxiosError } = await import('axios')
      const mockError = {}
      vi.mocked(isAxiosError).mockReturnValue(true)
      api.get.mockRejectedValue(mockError)

      await expect(
        fetchQrResource({
          endpoint: '/api/ganado',
          resourceId: '1'
        })
      ).rejects.toThrow('desconocido')
    })

    it('should handle fetchQrResource with signal abort', async () => {
      const axiosDefault = await import('axios')
      const { isAxiosError } = await import('axios')
      const abortController = new AbortController()
      abortController.abort()
      
      const mockError = {
        message: 'Aborted'
      }
      vi.mocked(isAxiosError).mockReturnValue(false)
      vi.mocked(axiosDefault.default.isCancel).mockReturnValue(true)
      api.get.mockRejectedValue(mockError)

      await expect(
        fetchQrResource({
          endpoint: '/api/ganado',
          resourceId: '1',
          signal: abortController.signal
        })
      ).rejects.toThrow('cancelada')
    })

    it('should handle fetchQrResource queue deduplication with trimmed values', async () => {
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
        resourceId: '  1  ',
        alternatives: ['1', '  1  ', '2', '  2  ']
      })

      // Should deduplicate '1' and '2' even with different whitespace
      expect(api.get).toHaveBeenCalledTimes(1)
    })

    it('should handle fetchQrResource with resourceId as number zero', async () => {
      // En fetchQrResource, el resourceId 0 se convierte a string "0" en el map
      // Luego pasa el filtro (length > 0) porque "0".length === 1
      // Pero buildUrl valida !resourceId, y "0" es truthy, así que pasa
      // Sin embargo, si la respuesta es exitosa, debería funcionar
      const mockResponse = {
        data: {
          status: 'success',
          data: {
            id: '1',
            nombre: 'Test'
          }
        }
      }
      api.get.mockResolvedValue(mockResponse)

      const result = await fetchQrResource({
        endpoint: '/api/ganado',
        resourceId: 0
      })

      expect(result.id).toBe('1')
    })

    it('should handle fetchQrResource with resourceId as string zero', async () => {
      const mockResponse = {
        data: {
          status: 'success',
          data: {
            id: '1',
            nombre: 'Test'
          }
        }
      }
      api.get.mockResolvedValue(mockResponse)

      // "0" es truthy, así que pasa la validación y se procesa
      const result = await fetchQrResource({
        endpoint: '/api/ganado',
        resourceId: '0'
      })

      expect(result.id).toBe('1')
    })

    it('should handle fetchQrResource when all candidates are filtered out', async () => {
      await expect(
        fetchQrResource({
          endpoint: '/api/ganado',
          resourceId: '   ',
          alternatives: ['', '   ', null, undefined]
        })
      ).rejects.toThrow('identificador')
    })

    it('should handle edge case where buildUrl receives falsy resourceId (line 71)', async () => {
      // Line 71: buildUrl throws when resourceId is falsy (empty string, null, undefined, 0, false)
      // This is defensive code. While the queue filter should prevent empty strings,
      // we test the edge case where a falsy value might somehow reach buildUrl.
      // Note: This is difficult to trigger through fetchQrResource because of the queue filter,
      // but the check exists for safety.
      
      // Since buildUrl is not exported, we can't test it directly.
      // However, we can verify that the queue filter prevents empty strings from reaching it.
      await expect(
        fetchQrResource({
          endpoint: '/api/ganado',
          resourceId: '',
          alternatives: []
        })
      ).rejects.toThrow('identificador')
    })

    it('should handle edge case where all candidates fail without 404 and lastNotFoundError is null (line 317)', async () => {
      // Line 317: This throws QrUnknownError when queue is exhausted without 404 errors
      // and lastNotFoundError is null. This is defensive code that should be unreachable
      // because non-404 errors throw immediately. However, to cover this line, we would need
      // a scenario where the loop completes without throwing and without success, which
      // shouldn't happen in practice.
      //
      // The current code flow:
      // - If error is 404: set lastNotFoundError and continue
      // - If error is not 404: throw immediately
      // - If success: return immediately
      // So line 317 is only reached if the loop completes without any of these happening,
      // which is theoretically impossible with the current logic.
      //
      // This line serves as a safety check for edge cases or future code changes.
      
      // We can't easily trigger this without modifying the source code, but we document
      // that it's defensive code that protects against unexpected scenarios.
    })
  })

  describe('transformEmbeddedPayload edge cases', () => {
    it('should handle toNullableString with unknown types (line 132)', () => {
      // This test covers line 132 in toNullableString for unknown types
      // We can test this through transformEmbeddedPayload by passing values
      // that are not string, number, boolean, object, null, or undefined
      
      // Test with Symbol
      const payloadWithSymbol = {
        id: '1',
        nombre: Symbol('test')
      }
      const result1 = transformEmbeddedPayload(payloadWithSymbol)
      expect(result1.nombre).toBeNull()
      
      // Test with BigInt
      const payloadWithBigInt = {
        id: '1',
        nombre: BigInt(123)
      }
      const result2 = transformEmbeddedPayload(payloadWithBigInt)
      expect(result2.nombre).toBeNull()
      
      // Test with function
      const payloadWithFunction = {
        id: '1',
        nombre: () => 'test'
      }
      const result3 = transformEmbeddedPayload(payloadWithFunction)
      expect(result3.nombre).toBeNull()
    })

    it('should handle toIsoString with non-string/number/Date types (line 148)', () => {
      // This test covers line 148 in toIsoString for types that are not
      // string, number, Date, null, or undefined
      
      // Test with boolean
      const payloadWithBoolean = {
        id: '1',
        fecha_nacimiento: true
      }
      const result1 = transformEmbeddedPayload(payloadWithBoolean)
      expect(result1.fecha_nacimiento).toBeNull()
      
      // Test with object
      const payloadWithObject = {
        id: '1',
        fecha_nacimiento: { year: 2020, month: 1, day: 15 }
      }
      const result2 = transformEmbeddedPayload(payloadWithObject)
      expect(result2.fecha_nacimiento).toBeNull()
      
      // Test with array
      const payloadWithArray = {
        id: '1',
        fecha_nacimiento: [2020, 1, 15]
      }
      const result3 = transformEmbeddedPayload(payloadWithArray)
      expect(result3.fecha_nacimiento).toBeNull()
      
      // Test with Symbol
      const payloadWithSymbol = {
        id: '1',
        fecha_nacimiento: Symbol('test')
      }
      const result4 = transformEmbeddedPayload(payloadWithSymbol)
      expect(result4.fecha_nacimiento).toBeNull()
    })
  })
})
