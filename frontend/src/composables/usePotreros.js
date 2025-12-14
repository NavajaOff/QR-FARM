// usePotreros.js - Composables para gestión de potreros
import { ref } from 'vue'
import { potreroAPI } from '../services/api.js'
import { socket } from '../socket.js'

let socketRegistered = false

export function usePotreros() {
  const potreros = ref([])
  const loading = ref(false)
  const error = ref(null)

  const cargarPotreros = async () => {
    try {
      loading.value = true
      error.value = null
      const response = await potreroAPI.getAll()
      const payload = response.data
      if (payload?.success || payload?.status === 'success') {
          potreros.value = payload.data || []
          console.log('DEBUG Frontend cargarPotreros: potreros loaded', potreros.value.length, 'first:', potreros.value[0] ? {id: potreros.value[0].id, estado: potreros.value[0].estado, estado_nombre: potreros.value[0].estado_nombre} : 'none')
          if (potreros.value[0]) {
              console.log('DEBUG Frontend: Campos del primer potrero:', Object.keys(potreros.value[0]))
              console.log('DEBUG Frontend: Valores de actividades:', {
                  ultima_limpieza: potreros.value[0].ultima_limpieza,
                  proxima_limpieza: potreros.value[0].proxima_limpieza,
                  ultimaLimpieza: potreros.value[0].ultimaLimpieza,
                  proximaLimpieza: potreros.value[0].proximaLimpieza
              })
          }
      } else {
          error.value = payload?.message || 'No fue posible obtener los potreros'
      }
    } catch (err) {
      error.value = err.message || 'Error desconocido al cargar potreros'
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
      return { success: false, message: err.message || 'Error desconocido al crear potrero' }
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
      return { success: false, message: err.message || 'Error desconocido al actualizar potrero' }
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
      return { success: false, message: err.message || 'Error desconocido al eliminar potrero' }
    }
  }

  const upsertPotrero = (nuevo) => {
    if (!nuevo?.id) return
    const index = potreros.value.findIndex(item => item.id === nuevo.id)
    if (index >= 0) {
      potreros.value.splice(index, 1, { ...potreros.value[index], ...nuevo })
    } else {
      potreros.value = [nuevo, ...potreros.value]
    }
  }

  const removePotrero = (id) => {
    if (!id) return
    potreros.value = potreros.value.filter(item => item.id !== id)
  }

  const registerSocketEvents = () => {
    if (socketRegistered) return
    socketRegistered = true

    socket.on('potrero_created', (payload) => {
      if (payload?.data) {
        upsertPotrero(payload.data)
      }
    })

    socket.on('potrero_updated', (payload) => {
      if (payload?.data) {
        upsertPotrero(payload.data)
      }
    })

    socket.on('potrero_deleted', (payload) => {
      const id = payload?.id
      if (id) {
        removePotrero(id)
      }
    })

    socket.on('disconnect', () => {
      socketRegistered = false
    })
  }

  registerSocketEvents()

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