import { beforeEach, vi, describe, it, expect } from 'vitest'
import { fetchQrResource, transformEmbeddedPayload } from './qr'
import api from './api.js'
import axios from 'axios'

vi.mock('./api.js', () => ({
  default: {
    get: vi.fn()
  }
}))

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

    it('should throw error when resourceId is empty', async () => {
      await expect(
        fetchQrResource({
          endpoint: '/api/ganado',
          resourceId: ''
        })
      ).rejects.toThrow('identificador')
    })

    it('should handle 404 error', async () => {
      const mockError = {
        response: { status: 404 },
        isAxiosError: true
      }
      api.get.mockRejectedValue(mockError)

      await expect(
        fetchQrResource({
          endpoint: '/api/ganado',
          resourceId: '999'
        })
      ).rejects.toThrow('registrado')
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
  })
})