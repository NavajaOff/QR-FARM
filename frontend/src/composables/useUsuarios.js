// useUsuarios.js - Composables para gestión de usuarios
import { ref } from 'vue'
import { userAPI } from '../services/api.js'
import { capitalizarPalabras } from '../utils/text.js'

const normalizarCampoNombre = (valor) => (valor ? capitalizarPalabras(valor) : valor)

const construirNombreCompletoUsuario = (usuario) => {
  const persona = usuario.persona
  const tienePersona = persona && (
    persona.primer_nombre ||
    persona.segundo_nombre ||
    persona.primer_apellido ||
    persona.segundo_apellido
  )

  const partes = tienePersona
    ? [
        persona.primer_nombre,
        persona.segundo_nombre,
        persona.primer_apellido,
        persona.segundo_apellido
      ]
    : [
        usuario.primer_nombre,
        usuario.segundo_nombre,
        usuario.primer_apellido,
        usuario.segundo_apellido
      ]

  const nombres = partes.filter(Boolean)
  if (nombres.length) {
    return capitalizarPalabras(nombres.join(' '))
  }
  if (usuario.nombre) {
    return capitalizarPalabras(usuario.nombre)
  }
  return ''
}

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
        const usuariosNormalizados = usuariosFiltrados.map((usuario) => {
          const personaOriginal = usuario.persona
          const persona = personaOriginal
            ? {
                ...personaOriginal,
                primer_nombre: normalizarCampoNombre(personaOriginal.primer_nombre),
                segundo_nombre: normalizarCampoNombre(personaOriginal.segundo_nombre),
                primer_apellido: normalizarCampoNombre(personaOriginal.primer_apellido),
                segundo_apellido: normalizarCampoNombre(personaOriginal.segundo_apellido)
              }
            : null

          const usuarioNormalizado = {
            ...usuario,
            persona,
            primer_nombre: normalizarCampoNombre(usuario.primer_nombre),
            segundo_nombre: normalizarCampoNombre(usuario.segundo_nombre),
            primer_apellido: normalizarCampoNombre(usuario.primer_apellido),
            segundo_apellido: normalizarCampoNombre(usuario.segundo_apellido)
          }

          const nombreVisible = construirNombreCompletoUsuario(usuarioNormalizado)
          usuarioNormalizado.nombre = nombreVisible || capitalizarPalabras(usuario.nombre || '')
          return usuarioNormalizado
        })
        usuarios.value = usuariosNormalizados
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