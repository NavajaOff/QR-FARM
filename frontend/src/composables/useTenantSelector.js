// useTenantSelector.js - Composable para manejo de selección de tenant
import { ref, computed, watch } from 'vue'
import { useTenants } from './useTenants.js'
import authService from '../services/authService.js'

const STORAGE_KEY = 'qr_farm_selected_tenant_id'
const STORAGE_KEY_NAME = 'qr_farm_selected_tenant_name'

export function useTenantSelector() {
  const selectedTenantId = ref(null)
  const selectedTenantName = ref(null)
  const { tenants, loading, error, cargarTenants } = useTenants()

  // Cargar tenant seleccionado desde localStorage al inicializar
  const loadSelectedTenant = () => {
    try {
      const storedId = localStorage.getItem(STORAGE_KEY)
      const storedName = localStorage.getItem(STORAGE_KEY_NAME)
      
      if (storedId) {
        const tenantId = Number.parseInt(storedId, 10)
        if (!Number.isNaN(tenantId)) {
          selectedTenantId.value = tenantId
          selectedTenantName.value = storedName || null
        }
      }
    } catch (err) {
      console.error('[useTenantSelector] Error cargando tenant seleccionado:', err)
    }
  }

  // Verificar si el usuario es super admin
  const isSuperAdmin = computed(() => {
    return authService.getRole() === 'super_admin'
  })

  // Verificar si debe mostrar el selector (solo para super admin)
  const shouldShowSelector = computed(() => {
    return isSuperAdmin.value
  })

  // Obtener el tenant actual seleccionado
  const currentTenant = computed(() => {
    if (!selectedTenantId.value) return null
    return tenants.value.find(t => t.id === selectedTenantId.value) || null
  })

  // Seleccionar un tenant
  const selectTenant = (tenantId, tenantName = null) => {
    try {
      if (!tenantId) {
        // Limpiar selección (ver todos los tenants)
        selectedTenantId.value = null
        selectedTenantName.value = null
        localStorage.removeItem(STORAGE_KEY)
        localStorage.removeItem(STORAGE_KEY_NAME)
        console.log('[useTenantSelector] Selección de tenant limpiada')
        return
      }

      const id = Number.parseInt(tenantId, 10)
      if (Number.isNaN(id)) {
        console.error('[useTenantSelector] ID de tenant inválido:', tenantId)
        return
      }

      selectedTenantId.value = id
      selectedTenantName.value = tenantName || null
      localStorage.setItem(STORAGE_KEY, id.toString())
      if (tenantName) {
        localStorage.setItem(STORAGE_KEY_NAME, tenantName)
      }
      console.log('[useTenantSelector] Tenant seleccionado:', id, tenantName)
    } catch (err) {
      console.error('[useTenantSelector] Error seleccionando tenant:', err)
    }
  }

  // Limpiar selección de tenant
  const clearTenant = () => {
    selectTenant(null)
  }

  // Cargar lista de tenants activos
  const loadTenants = async () => {
    if (!isSuperAdmin.value) return
    await cargarTenants(true) // Solo activos
  }

  // Inicializar al montar
  loadSelectedTenant()

  return {
    selectedTenantId,
    selectedTenantName,
    tenants,
    loading,
    error,
    isSuperAdmin,
    shouldShowSelector,
    currentTenant,
    selectTenant,
    clearTenant,
    loadTenants
  }
}

