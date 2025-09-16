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
            <i class="fas fa-syringe fa-2x"></i>
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
            <router-link class="nav-link" to="/gestionar_potreros"><i class="fas fa-map-marked-alt me-2"></i>Potreros</router-link>
            <router-link class="nav-link active" to="/registro_vacunacion"><i class="fas fa-syringe me-2"></i>Vacunación</router-link>
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
          <router-link class="nav-link" to="/gestionar_potreros"><i class="fas fa-map-marked-alt me-2"></i>Potreros</router-link>
          <router-link class="nav-link active" to="/registro_vacunacion"><i class="fas fa-syringe me-2"></i>Vacunación</router-link>
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
            <div class="d-flex justify-content-between align-items-center mb-4">
              <h2 class="fw-bold text-dark mb-0">
                <i class="fas fa-syringe me-2 text-success"></i>Registro de Vacunación
              </h2>
              <div class="d-flex gap-2">
                <button class="btn btn-success" @click="registrarVacunacion">
                  <i class="fas fa-plus me-2"></i>Nueva Vacunación
                </button>
                <button class="btn btn-primary" @click="generarReporte">
                  <i class="fas fa-file-pdf me-2"></i>Generar Reporte
                </button>
              </div>
            </div>

            <!-- Filtros -->
            <div class="card border-0 shadow-lg mb-4">
              <div class="card-body p-3 p-sm-4">
                <div class="row g-3">
                  <div class="col-md-3">
                    <label class="form-label">Buscar animal:</label>
                    <input type="text" class="form-control" v-model="filtros.animal" placeholder="ID o Nombre">
                  </div>
                  <div class="col-md-3">
                    <label class="form-label">Tipo de vacuna:</label>
                    <select class="form-select" v-model="filtros.vacuna">
                      <option value="">Todas</option>
                      <option>Brucelosis</option>
                      <option>Fiebre Aftosa</option>
                      <option>Tuberculosis</option>
                    </select>
                  </div>
                  <div class="col-md-3">
                    <label class="form-label">Fecha desde:</label>
                    <input type="date" class="form-control" v-model="filtros.fechaDesde">
                  </div>
                  <div class="col-md-3">
                    <label class="form-label">Fecha hasta:</label>
                    <input type="date" class="form-control" v-model="filtros.fechaHasta">
                  </div>
                </div>
              </div>
            </div>

            <!-- Tabla de Registros -->
            <div class="card border-0 shadow-lg">
              <div class="card-body p-0">
                <div class="table-responsive">
                  <table class="table table-hover mb-0">
                    <thead class="bg-light">
                      <tr>
                        <th>ID Animal</th>
                        <th>Nombre/Código</th>
                        <th>Tipo de Vacuna</th>
                        <th>Fecha Aplicación</th>
                        <th>Próxima Dosis</th>
                        <th>Responsable</th>
                        <th>Estado</th>
                        <th>Acciones</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="v in vacunaciones" :key="v.id">
                        <td>{{ v.idAnimal }}</td>
                        <td>{{ v.nombre }}</td>
                        <td>{{ v.tipoVacuna }}</td>
                        <td>{{ v.fechaAplicacion }}</td>
                        <td>{{ v.proximaDosis }}</td>
                        <td>{{ v.responsable }}</td>
                        <td><span :class="['badge', estadoClass(v.estado)]">{{ v.estado }}</span></td>
                        <td>
                          <button class="btn btn-sm btn-outline-primary me-1" @click="verVacunacion(v.id)"><i class="fas fa-eye"></i></button>
                          <button class="btn btn-sm btn-outline-warning" @click="editarVacunacion(v.id)"><i class="fas fa-edit"></i></button>
                        </td>
                      </tr>
                      <tr v-if="vacunaciones.length === 0">
                        <td colspan="8" class="text-center">No hay registros de vacunación.</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
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
  name: "RegistroVacunacion",
  data() {
    return {
      filtros: { animal: '', vacuna: '', fechaDesde: '', fechaHasta: '' },
      vacunaciones: [
        { id: 1, idAnimal: '001', nombre: 'Holstein-001', tipoVacuna: 'Brucelosis', fechaAplicacion: '2025-08-01', proximaDosis: '2025-10-01', responsable: 'Juan Pérez', estado: 'Aplicada' },
        { id: 2, idAnimal: '002', nombre: 'Angus-002', tipoVacuna: 'Fiebre Aftosa', fechaAplicacion: '2025-08-05', proximaDosis: '2025-09-05', responsable: 'María Gómez', estado: 'Pendiente' }
      ]
    };
  },
  methods: {
    estadoClass(estado) {
      if (estado === 'Aplicada') return 'bg-success';
      if (estado === 'Pendiente') return 'bg-warning';
      return 'bg-secondary';
    },
    registrarVacunacion() {
      Swal.fire('Registrar Vacunación', 'Aquí iría el formulario de registro', 'info');
    },
    generarReporte() {
      Swal.fire('Reporte PDF', 'Aquí se generaría el reporte de vacunación', 'success');
    },
    verVacunacion(id) {
      const v = this.vacunaciones.find(x => x.id === id);
      Swal.fire({
        title: `Vacunación ${id}`,
        html: `<pre>${JSON.stringify(v, null, 2)}</pre>`,
        confirmButtonColor: '#00d563'
      });
    },
    editarVacunacion(id) {
      Swal.fire('Editar Vacunación', `Editar vacunación con ID ${id}`, 'info');
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
