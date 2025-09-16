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

            <!-- Card Potrero -->
            <div class="d-flex justify-content-center align-items-start gap-2">
              <button class="btn btn-outline-secondary" @click="prevPotrero"><i class="fas fa-chevron-left"></i></button>
              
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
                    <div class="col-6"><strong>Capacidad:</strong> {{ potreros[currentIndex].capacidad }} Animales</div>
                  </div>
                  <div class="row g-3 mb-3">
                    <div class="col-6"><strong>Ocupación:</strong> {{ potreros[currentIndex].ocupacion }} Animales</div>
                    <div class="col-6"><strong>Tipo de pasto:</strong> {{ potreros[currentIndex].pasto }}</div>
                  </div>
                  <div class="row g-3 mb-3">
                    <div class="col-6"><strong>Fecha de último uso:</strong> {{ potreros[currentIndex].fechaUso }}</div>
                    <div class="col-6"><strong>Responsable:</strong> {{ potreros[currentIndex].responsable }}</div>
                  </div>
                  <div class="row g-3 mb-3">
                    <div class="col-12"><strong>Próxima limpieza:</strong> <input type="date" class="form-control d-inline-block w-auto" style="min-width:150px;"></div>
                  </div>
                  <div class="row g-3 mb-3">
                    <div class="col-6"><strong>Área:</strong> {{ potreros[currentIndex].area }} ha</div>
                    <div class="col-6"><strong>Última limpieza:</strong> {{ potreros[currentIndex].ultimaLimpieza }}</div>
                  </div>
                  <div class="d-flex gap-2 justify-content-center">
                    <button class="btn btn-primary" @click="editarPotrero(potreros[currentIndex].id)"><i class="fas fa-edit me-1"></i>Editar</button>
                    <button class="btn btn-success" @click="crearPotrero()"><i class="fas fa-plus me-1"></i>Crear Potrero</button>
                  </div>
                </div>
              </div>

              <button class="btn btn-outline-secondary" @click="nextPotrero"><i class="fas fa-chevron-right"></i></button>
            </div>

          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Swal from 'sweetalert2';
export default {
  name: "GestionarPotreros",
  data() {
    return {
      currentIndex: 0,
      accordionOpen: true,
      potreros: [
        { id: 1, nombre: 'Potrero 1', estado: 'Disponible', capacidad: 25, ocupacion: 18, pasto: 'Kikuyo', area: 2.5, fechaUso: '10/04/2025', ultimaLimpieza: '10/04/2025', responsable: 'Juan Pérez' },
        { id: 2, nombre: 'Potrero 2', estado: 'En uso', capacidad: 30, ocupacion: 28, pasto: 'Braquiaria', area: 3, fechaUso: '08/04/2025', ultimaLimpieza: '08/04/2025', responsable: 'María Gómez' },
        { id: 3, nombre: 'Potrero 3', estado: 'Mantenimiento', capacidad: 20, ocupacion: 0, pasto: 'Pastura Mixta', area: 1.8, fechaUso: '05/04/2025', ultimaLimpieza: '05/04/2025', responsable: 'Carlos Ruiz' }
      ]
    };
  },
  methods: {
    estadoClass(estado) {
      if (estado === 'Disponible') return 'bg-success';
      if (estado === 'En uso') return 'bg-warning';
      if (estado === 'Mantenimiento') return 'bg-danger';
      return 'bg-secondary';
    },
    crearPotrero() {
      Swal.fire({
        title: '<i class="fas fa-plus"></i> Crear Nuevo Potrero',
        html: `
          <form class="text-start">
            <div class="mb-3"><label class="form-label">Nombre:</label><input type="text" class="form-control" placeholder="Ej: Potrero 4"></div>
            <div class="mb-3"><label class="form-label">Capacidad:</label><input type="number" class="form-control" placeholder="Ej: 25"></div>
            <div class="mb-3"><label class="form-label">Tipo de pasto:</label><input type="text" class="form-control" placeholder="Ej: Kikuyo"></div>
          </form>
        `,
        showCancelButton: true,
        confirmButtonText: 'Agregar',
        confirmButtonColor: '#00d563'
      });
    },
    editarPotrero(id) {
      Swal.fire({ title: `<i class="fas fa-edit"></i> Editar Potrero ${id}`, html: '<p>Aquí se podría editar el potrero seleccionado</p>', icon: 'info', confirmButtonColor: '#00d563' });
    },
    prevPotrero() {
      this.currentIndex = (this.currentIndex - 1 + this.potreros.length) % this.potreros.length;
      this.accordionOpen = true;
    },
    nextPotrero() {
      this.currentIndex = (this.currentIndex + 1) % this.potreros.length;
      this.accordionOpen = true;
    },
    toggleAccordion() {
      this.accordionOpen = !this.accordionOpen;
    }
  }
};
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
@media (max-width: 767px) { .sidebar { display: none !important; } }
.main-content { margin-left: 250px; margin-top: 0; }
@media (max-width: 767px) { .main-content { margin-left: 0 !important; } }
</style>
