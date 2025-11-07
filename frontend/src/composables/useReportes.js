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
      const response = await reportAPI.getSummary()
      if (response.data?.status === 'success') {
        resumen.value = response.data.data
      } else {
        error.value = response.data?.message || 'No fue posible obtener el resumen'
      }
    } catch (err) {
      error.value = err.message || 'Error al consultar reportes'
      console.error('[useReportes] Error cargando resumen:', err)
    } finally {
      loading.value = false
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

