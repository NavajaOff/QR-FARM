import { beforeEach, vi } from 'vitest'
import { useReportes } from './useReportes'
import { reportAPI } from '../services/api.js'

vi.mock('../services/api.js', () => ({
  reportAPI: {
    getSummary: vi.fn(),
    downloadSummaryPdf: vi.fn()
  }
}))

describe('useReportes', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    sessionStorage.clear()
    globalThis.location = { href: '' }
    globalThis.URL = {
      createObjectURL: vi.fn(() => 'blob:url'),
      revokeObjectURL: vi.fn()
    }
    document.body.innerHTML = ''
  })

  it('should export useReportes composable', () => {
    expect(useReportes).toBeDefined()
    expect(typeof useReportes).toBe('function')
  })

  it('should initialize with default values', () => {
    const { resumen, loading, error } = useReportes()
    expect(resumen.value).toBeNull()
    expect(loading.value).toBe(false)
    expect(error.value).toBeNull()
  })

  it('should load summary successfully', async () => {
    const mockResumen = { usuarios: { total: 5 } }
    reportAPI.getSummary.mockResolvedValue({
      data: {
        status: 'success',
        data: mockResumen
      }
    })

    const { cargarResumen, resumen, loading } = useReportes()
    await cargarResumen()

    expect(resumen.value).toEqual(mockResumen)
    expect(loading.value).toBe(false)
  })

  it('should handle error when loading summary', async () => {
    const errorMessage = 'Error al cargar resumen'
    reportAPI.getSummary.mockRejectedValue(new Error(errorMessage))

    const { cargarResumen, error, loading } = useReportes()
    await cargarResumen()

    expect(error.value).toBe(errorMessage)
    expect(loading.value).toBe(false)
  })

  it('should download PDF successfully', async () => {
    const mockBlob = new Blob(['pdf content'], { type: 'application/pdf' })
    reportAPI.downloadSummaryPdf.mockResolvedValue({
      data: mockBlob
    })

    const { descargarPdf } = useReportes()
    const result = await descargarPdf()

    expect(result.success).toBe(true)
    expect(globalThis.URL.createObjectURL).toHaveBeenCalled()
    expect(globalThis.URL.revokeObjectURL).toHaveBeenCalled()
  })

  it('should handle error when downloading PDF', async () => {
    const errorMessage = 'Error al descargar'
    reportAPI.downloadSummaryPdf.mockRejectedValue(new Error(errorMessage))

    const { descargarPdf } = useReportes()
    const result = await descargarPdf()

    expect(result.success).toBe(false)
    expect(result.message).toBe(errorMessage)
  })

  it('should handle 401 error and redirect to login if no email', async () => {
    reportAPI.getSummary.mockRejectedValue({
      response: { status: 401 }
    })

    const { cargarResumen } = useReportes()
    await cargarResumen()

    expect(globalThis.location.href).toBe('/login')
  })

  it('should handle 401 error with stored email', async () => {
    sessionStorage.setItem('lastLoginEmail', 'test@example.com')
    reportAPI.getSummary
      .mockRejectedValueOnce({
        response: { status: 401 }
      })
      .mockResolvedValueOnce({
        data: {
          status: 'success',
          data: { usuarios: { total: 5 } }
        }
      })

    const { cargarResumen, resumen } = useReportes()
    await cargarResumen()

    expect(resumen.value).toBeDefined()
  })
})