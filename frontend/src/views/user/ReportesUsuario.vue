<template>
  <div class="container-fluid py-4">
    <div class="row">
      <div class="col-12">
        <div class="d-flex flex-wrap justify-content-between align-items-center mb-4 gap-3">
          <div>
            <h2 class="mb-1">
              <i class="fas fa-chart-line me-2 text-success"></i>Reportes de Mis Recursos
            </h2>
            <p class="text-muted mb-0">Resumen de ganado, potreros y vacunaciones</p>
          </div>
          <button class="btn btn-danger" @click="descargar" :disabled="descargando">
            <span v-if="descargando" class="spinner-border spinner-border-sm me-2"></span>
            <i v-else class="fas fa-file-download me-2"></i>
            Descargar PDF
          </button>
        </div>

        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-success" role="status">
            <span class="visually-hidden">Cargando...</span>
          </div>
          <p class="mt-2 text-muted">Generando resumen...</p>
        </div>

        <div v-else-if="error" class="alert alert-danger">
          <i class="fas fa-exclamation-circle me-2"></i>{{ error }}
        </div>

        <template v-else-if="resumen">
          <div class="row g-3 mb-4">
            <div class="col-12 col-sm-6 col-lg-4" v-for="card in cards" :key="card.titulo">
              <div class="card border-0 shadow-sm h-100">
                <div class="card-body">
                  <h6 class="text-muted text-uppercase fw-bold">{{ card.titulo }}</h6>
                  <p class="display-6 fw-bold mb-1">{{ card.total }}</p>
                  <p v-for="detalle in card.detalles" :key="detalle" class="text-muted mb-1">
                    {{ detalle }}
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div class="card border-0 shadow">
            <div class="card-body">
              <h4 class="card-title mb-4">Distribución por estado</h4>
              <div class="d-flex justify-content-center">
                <div class="chart-wrapper">
                  <canvas ref="chartCanvas"></canvas>
                </div>
              </div>
            </div>
          </div>

          <div class="card border-0 shadow mt-4">
            <div class="card-body">
              <h4 class="card-title mb-4">Detalle</h4>

              <div v-for="seccion in secciones" :key="seccion.titulo" class="mb-4">
                <div class="d-flex justify-content-between align-items-center">
                  <h5 class="mb-1">{{ seccion.titulo }}</h5>
                  <span class="badge bg-light text-dark">Total: {{ seccion.total }}</span>
                </div>
                <div class="table-responsive">
                  <table class="table table-sm table-striped">
                    <caption class="visually-hidden">Tabla de detalle de reportes mostrando estado y cantidad para ganado, potreros y vacunaciones</caption>
                    <thead>
                      <tr>
                        <th>Estado</th>
                        <th class="text-end">Cantidad</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="fila in seccion.detalle" :key="fila.estado">
                        <td>{{ capitalizar(fila.estado) }}</td>
                        <td class="text-end">{{ fila.cantidad }}</td>
                      </tr>
                      <tr v-if="seccion.detalle.length === 0">
                        <td colspan="2" class="text-center text-muted">Sin información disponible</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <p v-if="seccion.extra" class="text-muted small mb-0">{{ seccion.extra }}</p>
                <hr v-if="seccion !== secciones[secciones.length - 1]" />
              </div>

              <p class="text-muted small mb-0">Generado el: {{ formatearFecha(resumen.generado_en) }}</p>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script>
import reportesUsuario from '../../assets/js/reportes-usuario.js';

export default reportesUsuario;
</script>

<style scoped>
</style>

