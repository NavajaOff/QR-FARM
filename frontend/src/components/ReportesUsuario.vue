<template>
  <div class="reportes-usuario">
    <!-- Loading state -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-success" aria-live="polite" aria-label="Cargando">
        <span class="visually-hidden">Cargando...</span>
      </div>
      <p class="mt-2 text-muted">Cargando reportes...</p>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="alert alert-danger text-center">
      <i class="fas fa-exclamation-circle me-2"></i>{{ error }}
    </div>

    <!-- Content -->
    <div v-else-if="resumen">
      <!-- Summary Cards -->
      <div class="row g-3 mb-4">
        <div v-for="card in cards" :key="card.titulo" class="col-md-4">
          <div class="card border-0 shadow-sm">
            <div class="card-body">
              <h5 class="card-title">{{ card.titulo }}</h5>
              <h2 class="text-success mb-3">{{ card.total }}</h2>
              <ul class="list-unstyled mb-0">
                <li v-for="(detalle, idx) in card.detalles" :key="idx" class="text-muted small">
                  {{ detalle }}
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <!-- Chart -->
      <div class="card border-0 shadow-sm mb-4">
        <div class="card-body">
          <canvas ref="chartCanvas" style="max-height: 400px;"></canvas>
        </div>
      </div>

      <!-- Download Button -->
      <div class="text-center">
        <button 
          class="btn btn-success btn-lg" 
          @click="descargar" 
          :disabled="descargando"
        >
          <span v-if="descargando" class="spinner-border spinner-border-sm me-2"></span>
          <i v-else class="fas fa-download me-2"></i>
          {{ descargando ? 'Descargando...' : 'Descargar Reporte PDF' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import reportesUsuario from '../assets/js/reportes-usuario.js'

export default {
  ...reportesUsuario
}
</script>

<style scoped>
.reportes-usuario {
  min-height: 400px;
}
</style>

