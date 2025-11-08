<template>
  <div class="container-fluid py-4">
    <div class="row">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4 gap-3 flex-wrap">
          <h2 class="mb-0">
            <i class="fas fa-cow me-2 text-success"></i>Gestionar Animales
          </h2>
          <button class="btn btn-outline-success" @click="cargarAnimales" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
            <i v-else class="fas fa-sync-alt me-2"></i>Actualizar
          </button>
        </div>

        <div class="card border-0 shadow-sm mb-4">
          <div class="card-body">
            <div class="row g-3">
              <div class="col-md-4">
                <label class="form-label">Buscar por nombre</label>
                <input v-model="busqueda" type="text" class="form-control" placeholder="Ej. Rosita" />
              </div>
              <div class="col-md-4">
                <label class="form-label">Raza</label>
                <select v-model="filtroRaza" class="form-select">
                  <option value="">Todas</option>
                  <option v-for="raza in razasDisponibles" :key="raza" :value="raza">{{ raza }}</option>
                </select>
              </div>
              <div class="col-md-4">
                <label class="form-label">Estado</label>
                <select v-model="filtroEstado" class="form-select">
                  <option value="">Todos</option>
                  <option v-for="estado in estadosDisponibles" :key="estado" :value="estado">{{ capitalizar(estado) }}</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-success" role="status">
            <span class="visually-hidden">Cargando...</span>
          </div>
          <p class="mt-2 text-muted">Cargando animales...</p>
        </div>

        <div v-else-if="error" class="alert alert-danger text-center">
          <i class="fas fa-exclamation-circle me-2"></i>{{ error }}
        </div>

        <div v-else-if="animales.length === 0" class="text-center py-5">
          <i class="fas fa-cow fa-4x text-muted mb-3"></i>
          <h4 class="text-muted">No hay animales registrados</h4>
          <p class="text-muted">Cuando registres tu ganado aparecerá aquí.</p>
        </div>

        <div v-else class="row g-4">
          <div class="col-12 col-sm-6 col-lg-4" v-for="animal in animalesFiltrados" :key="animal.id">
            <div class="card border-0 shadow-sm h-100">
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-center mb-3">
                  <h5 class="mb-0">{{ animal.nombre || `Animal #${animal.id}` }}</h5>
                  <span class="badge" :class="estadoClass(animal.estado)">{{ capitalizar(animal.estado) }}</span>
                </div>
                <ul class="list-unstyled mb-3">
                  <li class="mb-2"><strong>Raza:</strong> {{ animal.raza || 'Sin información' }}</li>
                  <li class="mb-2"><strong>Edad:</strong> {{ animal.edad ?? 'Sin información' }}</li>
                  <li class="mb-2"><strong>Peso:</strong> {{ animal.peso ?? 'Sin información' }}</li>
                  <li class="mb-2"><strong>Sexo:</strong> {{ capitalizar(animal.sexo) }}</li>
                </ul>
                <div v-if="animal.codigo_qr" class="text-center">
                  <img
                    :src="`http://localhost:5000/api/animales/qr/${animal.codigo_qr}.png`"
                    alt="Código QR"
                    class="img-fluid rounded"
                    style="max-width: 160px;"
                  />
                </div>
              </div>
              <div class="card-footer bg-light">
                <div class="d-flex justify-content-between">
                  <button class="btn btn-sm btn-outline-primary" @click="verPerfilAnimal(animal)">
                    <i class="fas fa-eye me-1"></i>Detalles
                  </button>
                  <button class="btn btn-sm btn-outline-warning" @click="editarAnimal(animal)">
                    <i class="fas fa-edit me-1"></i>Editar
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="animales.length > 0" class="text-center mt-4">
          <p class="text-muted mb-0">Las tarjetas se actualizan automáticamente cuando hay nuevos registros.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import Swal from 'sweetalert2'
import authService from '../../services/authService.js'
import { useGanado } from '../../composables/useGanado.js'

const busqueda = ref('')
const filtroRaza = ref('')
const filtroEstado = ref('')

const { ganado: animales, loading, error, cargarGanado } = useGanado()

const cargarAnimales = () => cargarGanado()

onMounted(() => {
  if (!authService.isAuthenticated() || !authService.isUser()) {
    window.location.href = '/login'
    return
  }
  cargarGanado()
})

const razasDisponibles = computed(() => {
  const razas = new Set()
  animales.value.forEach(a => {
    if (a.raza) razas.add(a.raza)
  })
  return Array.from(razas)
})

const estadosDisponibles = computed(() => {
  const estados = new Set()
  animales.value.forEach(a => {
    if (a.estado) estados.add(a.estado)
  })
  return Array.from(estados)
})

const animalesFiltrados = computed(() => {
  return animales.value.filter(a => {
    const coincideNombre = !busqueda.value || (a.nombre || '').toLowerCase().includes(busqueda.value.toLowerCase())
    const coincideRaza = !filtroRaza.value || a.raza === filtroRaza.value
    const coincideEstado = !filtroEstado.value || a.estado === filtroEstado.value
    return coincideNombre && coincideRaza && coincideEstado
  })
})

const capitalizar = valor => {
  if (!valor) return ''
  return valor.charAt(0).toUpperCase() + valor.slice(1)
}

const estadoClass = estado => {
  if (!estado) return 'bg-secondary'
  const map = {
    activo: 'bg-success',
    saludable: 'bg-success',
    enfermo: 'bg-danger',
    revision: 'bg-warning',
    vendido: 'bg-secondary'
  }
  return map[estado] || 'bg-secondary'
}

const verPerfilAnimal = animal => {
  const html = `
    <div class="text-start">
      <p><strong>ID:</strong> ${animal.id}</p>
      <p><strong>Nombre:</strong> ${animal.nombre || 'Sin información'}</p>
      <p><strong>Raza:</strong> ${animal.raza || 'Sin información'}</p>
      <p><strong>Edad:</strong> ${animal.edad ?? 'Sin información'}</p>
      <p><strong>Peso:</strong> ${animal.peso ?? 'Sin información'}</p>
      <p><strong>Estado:</strong> ${capitalizar(animal.estado)}</p>
    </div>
  `
  Swal.fire({
    title: 'Detalle del animal',
    html,
    confirmButtonColor: '#28a745'
  })
}

const editarAnimal = () => {
  Swal.fire('Funcionalidad en desarrollo', 'Pronto podrás editar tus animales desde aquí.', 'info')
}
</script>

<style scoped>
.card {
  border-radius: 16px;
}

.card-footer {
  border-radius: 0 0 16px 16px;
}
</style>
