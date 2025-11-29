<template>
  <div>
    <div class="row">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-3">
          <h2 class="mb-0">
            <i class="fas fa-building me-2"></i>Gestión de Tenants
          </h2>
          <button class="btn btn-primary" @click="openAddModal">
            <i class="fas fa-plus me-2"></i>Crear Tenant
          </button>
        </div>

        <!-- Filtros -->
        <div class="card mb-4">
          <div class="card-body">
            <div class="form-check form-switch">
              <input 
                class="form-check-input" 
                type="checkbox" 
                id="mostrarInactivos"
                v-model="mostrarInactivos"
                @change="handleToggleInactivos"
              >
              <label class="form-check-label" for="mostrarInactivos">
                Mostrar tenants inactivos
              </label>
            </div>
          </div>
        </div>

        <!-- Tabla de tenants -->
        <div class="card">
          <div class="card-body">
            <div v-if="loading" class="text-center py-4">
              <div class="spinner-border text-primary">
                <output class="visually-hidden">Cargando...</output>
              </div>
            </div>
            
            <div v-else-if="error" class="alert alert-danger">
              <i class="fas fa-exclamation-triangle me-2"></i>{{ error }}
            </div>

            <div v-else-if="tenants.length === 0" class="text-center py-4 text-muted">
              <i class="fas fa-inbox fa-3x mb-3"></i>
              <p v-if="mostrarInactivos">
                <strong>No hay tenants inactivos</strong><br>
                <small>Todos los tenants están activos actualmente.</small>
              </p>
              <p v-else>
                <strong>No hay tenants registrados</strong><br>
                <small>Comienza creando tu primer tenant.</small>
              </p>
            </div>

            <div v-else class="table-responsive">
              <table class="table table-striped table-hover">
                <caption class="visually-hidden">Tabla de gestión de tenants</caption>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Nombre</th>
                    <th>Código</th>
                    <th>Estado</th>
                    <th>Fecha Creación</th>
                    <th>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="tenant in tenants" :key="tenant.id">
                    <td>{{ tenant.id }}</td>
                    <td>{{ tenant.nombre }}</td>
                    <td>
                      <code>{{ tenant.codigo_tenant }}</code>
                    </td>
                    <td>
                      <span 
                        class="badge" 
                        :class="tenant.estado === 'activo' ? 'bg-success' : 'bg-secondary'"
                      >
                        {{ tenant.estado }}
                      </span>
                    </td>
                    <td>{{ formatearFecha(tenant.fecha_creacion) }}</td>
                    <td>
                      <button 
                        class="btn btn-sm btn-outline-primary me-2" 
                        @click="editTenant(tenant)"
                        title="Editar tenant"
                      >
                        <i class="fas fa-edit"></i>
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal de creación/edición -->
    <div class="modal fade" :class="{ 'show d-block': showModal }" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              {{ editMode ? 'Editar Tenant' : 'Crear Tenant' }}
            </h5>
            <button type="button" class="btn-close" @click="closeModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveTenant">
              <div class="mb-3">
                <label for="nombre" class="form-label">Nombre del Tenant *</label>
                <input
                  type="text"
                  class="form-control"
                  id="nombre"
                  v-model="form.nombre"
                  required
                  placeholder="Ej: Finca San José"
                >
              </div>
              
              <div class="mb-3" v-if="!editMode">
                <label for="codigo_tenant" class="form-label">Código del Tenant *</label>
                <input
                  type="text"
                  class="form-control"
                  id="codigo_tenant"
                  v-model="form.codigo_tenant"
                  required
                  placeholder="Ej: finca-san-jose"
                  pattern="[a-z0-9-]+"
                  title="Solo letras minúsculas, números y guiones"
                >
                <small class="form-text text-muted">
                  Solo letras minúsculas, números y guiones. Debe ser único.
                </small>
              </div>

              <div class="mb-3" v-if="editMode">
                <label for="codigo_tenant_edit" class="form-label">Código del Tenant</label>
                <input
                  type="text"
                  class="form-control"
                  id="codigo_tenant_edit"
                  :value="form.codigo_tenant"
                  disabled
                >
                <small class="form-text text-muted">
                  El código del tenant no se puede modificar.
                </small>
              </div>

              <div class="mb-3" v-if="editMode">
                <label for="estado" class="form-label">Estado</label>
                <select class="form-select" id="estado" v-model="form.estado">
                  <option value="activo">Activo</option>
                  <option value="inactivo">Inactivo</option>
                </select>
              </div>

              <div v-if="errorMessage" class="alert alert-danger mt-3">
                {{ errorMessage }}
              </div>

              <div class="modal-footer">
                <button type="button" class="btn btn-secondary" @click="closeModal">
                  Cancelar
                </button>
                <button type="submit" class="btn btn-primary" :disabled="saving">
                  <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
                  {{ editMode ? 'Actualizar' : 'Crear' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useTenants } from '../../composables/useTenants.js'
import Swal from 'sweetalert2'

const { tenants, loading, error, cargarTenants, crearTenant, actualizarTenant } = useTenants()

const mostrarInactivos = ref(false)
const showModal = ref(false)
const editMode = ref(false)
const saving = ref(false)
const errorMessage = ref('')
const form = ref({
  id: null,
  nombre: '',
  codigo_tenant: '',
  estado: 'activo'
})

const openAddModal = () => {
  editMode.value = false
  form.value = { id: null, nombre: '', codigo_tenant: '', estado: 'activo' }
  errorMessage.value = ''
  showModal.value = true
}

const editTenant = (tenant) => {
  editMode.value = true
  form.value = {
    id: tenant.id,
    nombre: tenant.nombre,
    codigo_tenant: tenant.codigo_tenant,
    estado: tenant.estado
  }
  errorMessage.value = ''
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  form.value = { id: null, nombre: '', codigo_tenant: '', estado: 'activo' }
  errorMessage.value = ''
}

const saveTenant = async () => {
  saving.value = true
  errorMessage.value = ''

  try {
    let result
    if (editMode.value) {
      // Pasar el filtro actual para mantener el estado después de actualizar
      const activosOnly = !mostrarInactivos.value
      result = await actualizarTenant(form.value.id, {
        nombre: form.value.nombre,
        estado: form.value.estado
      }, activosOnly)
    } else {
      result = await crearTenant({
        nombre: form.value.nombre,
        codigo_tenant: form.value.codigo_tenant.toLowerCase().replaceAll(' ', '-').replaceAll('--', '-')
      })
    }

    if (result.success) {
      await Swal.fire({
        icon: 'success',
        title: editMode.value ? 'Tenant actualizado' : 'Tenant creado',
        text: `El tenant se ha ${editMode.value ? 'actualizado' : 'creado'} exitosamente`,
        timer: 1500,
        showConfirmButton: false
      })
      closeModal()
      // Recargar con el filtro actual (mantener el estado del switch)
      const activosOnly = !mostrarInactivos.value
      console.log('[GestionarTenants] Recargando después de guardar - activosOnly:', activosOnly)
      await cargarTenants(activosOnly)
    } else {
      errorMessage.value = result.message || 'Error al guardar el tenant'
    }
  } catch (err) {
    errorMessage.value = err.message || 'Error inesperado'
  } finally {
    saving.value = false
  }
}

const handleToggleInactivos = () => {
  // Si mostrarInactivos es true, cargar todos incluyendo inactivos (activosOnly = false)
  // Si mostrarInactivos es false, cargar solo activos (activosOnly = true)
  const activosOnly = !mostrarInactivos.value
  console.log('[GestionarTenants] Cambiando filtro:')
  console.log('  - mostrarInactivos:', mostrarInactivos.value)
  console.log('  - activosOnly (parámetro a enviar):', activosOnly)
  console.log('  - URL será: /tenants?activos_only=' + activosOnly)
  cargarTenants(activosOnly)
}

const formatearFecha = (fecha) => {
  if (!fecha) return '-'
  const date = new Date(fecha)
  return date.toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

onMounted(() => {
  // Al montar, cargar solo activos (mostrarInactivos = false, activosOnly = true)
  cargarTenants(true)
})
</script>

<style scoped>
code {
  background-color: #f8f9fa;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 0.9em;
}
</style>

