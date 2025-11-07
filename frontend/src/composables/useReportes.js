import { ref } from 'vue'
import { reportAPI, authAPI } from '../services/api.js'

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
      error.value = err.message || 'Error al consultar reportes'
      console.error('[useReportes] Error cargando resumen:', err)
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

      if (status === 401) {
        await renovarToken()
        const response = await reportAPI.getSummary()
        if (response.data?.status === 'success') {
          resumen.value = response.data.data
          return
        }
        throw new Error(response.data?.message || 'No autorizado')
      }

      throw err
    }
  }

  const renovarToken = async () => {
    try {
      const email = sessionStorage.getItem('lastLoginEmail')
      const password = sessionStorage.getItem('lastLoginPassword')

      if (!email || !password) {
        throw new Error('No hay credenciales almacenadas para renovar el token')
      }

      const response = await authAPI.login({ email, password })
      if (response.data?.status === 'success') {
        localStorage.setItem('token', response.data.token)
        localStorage.setItem('user', JSON.stringify(response.data.user))
        localStorage.setItem('userRole', response.data.user?.rol?.rol || 'usuario')
        return
      }

      throw new Error(response.data?.message || 'No fue posible renovar el token')
    } catch (error) {
      console.warn('[useReportes] No se pudo renovar el token automáticamente:', error.message)
      throw error
    }
  }

  const descargarPdf = async () => {
    try {
      const response = await reportAPI.downloadSummaryPdf()
      const blob = new Blob([response.data], { type: 'application/pdf' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = 'reporte_qrfarm.pdf'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
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

