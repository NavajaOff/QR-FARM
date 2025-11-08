<template>
  <div class="container-fluid py-4">
    <div class="row">
      <div class="col-12">
        <div class="d-flex flex-wrap justify-content-between align-items-center mb-4 gap-3">
          <div>
            <h2 class="mb-1">
              <i class="fas fa-map-marked-alt me-2 text-success"></i>Mis Potreros
            </h2>
            <p class="text-muted mb-0">Consulta el estado de tus potreros en tiempo real</p>
          </div>
          <button class="btn btn-outline-success" @click="cargarPotreros" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
            <i v-else class="fas fa-sync-alt me-2"></i>
            Actualizar
          </button>
        </div>

        <div class="card border-0 shadow-sm mb-4">
          <div class="card-body">
            <div class="row g-3">
              <div class="col-md-4">
                <label class="form-label">Buscar:</label>
                <input
                  v-model="busqueda"
                  type="text"
                  class="form-control"
                  placeholder="Escribe el nombre del potrero"
                />
              </div>
              <div class="col-md-4">
                <label class="form-label">Estado:</label>
                <select v-model="filtroEstado" class="form-select">
                  <option value="">Todos los estados</option>
                  <option v-for="estado in estadosDisponibles" :key="estado" :value="estado">{{ capitalizar(estado) }}</option>
                </select>
              </div>
              <div class="col-md-4">
                <label class="form-label">Tipo de pasto:</label>
                <select v-model="filtroPasto" class="form-select">
                  <option value="">Todos</option>
                  <option v-for="pasto in tiposPasto" :key="pasto" :value="pasto">{{ capitalizar(pasto) }}</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-success" role="status">
            <span class="visually-hidden">Cargando...</span>
          </div>
          <p class="mt-2 text-muted">Obteniendo información de potreros...</p>
        </div>

        <div v-else-if="error" class="alert alert-danger text-center">
          <i class="fas fa-exclamation-triangle me-2"></i>
          {{ error }}
        </div>

        <div v-else-if="potrerosFiltrados.length === 0" class="text-center py-5">
          <i class="fas fa-map-marked-alt fa-4x text-muted mb-3"></i>
          <h4 class="text-muted">No hay potreros que coincidan con los filtros</h4>
          <p class="text-muted">Intenta con otros criterios o limpia los filtros actuales.</p>
        </div>

        <div v-else class="row g-4">
          <div class="col-12 col-md-6 col-xl-4" v-for="potrero in potrerosFiltrados" :key="potrero.id">
            <div class="card border-0 shadow h-100">
              <div class="card-header bg-success text-white">
                <div class="d-flex justify-content-between align-items-center">
                  <h5 class="mb-0">
                    <i class="fas fa-leaf me-2"></i>{{ potrero.nombre || `Potrero #${potrero.id}` }}
                  </h5>
                  <span class="badge bg-light text-success text-uppercase">{{ capitalizar(potrero.estado || 'desconocido') }}</span>
                </div>
              </div>
              <div class="card-body">
                <ul class="list-unstyled mb-3">
                  <li class="mb-2">
                    <strong>Capacidad:</strong> {{ potrero.capacidad ?? 'No definida' }} animales
                  </li>
                  <li class="mb-2">
                    <strong>Ocupación:</strong> {{ potrero.ocupacion ?? 0 }} animales
                  </li>
                  <li class="mb-2">
                    <strong>Hectáreas:</strong> {{ potrero.hectareas ?? 'No definido' }}
                  </li>
                  <li class="mb-2">
                    <strong>Tipo de pasto:</strong> {{ capitalizar(potrero.tipo_pasto_nombre || potrero.tipo_pasto || 'No definido') }}
                  </li>
                  <li class="mb-2">
                    <strong>Próxima limpieza:</strong> {{ formatearFecha(potrero.proxima_limpieza || potrero.proximaLimpieza) }}
                  </li>
                  <li class="mb-2">
                    <strong>Última limpieza:</strong> {{ formatearFecha(potrero.ultima_limpieza || potrero.ultimaLimpieza) }}
                  </li>
                </ul>
                <p v-if="potrero.descripcion" class="text-muted small">{{ potrero.descripcion }}</p>
              </div>
              <div class="card-footer bg-light">
                <small class="text-muted">
                  Responsable: {{ potrero.responsable_nombre || potrero.responsable || 'No asignado' }}
                </small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { usePotreros } from '../../composables/usePotreros.js'

const { potreros, loading, error, cargarPotreros } = usePotreros()
const busqueda = ref('')
const filtroEstado = ref('')
const filtroPasto = ref('')

const estadosDisponibles = computed(() => {
  const estados = new Set()
  potreros.value.forEach(p => {
    if (p.estado) estados.add(p.estado)
  })
  return Array.from(estados)
})

const tiposPasto = computed(() => {
  const tipos = new Set()
  potreros.value.forEach(p => {
    if (p.tipo_pasto_nombre) tipos.add(p.tipo_pasto_nombre)
    else if (p.tipo_pasto) tipos.add(p.tipo_pasto)
  })
  return Array.from(tipos)
})

const potrerosFiltrados = computed(() => {
  return potreros.value.filter(p => {
    const coincideBusqueda =
      !busqueda.value ||
      (p.nombre && p.nombre.toLowerCase().includes(busqueda.value.toLowerCase()))
    const coincideEstado = !filtroEstado.value || p.estado === filtroEstado.value
    const coincidePasto =
      !filtroPasto.value ||
      p.tipo_pasto === filtroPasto.value ||
      p.tipo_pasto_nombre === filtroPasto.value

    return coincideBusqueda && coincideEstado && coincidePasto
  })
})

onMounted(() => {
  cargarPotreros()
})

const capitalizar = (texto) => {
  if (!texto) return ''
  return texto.toString().charAt(0).toUpperCase() + texto.toString().slice(1)
}

const formatearFecha = (fecha) => {
  if (!fecha) return 'No registrada'
  try {
    return new Date(fecha).toLocaleDateString()
  } catch {
    return fecha
  }
}
</script>

<style scoped>
.card {
  border-radius: 16px;
}

.card-header {
  border-radius: 16px 16px 0 0;
}
</style>

