// useGanado.js - Composables para gestión de ganado
import { ref } from 'vue'
import { ganadoAPI } from '../services/api.js'
import { socket } from '../socket.js'

let socketRegistered = false

export function useGanado() {
  const ganado = ref([])
  const loading = ref(false)
  const error = ref(null)

  const cargarGanado = async () => {
    try {
      loading.value = true
      error.value = null
      const response = await ganadoAPI.getAll()
      
      // Manejar diferentes formatos de respuesta
      let ganadoData = []
      if (response.data?.status === 'success' && Array.isArray(response.data?.data)) {
        ganadoData = response.data.data
      } else if (Array.isArray(response.data?.data)) {
        ganadoData = response.data.data
      }
      
      ganado.value = ganadoData
    } catch (err) {
      const errorMessage = err.response?.data?.message || err.message || 'Error al cargar el ganado'
      error.value = errorMessage
      console.error('[useGanado] Error cargando ganado:', {
        message: errorMessage,
        error: err,
        status: err.response?.status,
        data: err.response?.data
      })
      ganado.value = []
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

  const upsertGanado = (nuevo) => {
    if (!nuevo?.id) return
    const index = ganado.value.findIndex(item => item.id === nuevo.id)
    if (index >= 0) {
      ganado.value.splice(index, 1, { ...ganado.value[index], ...nuevo })
    } else {
      ganado.value = [nuevo, ...ganado.value]
    }
  }

  const removeGanado = (id) => {
    if (!id) return
    ganado.value = ganado.value.filter(item => item.id !== id)
  }

  const registerSocketEvents = () => {
    if (socketRegistered) return
    socketRegistered = true

    socket.on('animal_created', (payload) => {
      if (payload?.data) {
        upsertGanado(payload.data)
      }
    })

    socket.on('animal_updated', (payload) => {
      if (payload?.data) {
        upsertGanado(payload.data)
      }
    })

    socket.on('animal_deleted', (payload) => {
      const id = payload?.id
      if (id) {
        removeGanado(id)
      }
    })

    socket.on('disconnect', () => {
      socketRegistered = false
    })
  }

  registerSocketEvents()

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