// useGanado.js - Composables para gestión de ganado
import { ref } from 'vue'
import { ganadoAPI } from '../services/api.js'
import { socket } from '../socket.js'

let socketRegistered = false

// Utility functions for age calculation
const calcularEdad = (fechaNacimiento) => {
  if (!fechaNacimiento) return Number.NaN;
  const nacimiento = new Date(fechaNacimiento);
  const hoy = new Date();
  let edad = hoy.getFullYear() - nacimiento.getFullYear();
  const mes = hoy.getMonth() - nacimiento.getMonth();
  if (mes < 0 || (mes === 0 && hoy.getDate() < nacimiento.getDate())) {
    edad--;
  }
  return edad;
};

const calcularDetalleEdad = (fechaNacimiento) => {
  if (!fechaNacimiento) return null;
  const nacimiento = new Date(fechaNacimiento);
  if (Number.isNaN(nacimiento.getTime())) return null;
  const hoy = new Date();
  let years = hoy.getFullYear() - nacimiento.getFullYear();
  let months = hoy.getMonth() - nacimiento.getMonth();
  if (hoy.getDate() < nacimiento.getDate()) {
    months--;
  }
  if (months < 0) {
    years--;
    months += 12;
  }
  if (years < 0) {
    years = 0;
  }
  return { years, months };
};

const obtenerEdadTexto = (fechaNacimiento) => {
  const detalle = calcularDetalleEdad(fechaNacimiento);
  if (!detalle) return 'Sin información';
  if (detalle.years >= 1) {
    return detalle.years === 1 ? '1 año' : `${detalle.years} años`;
  }
  if (detalle.months >= 1) {
    return detalle.months === 1 ? '1 mes' : `${detalle.months} meses`;
  }
  return 'Menos de un mes';
};

export function useGanado() {
  const ganado = ref([])
  const loading = ref(false)
  const error = ref(null)

  const cargarGanado = async () => {
    try {
      loading.value = true
      error.value = null
      const response = await ganadoAPI.getAll()
      
      // Helper function to extract data from API response
      const extractDataFromResponse = (response) => {
        if (!response?.data) return [];
        const data = response.data;
        if (data.status === 'success' && Array.isArray(data.data)) {
          return data.data;
        }
        if (Array.isArray(data.data)) {
          return data.data;
        }
        return [];
      };
      
      ganado.value = extractDataFromResponse(response).map(animal => ({
        ...animal,
        edadTexto: animal.fecha_nacimiento ? obtenerEdadTexto(animal.fecha_nacimiento) : 'Sin información'
      }))
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
    const mapped = {
      ...nuevo,
      edadTexto: nuevo.fecha_nacimiento ? obtenerEdadTexto(nuevo.fecha_nacimiento) : 'Sin información'
    }
    const index = ganado.value.findIndex(item => item.id === nuevo.id)
    if (index >= 0) {
      ganado.value.splice(index, 1, { ...ganado.value[index], ...mapped })
    } else {
      ganado.value = [mapped, ...ganado.value]
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