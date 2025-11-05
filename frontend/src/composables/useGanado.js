// useGanado.js - Composables para gestión de ganado
import { ref } from 'vue'
import { ganadoAPI } from '../services/api.js'

export function useGanado() {
  const ganado = ref([])
  const loading = ref(false)
  const error = ref(null)

  const cargarGanado = async () => {
    try {
      loading.value = true
      error.value = null
      const response = await ganadoAPI.getAll()
      if (response.data?.status === 'success') {
        ganado.value = response.data.data
      }
    } catch (err) {
      error.value = err.message
      console.error('Error cargando ganado:', err)
    } finally {
      loading.value = false
    }
  }

  const crearGanado = async (data) => {
    try {
      const response = await ganadoAPI.create(data)
      if (response.data?.status === 'success') {
        await cargarGanado() // Recargar lista
        return { success: true }
      }
      return { success: false, message: response.data?.message }
    } catch (err) {
      return { success: false, message: err.message }
    }
  }

  const actualizarGanado = async (id, data) => {
    try {
      const response = await ganadoAPI.update(id, data)
      if (response.data?.status === 'success') {
        await cargarGanado() // Recargar lista
        return { success: true }
      }
      return { success: false, message: response.data?.message }
    } catch (err) {
      return { success: false, message: err.message }
    }
  }

  const eliminarGanado = async (id) => {
    try {
      const response = await ganadoAPI.delete(id)
      if (response.data?.status === 'success') {
        await cargarGanado() // Recargar lista
        return { success: true }
      }
      return { success: false, message: response.data?.message }
    } catch (err) {
      return { success: false, message: err.message }
    }
  }

  return {
    ganado,
    loading,
    error,
    cargarGanado,
    crearGanado,
    actualizarGanado,
    eliminarGanado
  }
}