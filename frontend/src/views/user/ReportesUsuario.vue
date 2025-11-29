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
        </div>
        <reportes-usuario></reportes-usuario>
      </div>
    </div>
  </div>
</template>

<script>
import ReportesUsuario from '../../components/ReportesUsuario.vue';

export default {
  name: 'ReportesUsuario',
  components: {
    ReportesUsuario
  }
};
</script>

<style scoped>
/* Styles for user reports page */
</style>
