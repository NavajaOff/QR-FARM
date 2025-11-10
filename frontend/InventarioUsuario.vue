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
          <router-link class="nav-link" to="/inventario">
            <i class="fas fa-boxes me-2"></i>Inventario
          </router-link>

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
        <router-link class="nav-link active" to="/inventario">
          <i class="fas fa-boxes me-2"></i>Inventario
        </router-link>

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
    <div class="main-content">
      <div class="container-fluid py-4 py-md-5">
        <div class="row justify-content-center g-4">
          <div class="col-12">
            <!-- Título -->
            <div class="mb-4">
              <h2 class="fw-bold text-dark">
                <i class="fas fa-boxes me-2 text-primary"></i>Inventario General
              </h2>
            </div>

            <!-- Resumen -->
            <div class="card border-0 shadow-lg mb-4">
              <div class="card-body p-3 p-sm-4 p-lg-5">
                <div class="row g-4 align-items-center">
                  <div class="col-12 col-lg-8">
                    <div style="max-width: 500px; margin: 0 auto;">
                      <canvas id="inventarioPie"></canvas>
                    </div>
                  </div>
                  <div class="col-12 col-lg-4">
                    <div class="d-flex align-items-center mb-3">
                      <i class="fas fa-cow fa-2x text-primary me-2"></i>
                      <span class="fw-bold">Animales: {{ totalAnimales }}</span>
                    </div>
                    <div class="d-flex align-items-center mb-3">
                      <i class="fas fa-check-circle fa-2x text-success me-2"></i>
                      <span class="fw-bold">Saludables: {{ countSaludable }}</span>
                    </div>
                    <div class="d-flex align-items-center mb-3">
                      <i class="fas fa-exclamation-triangle fa-2x text-warning me-2"></i>
                      <span class="fw-bold">En Tratamiento: {{ countTratamiento }}</span>
                    </div>
                    <div class="d-flex align-items-center mb-3">
                      <i class="fas fa-baby fa-2x text-info me-2"></i>
                      <span class="fw-bold">Recién Nacidos: {{ countRecienNacidos }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Tabla -->
            <div class="card border-0 shadow-lg">
              <div class="card-header bg-light p-3">
                <div class="row align-items-center">
                  <div class="col">
                    <h5 class="mb-0">Lista de Animales</h5>
                  </div>
                </div>
              </div>
              <div class="card-body p-3 p-sm-4">
                <div class="table-responsive">
                  <table class="table table-hover">
                    <caption class="visually-hidden">Lista de animales en el inventario, mostrando ID, nombre/código, raza, edad, estado, ubicación y acciones disponibles</caption>
                    <thead class="table-light">
                      <tr>
                        <th>ID</th>
                        <th>Nombre/Código</th>
                        <th>Raza</th>
                        <th>Edad</th>
                        <th>Estado</th>
                        <th>Ubicación</th>
                        <th>Acciones</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="a in animales" :key="a.id">
                        <td>{{ a.id }}</td>
                        <td>{{ a.nombre }}</td>
                        <td>{{ a.raza }}</td>
                        <td>{{ a.edad }} años</td>
                        <td><span :class="['badge', estadoClass(a.estado)]">{{ a.estado }}</span></td>
                        <td>{{ a.potrero }}</td>
                        <td>
                          <button class="btn btn-sm btn-outline-primary me-1" @click="verPerfilAnimal(a.id)">
                            <i class="fas fa-eye"></i>
                          </button>
                          <button class="btn btn-sm btn-outline-warning" @click="editarAnimal(a.id)">
                            <i class="fas fa-edit"></i>
                          </button>
                        </td>
                      </tr>
                      <tr v-if="animales.length === 0">
                        <td colspan="7" class="text-center">No hay animales registrados.</td>
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
import { Chart, registerables } from 'chart.js';
Chart.register(...registerables);

export default {
  name: "Inventario",
  data() {
    return {
      animales: [
        { id: "001", nombre: "Holstein-001", raza: "Holstein", edad: 3, estado: "Saludable", potrero: "Potrero 1" },
        { id: "002", nombre: "Angus-002", raza: "Angus", edad: 2, estado: "En Tratamiento", potrero: "Potrero 2" },
        { id: "003", nombre: "Jersey-003", raza: "Jersey", edad: 4, estado: "Saludable", potrero: "Potrero 1" }
      ]
    };
  },
  computed: {
    totalAnimales() {
      return this.animales.length;
    },
    countSaludable() {
      return this.animales.filter(a => a.estado === 'Saludable').length;
    },
    countTratamiento() {
      return this.animales.filter(a => a.estado === 'En Tratamiento').length;
    },
    countRecienNacidos() {
      return this.animales.filter(a => a.recién === true).length || 0;
    }
  },
  mounted() {
    if (window.Chart) {
      const ctx = document.getElementById('inventarioPie').getContext('2d');
      const data = {
        labels: ['Saludables', 'En Tratamiento', 'Otros'],
        datasets: [{
          data: [
            this.countSaludable,
            this.countTratamiento,
            Math.max(0, this.totalAnimales - this.countSaludable - this.countTratamiento)
          ],
          backgroundColor: ['#28a745', '#ffc107', '#6c757d']
        }]
      };
      new window.Chart(ctx, {
        type: 'doughnut',
        data,
        options: { responsive: true, maintainAspectRatio: false }
      });
    }
  },
  methods: {
    verPerfilAnimal(id) {
      const a = this.animales.find(x => x.id === id);
      const html = `
        <div class="text-start">
          <p><strong>ID:</strong> ${a?.id || ''}</p>
          <p><strong>Nombre:</strong> ${a?.nombre || ''}</p>
          <p><strong>Raza:</strong> ${a?.raza || ''}</p>
          <p><strong>Edad:</strong> ${a?.edad || ''} años</p>
          <p><strong>Estado:</strong> ${a?.estado || ''}</p>
          <p><strong>Potrero:</strong> ${a?.potrero || ''}</p>
        </div>
      `;
      if (window.Swal) Swal.fire({ title: `Perfil ${id}`, html, confirmButtonColor: '#00d563' });
      else alert(`Perfil ${id}\n\n` + JSON.stringify(a, null, 2));
    },
    editarAnimal(id) {
      if (window.Swal) Swal.fire('Editar', `Aquí editarías al animal ${id}`, 'info');
      else alert('Editar ' + id);
    },
    estadoClass(estado) {
      if (estado === 'Saludable') return 'bg-success';
      if (estado === 'En Tratamiento') return 'bg-warning';
      if (estado === 'Enfermo') return 'bg-danger';
      return 'bg-secondary';
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
@media (max-width: 767px) {
  .sidebar { display: none !important; }
}
.main-content { margin-left: 250px; margin-top: 0; }
@media (max-width: 767px) { .main-content { margin-left: 0 !important; } }
#inventarioPie { max-height: 320px; width: 100% !important; }
</style>
