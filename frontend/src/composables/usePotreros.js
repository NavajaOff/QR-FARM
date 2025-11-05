// usePotreros.js - Composables para gestión de potreros
import { ref } from 'vue'
import { potreroAPI } from '../services/api.js'

export function usePotreros() {
  const potreros = ref([])
  const loading = ref(false)
  const error = ref(null)

  const cargarPotreros = async () => {
    try {
      loading.value = true
      error.value = null
      const response = await potreroAPI.getAll()
      if (response.data?.status === 'success') {
        potreros.value = response.data.data
      }
    } catch (err) {
      error.value = err.message
      console.error('Error cargando potreros:', err)
    } finally {
      loading.value = false
    }
  }

  const crearPotrero = async (data) => {
    try {
      const response = await potreroAPI.create(data)
      if (response.data?.success) {
        await cargarPotreros() // Recargar lista
        return { success: true }
      }
      return { success: false, message: response.data?.message }
    } catch (err) {
      return { success: false, message: err.message }
    }
  }

  const actualizarPotrero = async (id, data) => {
    try {
      const response = await potreroAPI.update(id, data)
      if (response.data?.success) {
        await cargarPotreros() // Recargar lista
        return { success: true }
      }
      return { success: false, message: response.data?.message }
    } catch (err) {
      return { success: false, message: err.message }
    }
  }

  const eliminarPotrero = async (id) => {
    try {
      const response = await potreroAPI.delete(id)
      if (response.data?.success) {
        await cargarPotreros() // Recargar lista
        return { success: true }
      }
      return { success: false, message: response.data?.message }
    } catch (err) {
      return { success: false, message: err.message }
    }
  }

  return {
    potreros,
    loading,
    error,
    cargarPotreros,
    crearPotrero,
    actualizarPotrero,
    eliminarPotrero
  }
}