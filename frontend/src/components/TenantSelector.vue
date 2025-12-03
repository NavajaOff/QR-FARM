<template>
  <div v-if="shouldShowSelector" class="tenant-selector">
    <div class="dropdown">
      <button
        class="btn btn-outline-light dropdown-toggle d-flex align-items-center"
        type="button"
        id="tenantSelectorDropdown"
        data-bs-toggle="dropdown"
        aria-expanded="false"
        :disabled="loading"
      >
        <i class="fas fa-building me-2"></i>
        <span class="d-none d-sm-inline">
          {{ selectedTenantName || 'Seleccionar Tenant' }}
        </span>
        <span class="d-sm-none">Tenant</span>
        <span v-if="selectedTenantId" class="badge bg-success ms-2">
          {{ selectedTenantId }}
        </span>
        <span v-else class="badge bg-warning text-dark ms-2">
          Todos
        </span>
      </button>
      <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="tenantSelectorDropdown">
        <li>
          <h6 class="dropdown-header">
            <i class="fas fa-filter me-2"></i>Filtrar por Tenant
          </h6>
        </li>
        <li>
          <hr class="dropdown-divider">
        </li>
        <li>
          <a
            class="dropdown-item"
            :class="{ active: !selectedTenantId }"
            href="#"
            @click.prevent="handleSelectTenant(null)"
          >
            <i class="fas fa-globe me-2"></i>
            <strong>Ver todos los tenants</strong>
            <span v-if="!selectedTenantId" class="badge bg-primary ms-2">Activo</span>
          </a>
        </li>
        <li v-if="loading">
          <div class="dropdown-item text-center">
            <div class="spinner-border spinner-border-sm text-primary" role="status">
              <span class="visually-hidden">Cargando...</span>
            </div>
            <output class="d-block mt-2 text-muted">Cargando tenants...</output>
          </div>
        </li>
        <li v-else-if="error">
          <div class="dropdown-item text-danger">
            <i class="fas fa-exclamation-triangle me-2"></i>
            <small>Error al cargar tenants</small>
          </div>
        </li>
        <li v-else-if="tenants.length === 0">
          <div class="dropdown-item text-muted">
            <small>No hay tenants disponibles</small>
          </div>
        </li>
        <template v-else>
          <li v-for="tenant in tenants" :key="tenant.id">
            <a
              class="dropdown-item"
              :class="{ active: selectedTenantId === tenant.id }"
              href="#"
              @click.prevent="handleSelectTenant(tenant.id, tenant.nombre)"
            >
              <i class="fas fa-building me-2"></i>
              {{ tenant.nombre }}
              <small class="text-muted d-block ms-4">{{ tenant.codigo_tenant }}</small>
              <span v-if="selectedTenantId === tenant.id" class="badge bg-success ms-2">Activo</span>
            </a>
          </li>
        </template>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { onMounted, watch } from 'vue'
import { useTenantSelector } from '../composables/useTenantSelector.js'
import { useRouter } from 'vue-router'

const router = useRouter()
const {
  selectedTenantId,
  selectedTenantName,
  tenants,
  loading,
  error,
  shouldShowSelector,
  selectTenant,
  loadTenants
} = useTenantSelector()

const handleSelectTenant = (tenantId, tenantName = null) => {
  selectTenant(tenantId, tenantName)
  
  // Emitir evento para que otros componentes se actualicen
  globalThis.dispatchEvent(new CustomEvent('tenant-changed', {
    detail: { tenantId, tenantName }
  }))
  
  // Recargar la página actual para aplicar el filtro
  // Esto asegura que todos los datos se recarguen con el nuevo tenant
  router.go(0)
}

// Cargar tenants al montar
onMounted(async () => {
  if (shouldShowSelector.value) {
    await loadTenants()
  }
})

// Observar cambios en shouldShowSelector
watch(shouldShowSelector, async (newValue) => {
  if (newValue) {
    await loadTenants()
  }
})
</script>

<style scoped>
.tenant-selector {
  margin-right: 1rem;
}

.dropdown-toggle {
  min-width: 150px;
  justify-content: space-between;
}

.dropdown-menu {
  max-height: 400px;
  overflow-y: auto;
  min-width: 280px;
}

.dropdown-item.active {
  background-color: var(--bs-primary);
  color: white;
}

.dropdown-item.active .badge {
  background-color: rgba(255, 255, 255, 0.3) !important;
}

.dropdown-item:hover {
  background-color: var(--bs-light);
}

.dropdown-item.active:hover {
  background-color: var(--bs-primary);
}

.dropdown-header {
  font-weight: 600;
  color: var(--bs-primary);
}

@media (max-width: 576px) {
  .dropdown-toggle {
    min-width: auto;
    padding: 0.375rem 0.75rem;
  }
}
</style>
