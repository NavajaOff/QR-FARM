// useTenantSelection.js - Composable para gestionar el tenant seleccionado por super admin
import { ref } from 'vue'

const STORAGE_KEY = 'qr_farm_selected_tenant_id'

// Estado global del tenant seleccionado
const selectedTenantId = ref(null)

// Cargar tenant seleccionado desde localStorage al inicializar
const loadFromStorage = () => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) {
      const tenantId = Number.parseInt(stored, 10)
      if (!Number.isNaN(tenantId)) {
        selectedTenantId.value = tenantId
      }
    }
  } catch (error) {
    console.error('Error cargando tenant seleccionado desde localStorage:', error)
  }
}

// Guardar tenant seleccionado en localStorage
const saveToStorage = (tenantId) => {
  try {
    if (tenantId === null || tenantId === undefined) {
      localStorage.removeItem(STORAGE_KEY)
    } else {
      localStorage.setItem(STORAGE_KEY, tenantId.toString())
    }
  } catch (error) {
    console.error('Error guardando tenant seleccionado en localStorage:', error)
  }
}

// Cargar al inicializar
loadFromStorage()

export function useTenantSelection() {
  const setSelectedTenantId = (tenantId) => {
    selectedTenantId.value = tenantId
    saveToStorage(tenantId)
  }

  const clearSelectedTenant = () => {
    selectedTenantId.value = null
    saveToStorage(null)
  }

  return {
    selectedTenantId,
    setSelectedTenantId,
    clearSelectedTenant
  }
}

