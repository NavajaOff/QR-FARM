<template>
  <div>
    <div class="row justify-content-center g-4">
      <div class="col-12">
        <div class="mb-4 text-center">
          <h2 class="fw-bold text-dark">
            <i class="fas fa-map-marked-alt me-2 text-success"></i>Gestionar Potreros
          </h2>
          <p class="lead text-muted">Administra y controla tus potreros de manera eficiente</p>
        </div>

        <!-- Selector de Tenant para Super Admin -->
        <TenantSelector v-if="isSuperAdmin" @tenant-changed="onTenantChanged" />

        <!-- Loading State -->
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-success" role="status">
            <span class="visually-hidden">Cargando...</span>
          </div>
          <p class="mt-2 text-muted">Cargando potreros...</p>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="alert alert-danger text-center">
          <i class="fas fa-exclamation-triangle me-2"></i>
          {{ error }}
          <button class="btn btn-sm btn-outline-danger ms-3" @click="cargarPotreros">
            <i class="fas fa-redo me-1"></i>Reintentar
          </button>
        </div>

        <!-- Empty State -->
        <div v-else-if="potreros.length === 0" class="text-center py-5">
          <i class="fas fa-map-marked-alt fa-4x text-muted mb-3"></i>
          <h4 class="text-muted">No hay potreros registrados</h4>
          <p class="text-muted">Aún no se han creado potreros en el sistema.</p>
          <button class="btn btn-success" @click="crearPotrero()">
            <i class="fas fa-plus me-1"></i>Crear Primer Potrero
          </button>
        </div>

        <!-- Card Potrero -->
        <div v-else class="d-flex justify-content-center align-items-start gap-2">
          <button class="btn btn-outline-secondary" @click="prevPotrero" :disabled="potreros.length <= 1"><i class="fas fa-chevron-left"></i></button>

          <div class="card border-0 shadow-lg" style="min-width: 450px; max-width: 700px;">
            <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
              <h5 class="mb-0"><i class="fas fa-leaf me-2"></i>{{ potreros[currentIndex].nombre }}</h5>
              <button class="btn btn-light btn-sm" @click="toggleAccordion">
                <i :class="accordionOpen ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
              </button>
            </div>
            <div class="card-body p-4 p-sm-5" v-show="accordionOpen">
              <div class="row g-3 mb-3">
                <div class="col-6"><strong>Estado:</strong> <span class="badge" :class="estadoClass(potreros[currentIndex].estado)">{{ potreros[currentIndex].estado }}</span></div>
                <div class="col-6"><strong>Capacidad:</strong> {{ potreros[currentIndex].capacidad || 'No definida' }} Animales</div>
              </div>
              <div class="row g-3 mb-3">
                <div class="col-6"><strong>Ocupación:</strong> {{ potreros[currentIndex].ocupacion || 0 }} Animales</div>
                <div class="col-6"><strong>Hectáreas:</strong> {{ potreros[currentIndex].hectareas || 'No definida' }} ha</div>
              </div>
              <div class="row g-3 mb-3">
                <div class="col-6"><strong>Fecha de último uso:</strong> {{ potreros[currentIndex].fechaUso || 'No registrada' }}</div>
                <div class="col-6"><strong>Responsable:</strong> {{ potreros[currentIndex].responsable }}</div>
              </div>
              <div class="row g-3 mb-3">
                <div class="col-12"><strong>Próxima limpieza:</strong> {{ potreros[currentIndex].proximaLimpieza || 'No programada' }}</div>
              </div>
              <div class="row g-3 mb-3">
                <div class="col-6"><strong>Área:</strong> {{ potreros[currentIndex].area || 'No definida' }} m²</div>
                <div class="col-6"><strong>Última limpieza:</strong> {{ potreros[currentIndex].ultimaLimpieza || 'No registrada' }}</div>
              </div>
              <div class="row g-3 mb-3" v-if="potreros[currentIndex].descripcion">
                <div class="col-12"><strong>Descripción:</strong> {{ potreros[currentIndex].descripcion }}</div>
              </div>
              <div class="d-flex gap-2 justify-content-center">
                <button class="btn btn-primary" @click="editarPotrero(potreros[currentIndex].id)"><i class="fas fa-edit me-1"></i>Editar</button>
                <button class="btn btn-success" @click="crearPotrero()"><i class="fas fa-plus me-1"></i>Crear Potrero</button>
              </div>
            </div>
          </div>

          <button class="btn btn-outline-secondary" @click="nextPotrero" :disabled="potreros.length <= 1"><i class="fas fa-chevron-right"></i></button>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
import gestionarPotrerosAdmin from '../../assets/js/gestionar-potreros-admin.js';
import TenantSelector from '../../components/TenantSelector.vue';
import authService from '../../services/authService.js';

export default {
  ...gestionarPotrerosAdmin,
  components: {
    TenantSelector
  },
  computed: {
    ...gestionarPotrerosAdmin.computed,
    isSuperAdmin() {
      return authService.getRole() === 'super_admin';
    }
  },
  methods: {
    ...gestionarPotrerosAdmin.methods,
    onTenantChanged() {
      // Recargar potreros cuando cambia el tenant
      this.cargarPotreros();
    }
  }
};
</script>

<style scoped>
@import '../../assets/css/gestionar-potreros-admin.css';
</style>
