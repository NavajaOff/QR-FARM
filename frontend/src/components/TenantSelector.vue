<template>
  <div v-if="isSuperAdmin" class="tenant-selector">
    <div class="card border-primary mb-3">
      <div class="card-body">
        <label for="tenant-select" class="form-label fw-bold">
          <i class="fas fa-building me-2"></i>Filtrar por Tenant
        </label>
        <select
          id="tenant-select"
          class="form-select"
          v-model="selectedTenantId"
          @change="onTenantChange"
        >
          <option :value="null">-- Todos los Tenants --</option>
          <option
            v-for="tenant in tenants"
            :key="tenant.id"
            :value="tenant.id"
          >
            {{ tenant.nombre }} ({{ tenant.codigo_tenant }})
          </option>
        </select>
        <small class="form-text text-muted" v-if="selectedTenantId">
          Mostrando datos del tenant: <strong>{{ selectedTenantName }}</strong>
        </small>
        <small class="form-text text-muted" v-else>
          <strong>Advertencia:</strong> Sin tenant seleccionado, no se mostrarán datos. Seleccione un tenant para ver información.
        </small>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useTenants } from '../composables/useTenants.js'
import { useTenantSelection } from '../composables/useTenantSelection.js'
import authService from '../services/authService.js'

const { tenants, loading, error, cargarTenants } = useTenants()
const { selectedTenantId, setSelectedTenantId } = useTenantSelection()

const isSuperAdmin = computed(() => {
  return authService.getRole() === 'super_admin'
})

const selectedTenantName = computed(() => {
  if (!selectedTenantId.value) return ''
  const tenant = tenants.value.find(t => t.id === selectedTenantId.value)
  return tenant ? tenant.nombre : ''
})

const onTenantChange = () => {
  setSelectedTenantId(selectedTenantId.value)
  // Emitir evento para que otros componentes se actualicen
  window.dispatchEvent(new CustomEvent('tenant-selected', { 
    detail: { tenantId: selectedTenantId.value } 
  }))
}

onMounted(async () => {
  if (isSuperAdmin.value) {
    await cargarTenants(true) // Cargar solo tenants activos
  }
})
</script>

<style scoped>
.tenant-selector {
  margin-bottom: 1rem;
}

.tenant-selector .card {
  background-color: #f8f9fa;
}

.tenant-selector .form-select {
  border-color: #0d6efd;
}

.tenant-selector .form-select:focus {
  border-color: #0d6efd;
  box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25);
}
</style>

