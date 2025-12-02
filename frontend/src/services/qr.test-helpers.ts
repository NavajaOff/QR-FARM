import { vi } from 'vitest'
import apiInternal from './api.js'
import type { GanadoResource, EmbeddedQrPayload } from './qr'

// Setup mocks
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

/**
 * Create a mock successful Ganado response
 */
export const createMockGanadoResponse = (
  overrides?: Partial<GanadoResource>
): { data: { data: Partial<GanadoResource> } } => ({
  data: {
    data: {
      id: '1',
      nombre: 'Vaca Test',
      raza: 'Holstein',
      estado: 'saludable',
      estado_salud: 'bueno',
      codigo_qr: 'QR123',
      ...overrides
    }
  }
})

/**
 * Create a mock Ganado response with nested structure
 */
export const createMockNestedGanadoResponse = (overrides?: {
  id?: string
  nombre?: string
  propietario?: Partial<GanadoResource['propietario']>
  potrero?: Partial<GanadoResource['potrero']>
  vacunas?: GanadoResource['vacunas']
  historial?: GanadoResource['historial']
}) => ({
  data: {
    status: 'success',
    data: {
      id: overrides?.id || '1',
      nombre: overrides?.nombre || 'Vaca Test',
      raza: 'Holstein',
      estado: 'saludable',
      estado_salud: 'bueno',
      codigo_qr: 'QR123',
      propietario: {
        nombre: 'Juan Pérez',
        telefono: '1234567890',
        rol: 'propietario',
        ...overrides?.propietario
      },
      potrero: {
        nombre: 'Potrero 1',
        tipo_pasto: 'Bermuda',
        capacidad: 25,
        estado: 'disponible',
        ...overrides?.potrero
      },
      vacunas: overrides?.vacunas || [],
      historial: overrides?.historial || []
    }
  }
})

/**
 * Create a mock axios error
 */
export const createMockAxiosError = (config: {
  status?: number
  request?: boolean
  message?: string
  isCancel?: boolean
} = {}) => {
  const error: any = {}
  
  if (config.status !== undefined) {
    error.response = { status: config.status }
  }
  
  if (config.request !== undefined) {
    error.request = config.request ? {} : undefined
  }
  
  if (config.message) {
    error.message = config.message
  }
  
  if (config.isCancel) {
    error.isCancel = true
  }
  
  return error
}

/**
 * Create a mock embedded payload
 */
export const createEmbeddedPayload = (
  overrides?: Partial<EmbeddedQrPayload>
): EmbeddedQrPayload => ({
  id: '1',
  nombre: 'Vaca Test',
  estado: 'saludable',
  codigo: 'QR123',
  ...overrides
})

/**
 * Setup axios mocks for a test
 */
export const setupAxiosMocks = async () => {
  const { isAxiosError } = await import('axios')
  const axiosDefault = await import('axios')
  
  return {
    isAxiosError: vi.mocked(isAxiosError),
    isCancel: vi.mocked(axiosDefault.default.isCancel)
  }
}

/**
 * Reset all mocks
 */
export const resetMocks = () => {
  vi.clearAllMocks()
  apiInternal.get.mockReset()
}

export { default as api } from './api.js'

