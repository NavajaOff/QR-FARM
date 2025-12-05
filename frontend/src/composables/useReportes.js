import { ref } from 'vue'
import { reportAPI } from '../services/api.js'

export function useReportes() {
  const resumen = ref(null)
  const loading = ref(false)
  const error = ref(null)

  const cargarResumen = async () => {
    try {
      loading.value = true
      error.value = null
      await obtenerResumenConRenovacion()
    } catch (err) {
      const errorMessage = err.message || 'Error al consultar reportes'
      error.value = errorMessage
      console.error('[useReportes] Error cargando resumen:', {
        message: errorMessage,
        error: err,
        status: err?.response?.status,
        data: err?.response?.data
      })
    } finally {
      loading.value = false
    }
  }

  const obtenerResumenConRenovacion = async () => {
    try {
      const response = await reportAPI.getSummary()
      if (response.data?.status === 'success') {
        resumen.value = response.data.data
        return
      }

      throw response
    } catch (err) {
      const status = err?.response?.status ?? err?.status
      const errorData = err?.response?.data

      if (status === 401) {
        await renovarToken()
        const response = await reportAPI.getSummary()
        if (response.data?.status === 'success') {
          resumen.value = response.data.data
          return
        }
        throw new Error(response.data?.message || 'No autorizado')
      }

      if (status === 403) {
        const message = errorData?.message || errorData?.data?.message || 'No tiene permisos para acceder a los reportes'
        throw new Error(message)
      }

      if (status >= 500) {
        throw new Error(errorData?.message || 'Error del servidor al generar el reporte')
      }

      if (errorData?.message) {
        throw new Error(errorData.message)
      }

      throw new Error(err.message || 'Error al consultar reportes')
    }
  }

  const renovarToken = async () => {
    const email = sessionStorage.getItem('lastLoginEmail')

    if (!email) {
      const errorMessage = 'No hay credenciales almacenadas para renovar el token. Redirigiendo a login.'
      console.warn('[useReportes]', errorMessage)
      globalThis.location.href = '/login'
      throw new Error(errorMessage)
    }

    throw new Error('Token expirado. Por favor, inicia sesión nuevamente.')
  }

  const descargarPdf = async () => {
    try {
      const response = await reportAPI.downloadSummaryPdf()
      const blob = new Blob([response.data], { type: 'application/pdf' })
      const url = globalThis.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = 'reporte_qrfarm.pdf'
      document.body.appendChild(link)
      link.click()
      link.remove()
      globalThis.URL.revokeObjectURL(url)
      return { success: true }
    } catch (err) {
      console.error('[useReportes] Error descargando PDF:', err)
      return { success: false, message: err.message || 'No fue posible descargar el PDF' }
    }
  }

  return {
    resumen,
    loading,
    error,
    cargarResumen,
    descargarPdf,
  }
}

