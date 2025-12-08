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
                <label class="form-label" for="usuario-buscar-animal">Buscar por nombre</label>
                <input id="usuario-buscar-animal" v-model="busqueda" type="text" class="form-control" placeholder="Ej. Rosita" />
              </div>
              <div class="col-md-4">
                <label class="form-label" for="usuario-filtro-raza">Raza</label>
                <select id="usuario-filtro-raza" v-model="filtroRaza" class="form-select">
                  <option value="">Todas</option>
                  <option v-for="raza in razasDisponibles" :key="raza" :value="raza">{{ raza }}</option>
                </select>
              </div>
              <div class="col-md-4">
                <label class="form-label" for="usuario-filtro-estado">Estado</label>
                <select id="usuario-filtro-estado" v-model="filtroEstado" class="form-select">
                  <option value="">Todos</option>
                  <option v-for="estado in estadosDisponibles" :key="estado" :value="estado">{{ capitalizar(estado) }}</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-success" aria-live="polite" aria-label="Cargando">
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
                  <p class="small text-muted mb-2">Código QR</p>
                  <img
                    :src="`${apiBaseUrl}/animales/qr/${animal.codigo_qr}.png`"
                    alt="Código QR"
                    class="img-fluid rounded border"
                    style="min-width: 300px; max-width: 400px; width: 100%;"
                  />
                  <p class="small text-muted mt-2">Apunta la cámara hacia el QR para escanear</p>
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
import { computed } from 'vue'
import { useGestionarAnimalesUsuario } from '../../assets/js/gestionar-animales-usuario.js'
import { getApiBaseUrl } from '../../utils/config.js'

const {
  busqueda,
  filtroRaza,
  filtroEstado,
  animales,
  loading,
  error,
  cargarAnimales,
  razasDisponibles,
  estadosDisponibles,
  animalesFiltrados,
  capitalizar,
  estadoClass,
  verPerfilAnimal,
  editarAnimal
} = useGestionarAnimalesUsuario()

const apiBaseUrl = computed(() => getApiBaseUrl())
</script>

<style scoped>
@import '../../assets/css/gestionar-animales-usuario.css';
</style>
