<template>
  <div class="container-fluid py-4">
    <div class="row">
      <div class="col-12">
        <h2 class="mb-4">
          <i class="fas fa-syringe me-2 text-primary"></i>Registro de Vacunación
        </h2>
        <registro-vacunacion-base></registro-vacunacion-base>
      </div>
    </div>
  </div>
</template>

<script>
import RegistroVacunacionBase from '../../components/RegistroVacunacionBase.vue';

export default {
  name: 'RegistroVacunacionUsuario',
  components: {
    RegistroVacunacionBase
  }
};
</script>

<style scoped>
/* Styles for user vaccination registration page */
</style>
