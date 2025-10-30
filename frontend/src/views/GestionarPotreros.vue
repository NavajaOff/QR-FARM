<template>
  <div>
    <!-- Header -->
    <nav class="navbar navbar-dark bg-success">
      <div class="container-fluid">
        <div class="d-flex align-items-center w-100">
          <button
            class="btn btn-outline-light d-md-none me-2"
            type="button"
            data-bs-toggle="offcanvas"
            data-bs-target="#sidebarMenu"
            aria-controls="sidebarMenu"
          >
            <i class="fas fa-bars"></i>
          </button>

          <div class="d-flex align-items-center">
            <i class="fas fa-user-circle fa-lg me-2"></i>
            <span class="fw-bold">Usuario</span>
          </div>

          <router-link class="navbar-brand mx-auto d-flex align-items-center" to="/">
            <span class="fw-bold fs-2">QR FARM</span>
            <i class="fas fa-cow ms-2 logo-icon"></i>
          </router-link>

          <div class="navbar-brand ms-auto">
            <i class="fas fa-cow fa-2x"></i>
          </div>
        </div>
      </div>
    </nav>

    <!-- Offcanvas Sidebar (móvil) -->
    <div
      class="offcanvas offcanvas-start d-md-none"
      tabindex="-1"
      id="sidebarMenu"
      aria-labelledby="sidebarMenuLabel"
    >
      <div class="offcanvas-header">
        <h5 class="offcanvas-title" id="sidebarMenuLabel">Menú</h5>
        <button type="button" class="btn-close text-reset" data-bs-dismiss="offcanvas" aria-label="Close"></button>
      </div>
      <div class="offcanvas-body">
        <nav class="nav flex-column">
          <router-link class="nav-link" to="/inventario"><i class="fas fa-boxes me-2"></i>Inventario</router-link>

          <!-- Dropdown Gestión -->
          <a
            class="nav-link d-flex justify-content-between align-items-center"
            data-bs-toggle="collapse"
            href="#gestionMenuMobile"
            role="button"
            aria-expanded="false"
            aria-controls="gestionMenuMobile"
          >
            <span><i class="fas fa-tasks me-2"></i>Gestión</span>
            <i class="fas fa-chevron-down"></i>
          </a>
          <div class="collapse ps-3" id="gestionMenuMobile">
            <router-link class="nav-link" to="/gestionar_animales"><i class="fas fa-cow me-2"></i>Animales</router-link>
            <router-link class="nav-link active" to="/gestionar_potreros"><i class="fas fa-map-marked-alt me-2"></i>Potreros</router-link>
            <router-link class="nav-link" to="/registro_vacunacion"><i class="fas fa-syringe me-2"></i>Vacunación</router-link>
          </div>

          <router-link class="nav-link" to="/escanear_qr"><i class="fas fa-qrcode me-2"></i>Escanear QR</router-link>
          <router-link class="nav-link" to="/login"><i class="fas fa-sign-out-alt me-2"></i>Salir</router-link>
        </nav>
      </div>
    </div>

    <!-- Sidebar fijo en desktop -->
    <div class="d-none d-md-block sidebar">
      <nav class="nav flex-column">
        <router-link class="nav-link" to="/inventario"><i class="fas fa-boxes me-2"></i>Inventario</router-link>

        <!-- Dropdown Gestión -->
        <a
          class="nav-link d-flex justify-content-between align-items-center"
          data-bs-toggle="collapse"
          href="#gestionMenuDesktop"
          role="button"
          aria-expanded="false"
          aria-controls="gestionMenuDesktop"
        >
          <span><i class="fas fa-tasks me-2"></i>Gestión</span>
          <i class="fas fa-chevron-down"></i>
        </a>
        <div class="collapse ps-3" id="gestionMenuDesktop">
          <router-link class="nav-link" to="/gestionar_animales"><i class="fas fa-cow me-2"></i>Animales</router-link>
          <router-link class="nav-link active" to="/gestionar_potreros"><i class="fas fa-map-marked-alt me-2"></i>Potreros</router-link>
          <router-link class="nav-link" to="/registro_vacunacion"><i class="fas fa-syringe me-2"></i>Vacunación</router-link>
        </div>

        <router-link class="nav-link" to="/escanear_qr"><i class="fas fa-qrcode me-2"></i>Escanear QR</router-link>
        <router-link class="nav-link" to="/login"><i class="fas fa-sign-out-alt me-2"></i>Salir</router-link>
      </nav>
    </div>

    <!-- Main Content -->
    <div class="main-content">
      <div class="container-fluid py-4 py-md-5">
        <div class="row justify-content-center g-4">
          <div class="col-12">
            <div class="mb-4 text-center">
              <h2 class="fw-bold text-dark">
                <i class="fas fa-map-marked-alt me-2 text-success"></i>Gestionar Potreros
              </h2>
              <p class="lead text-muted">Administra y controla tus potreros de manera eficiente</p>
            </div>

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

              <div class="card border-0 shadow-lg" style="min-width: 350px; max-width: 600px;">
                <div class="card-header bg-success text-white d-flex justify-content-between align-items-center">
                  <h5 class="mb-0"><i class="fas fa-leaf me-2"></i>{{ potreros[currentIndex].nombre }}</h5>
                  <button class="btn btn-light btn-sm" @click="toggleAccordion">
                    <i :class="accordionOpen ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
                  </button>
                </div>
                <div class="card-body p-3 p-sm-4" v-show="accordionOpen">
                  <div class="row g-3 mb-3">
                    <div class="col-6"><strong>Estado:</strong> <span class="badge" :class="estadoClass(potreros[currentIndex].estado)">{{ potreros[currentIndex].estado }}</span></div>
                    <div class="col-6"><strong>Capacidad:</strong> {{ potreros[currentIndex].capacidad || 'No definida' }} Animales</div>
                  </div>
                  <div class="row g-3 mb-3">
                    <div class="col-6"><strong>Ocupación:</strong> {{ potreros[currentIndex].ocupacion }} Animales</div>
                    <div class="col-6"><strong>Hectáreas:</strong> {{ potreros[currentIndex].hectareas || 'No definida' }} ha</div>
                  </div>
                  <div class="row g-3 mb-3">
                    <div class="col-6"><strong>Tipo de pasto:</strong> {{ potreros[currentIndex].pasto }}</div>
                    <div class="col-6"><strong>Responsable:</strong> {{ potreros[currentIndex].responsable }}</div>
                  </div>
                  <div class="row g-3 mb-3">
                    <div class="col-6"><strong>Fecha de último uso:</strong> {{ potreros[currentIndex].fechaUso || 'No registrada' }}</div>
                    <div class="col-6"><strong>Próxima limpieza:</strong> <input type="date" class="form-control d-inline-block w-auto" style="min-width:150px;"></div>
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
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import {
  currentIndex,
  accordionOpen,
  potreros,
  tiposPasto,
  estadosPotrero,
  personasUsuario,
  loading,
  error,
  cargarDatosIniciales,
  estadoClass,
  crearPotrero,
  editarPotrero,
  prevPotrero,
  nextPotrero,
  toggleAccordion
} from '../assets/js/gestionar-potreros.js';

// Hacer variables disponibles en el template
const templateData = {
  currentIndex,
  accordionOpen,
  potreros,
  tiposPasto,
  estadosPotrero,
  personasUsuario,
  loading,
  error,
  estadoClass,
  crearPotrero,
  editarPotrero,
  prevPotrero,
  nextPotrero,
  toggleAccordion,
  cargarPotreros: () => cargarDatosIniciales() // Para el botón de reintentar
};

// Lifecycle
onMounted(() => {
  cargarDatosIniciales();
});
</script>

<style scoped>
@import '../assets/css/gestionar-potreros.css';
</style>
