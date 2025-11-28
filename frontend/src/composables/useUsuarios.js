// useUsuarios.js - Composables para gestión de usuarios
import { ref } from 'vue'
import { userAPI } from '../services/api.js'

export function useUsuarios() {
  const usuarios = ref([])
  const loading = ref(false)
  const error = ref(null)

  const cargarUsuarios = async () => {
    try {
      loading.value = true
      error.value = null
      const response = await userAPI.getAll()
      if (response.data?.status === 'success') {
        // Filtrar usuarios con rol super_admin para seguridad adicional en frontend
        const usuariosFiltrados = (response.data.data || []).filter(usuario => {
          // Verificar diferentes formas de obtener el rol
          const rol = usuario?.rol?.nombre_rol || usuario?.rol?.rol || usuario?.rol
          return rol !== 'super_admin'
        })
        usuarios.value = usuariosFiltrados
        console.log(`[useUsuarios] Cargados ${usuariosFiltrados.length} usuarios (filtrados de ${response.data.data?.length || 0} total)`)
      }
    } catch (err) {
      error.value = err.message
      console.error('Error cargando usuarios:', err)
    } finally {
      loading.value = false
    }
  }

  const actualizarUsuario = async (id, data) => {
    try {
      const response = await userAPI.update(id, data)
      if (response.data?.status === 'success') {
        await cargarUsuarios() // Recargar lista
        return { success: true }
      }
      return { success: false, message: response.data?.message }
    } catch (err) {
      return { success: false, message: err.message }
    }
  }

  const cambiarEstadoUsuario = async (id, estado) => {
    try {
      const response = await userAPI.changeStatus(id, estado)
      if (response.data?.status === 'success') {
        await cargarUsuarios() // Recargar lista
        return { success: true }
      }
      return { success: false, message: response.data?.message || 'Error desconocido' }
    } catch (err) {
      console.error('Error cambiando estado de usuario:', err)
      const errorMessage = err.response?.data?.message || err.message || 'Error al cambiar el estado del usuario'
      return { success: false, message: errorMessage }
    }
  }

  return {
    usuarios,
    loading,
    error,
    cargarUsuarios,
    actualizarUsuario,
    cambiarEstadoUsuario
  }
}