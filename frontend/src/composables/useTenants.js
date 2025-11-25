// useTenants.js - Composables para gestión de tenants
import { ref } from 'vue'
import { tenantAPI } from '../services/api.js'

export function useTenants() {
  const tenants = ref([])
  const loading = ref(false)
  const error = ref(null)

  const cargarTenants = async (activosOnly = true) => {
    try {
      loading.value = true
      error.value = null
      const response = await tenantAPI.getAll(activosOnly)
      if (response.data?.status === 'success') {
        tenants.value = response.data.data
      } else {
        error.value = response.data?.message || 'Error al cargar tenants'
      }
    } catch (err) {
      error.value = err.response?.data?.message || err.message || 'Error al cargar tenants'
      console.error('Error cargando tenants:', err)
    } finally {
      loading.value = false
    }
  }

  const crearTenant = async (data) => {
    try {
      loading.value = true
      error.value = null
      const response = await tenantAPI.create(data)
      if (response.data?.status === 'success') {
        await cargarTenants(false) // Recargar lista incluyendo inactivos
        return { success: true, data: response.data.data }
      }
      return { success: false, message: response.data?.message || 'Error al crear tenant' }
    } catch (err) {
      const message = err.response?.data?.message || err.message || 'Error al crear tenant'
      error.value = message
      return { success: false, message }
    } finally {
      loading.value = false
    }
  }

  const actualizarTenant = async (id, data) => {
    try {
      loading.value = true
      error.value = null
      const response = await tenantAPI.update(id, data)
      if (response.data?.status === 'success') {
        await cargarTenants(false) // Recargar lista
        return { success: true, data: response.data.data }
      }
      return { success: false, message: response.data?.message || 'Error al actualizar tenant' }
    } catch (err) {
      const message = err.response?.data?.message || err.message || 'Error al actualizar tenant'
      error.value = message
      return { success: false, message }
    } finally {
      loading.value = false
    }
  }

  const obtenerTenant = async (id) => {
    try {
      loading.value = true
      error.value = null
      const response = await tenantAPI.getById(id)
      if (response.data?.status === 'success') {
        return { success: true, data: response.data.data }
      }
      return { success: false, message: response.data?.message || 'Tenant no encontrado' }
    } catch (err) {
      const message = err.response?.data?.message || err.message || 'Error al obtener tenant'
      error.value = message
      return { success: false, message }
    } finally {
      loading.value = false
    }
  }

  return {
    tenants,
    loading,
    error,
    cargarTenants,
    crearTenant,
    actualizarTenant,
    obtenerTenant
  }
}

