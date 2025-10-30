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
            style="margin-right: 16px;"
          >
            <i class="fas fa-bars"></i>
          </button>
          <i class="fas fa-user-circle fa-lg me-2"></i>
          <span class="fw-bold">Usuario</span>
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

    <!-- Notification Icon -->
    <div class="notification-icon" style="position: fixed; top: 70px; right: 20px; z-index: 1000;">
      <button class="btn btn-light rounded-circle shadow" @click="mostrarNotificaciones">
        <i class="fas fa-bell fa-lg"></i>
        <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">3</span>
      </button>
    </div>

    <!-- Offcanvas Sidebar (móvil) -->
    <div class="offcanvas offcanvas-start d-md-none" tabindex="-1" id="sidebarMenu" aria-labelledby="sidebarMenuLabel">
      <div class="offcanvas-header">
        <h5 class="offcanvas-title" id="sidebarMenuLabel">Menú</h5>
        <button type="button" class="btn-close text-reset" data-bs-dismiss="offcanvas" aria-label="Close"></button>
      </div>
      <div class="offcanvas-body">
        <nav class="nav flex-column">
          <router-link class="nav-link" to="/inventario">
            <i class="fas fa-boxes me-2"></i>Inventario
          </router-link>

          <!-- Submenú Gestión (colapsable) -->
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
            <router-link class="nav-link" to="/gestionar_animales">
              <i class="fas fa-cow me-2"></i>Animales
            </router-link>
            <router-link class="nav-link" to="/gestionar_potreros">
              <i class="fas fa-map-marked-alt me-2"></i>Potreros
            </router-link>
            <router-link class="nav-link" to="/registro_vacunacion">
              <i class="fas fa-syringe me-2"></i>Vacunación
            </router-link>
          </div>

          <router-link class="nav-link" to="/escanear_qr">
            <i class="fas fa-qrcode me-2"></i>Escanear QR
          </router-link>
          <router-link class="nav-link" to="/login">
            <i class="fas fa-sign-out-alt me-2"></i>Salir
          </router-link>
        </nav>
      </div>
    </div>

    <!-- Sidebar fijo en desktop -->
    <div class="d-none d-md-block sidebar">
      <nav class="nav flex-column">
        <router-link class="nav-link" to="/inventario">
          <i class="fas fa-boxes me-2"></i>Inventario
        </router-link>

        <!-- Submenú Gestión (colapsable en desktop) -->
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
          <router-link class="nav-link" to="/gestionar_animales">
            <i class="fas fa-cow me-2"></i>Animales
          </router-link>
          <router-link class="nav-link" to="/gestionar_potreros">
            <i class="fas fa-map-marked-alt me-2"></i>Potreros
          </router-link>
          <router-link class="nav-link" to="/registro_vacunacion">
            <i class="fas fa-syringe me-2"></i>Vacunación
          </router-link>
        </div>

        <router-link class="nav-link" to="/escanear_qr">
          <i class="fas fa-qrcode me-2"></i>Escanear QR
        </router-link>
        <router-link class="nav-link" to="/login">
          <i class="fas fa-sign-out-alt me-2"></i>Salir
        </router-link>
      </nav>
    </div>

    <!-- Main Content -->
    <div class="main-content d-flex align-items-center justify-content-center">
      <div class="container-fluid py-4 py-md-5">
        <div class="row justify-content-center g-4">
          <div class="col-12">
            <!-- Título -->
            <div class="mb-4">
              <h2 class="fw-bold text-dark mb-2 mb-md-3">
                <i class="fas fa-cow me-2 text-success"></i>Gestionar Animales
              </h2>
            </div>

            <!-- Filtros -->
            <div class="card border-0 shadow-lg mb-4">
              <div class="card-body p-3 p-sm-4">
                <div class="row g-3">
                  <div class="col-md-4">
                    <label class="form-label">Buscar por nombre:</label>
                    <input type="text" class="form-control" v-model="busqueda" placeholder="Buscar por nombre...">
                  </div>
                  <div class="col-md-3">
                    <label class="form-label">Filtrar por raza:</label>
                    <select class="form-select" v-model="filtroRaza">
                      <option value="">Todas las razas</option>
                      <option>Holstein</option>
                      <option>Angus</option>
                      <option>Jersey</option>
                    </select>
                  </div>
                  <div class="col-md-3">
                    <label class="form-label">Estado de salud:</label>
                    <select class="form-select" v-model="filtroSalud">
                      <option value="">Todos los estados</option>
                      <option>Saludable</option>
                      <option>En tratamiento</option>
                      <option>Enfermo</option>
                    </select>
                  </div>
                  <div class="col-md-2 d-flex align-items-end">
                    <button class="btn btn-primary w-100" @click="filtrarAnimales">
                      <i class="fas fa-search me-1"></i>Buscar
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="text-center py-5">
              <div class="spinner-border text-success" role="status">
                <span class="visually-hidden">Cargando...</span>
              </div>
              <p class="mt-2 text-muted">Cargando animales...</p>
            </div>

            <!-- Error State -->
            <div v-else-if="error" class="alert alert-danger text-center">
              <i class="fas fa-exclamation-triangle me-2"></i>
              {{ error }}
              <button class="btn btn-sm btn-outline-danger ms-3" @click="cargarAnimales">
                <i class="fas fa-redo me-1"></i>Reintentar
              </button>
            </div>

            <!-- Empty State -->
            <div v-else-if="animales.length === 0" class="text-center py-5">
              <i class="fas fa-cow fa-4x text-muted mb-3"></i>
              <h4 class="text-muted">No hay animales registrados</h4>
              <p class="text-muted">Aún no se han creado animales en el sistema.</p>
              <button class="btn btn-success" @click="agregarNuevoAnimal()">
                <i class="fas fa-plus me-1"></i>Crear Primer Animal
              </button>
            </div>

            <!-- Grid de Animales -->
            <div v-else class="row g-4" id="gridAnimales">
              <div class="col-12 col-sm-6 col-lg-4" v-for="animal in animalesFiltrados" :key="animal.id">
                <div class="card border-0 shadow-sm h-100">
                  <div class="card-body text-center">
                    <i class="fas fa-cow fa-3x mb-3" :class="iconClass(animal)"></i>
                    <h5 class="card-title">{{ animal.nombre }}</h5>
                    <p class="text-muted">Raza: {{ animal.raza }}</p>
                    <p class="text-muted">Edad: {{ animal.edad }} años</p>
                    <span class="badge mb-3" :class="estadoClass(animal.estado)">{{ animal.estado }}</span>
                    <div class="d-grid gap-2">
                      <button class="btn btn-outline-primary" @click="verPerfilAnimal(animal.id)">
                        <i class="fas fa-eye me-1"></i>Ver Perfil
                      </button>
                      <button class="btn btn-outline-warning" @click="editarAnimal(animal.id)">
                        <i class="fas fa-edit me-1"></i>Editar
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Botón Agregar -->
            <div v-if="animales.length > 0" class="text-center mt-4 mt-md-5">
              <button class="btn btn-success btn-lg" @click="agregarNuevoAnimal">
                <i class="fas fa-plus me-2"></i>Agregar Nuevo Animal
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

</template>

<script setup>
import { onMounted, ref, computed } from 'vue';
import {
  currentIndex,
  accordionOpen,
  animales,
  estadosGanado,
  personasUsuario,
  loading,
  error,
  cargarDatosIniciales,
  estadoClass,
  iconClass,
  verPerfilAnimal,
  editarAnimal,
  agregarNuevoAnimal,
  prevAnimal,
  nextAnimal,
  toggleAccordion
} from '../assets/js/gestionar_animales.js';

// Variables locales para filtros
const busqueda = ref("");
const filtroRaza = ref("");
const filtroSalud = ref("");

// Computed para animales filtrados
const animalesFiltrados = computed(() => {
  return animales.value.filter(a => {
    const matchesNombre = !busqueda.value || a.nombre.toLowerCase().includes(busqueda.value.toLowerCase());
    const matchesRaza = !filtroRaza.value || a.raza === filtroRaza.value;
    const matchesSalud = !filtroSalud.value || a.estado === filtroSalud.value;
    return matchesNombre && matchesRaza && matchesSalud;
  });
});

// Función para mostrar notificaciones
const mostrarNotificaciones = () => {
  const SwalLib = (typeof Swal !== 'undefined') ? Swal : (window.Swal || null);
  if (SwalLib && SwalLib.fire) {
    SwalLib.fire({
      title: '<i class="fas fa-bell"></i> Notificaciones',
      html: `
        <div class="text-start">
          <div class="alert alert-info"><i class="fas fa-info-circle me-2"></i><strong>Recordatorio:</strong> Vacunación programada para mañana</div>
          <div class="alert alert-warning"><i class="fas fa-exclamation-triangle me-2"></i><strong>Alerta:</strong> Animal #125 requiere atención médica</div>
        </div>
      `,
      confirmButtonColor: '#00d563'
    });
  } else {
    alert('Notificaciones');
  }
};

// Lifecycle
onMounted(() => {
  cargarDatosIniciales();
});
</script>

<style scoped>
.sidebar {
  min-width: 250px;
  max-width: 250px;
  position: fixed;
  top: 80px;
  left: 0;
  height: calc(100vh - 80px);
  background-color: #6c757d;
  z-index: 1020;
  padding: 1rem;
  overflow-y: auto;
}
@media (max-width: 767px) {
  .sidebar {
    display: none !important;
  }
}
.main-content {
  margin-left: 250px;
  margin-top: 0;
}
@media (max-width: 767px) {
  .main-content {
    margin-left: 0 !important;
  }
}
</style>
