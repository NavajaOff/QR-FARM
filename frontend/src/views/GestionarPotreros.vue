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
                    <div class="col-6"><strong>Tipo de pasto:</strong> {{ potreros[currentIndex].pasto || 'No definido' }}</div>
                  </div>
                  <div class="row g-3 mb-3">
                    <div class="col-6"><strong>Fecha de último uso:</strong> {{ potreros[currentIndex].fechaUso || 'No registrada' }}</div>
                    <div class="col-6"><strong>Responsable:</strong> {{ potreros[currentIndex].responsable }}</div>
                  </div>
                  <div class="row g-3 mb-3">
                    <div class="col-12"><strong>Próxima limpieza:</strong> <input type="date" class="form-control d-inline-block w-auto" style="min-width:150px;"></div>
                  </div>
                  <div class="row g-3 mb-3">
                    <div class="col-6"><strong>Área:</strong> {{ potreros[currentIndex].area || 'No definida' }} ha</div>
                    <div class="col-6"><strong>Última limpieza:</strong> {{ potreros[currentIndex].ultimaLimpieza || 'No registrada' }}</div>
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

<script>
import Swal from 'sweetalert2';
export default {
  name: "GestionarPotreros",
  data() {
    return {
      currentIndex: 0,
      accordionOpen: true,
      potreros: [],
      loading: true,
      error: null
    };
  },
  async mounted() {
    await this.cargarPotreros();
  },
  methods: {
    async cargarPotreros() {
      try {
        this.loading = true;
        this.error = null;
        const response = await fetch('/api/potreros/');
        if (!response.ok) {
          throw new Error('Error al cargar potreros');
        }
        const data = await response.json();
        if (data.success) {
          this.potreros = data.data.map(potrero => ({
            id: potrero.id,
            nombre: potrero.nombre,
            estado: this.mapEstado(potrero.estado),
            capacidad: potrero.capacidad,
            ocupacion: potrero.ocupacion,
            pasto: potrero.tipo_pasto,
            area: potrero.area,
            fechaUso: potrero.fecha_ultimo_uso ? this.formatDate(potrero.fecha_ultimo_uso) : '',
            ultimaLimpieza: potrero.ultima_limpieza ? this.formatDate(potrero.ultima_limpieza) : '',
            responsable: potrero.responsable_persona_id ? `Persona ${potrero.responsable_persona_id}` : 'No asignado'
          }));
        } else {
          throw new Error(data.message || 'Error desconocido');
        }
      } catch (error) {
        this.error = error.message;
        console.error('Error cargando potreros:', error);
      } finally {
        this.loading = false;
      }
    },
    mapEstado(estado) {
      const estados = {
        'disponible': 'Disponible',
        'en_uso': 'En uso',
        'mantenimiento': 'Mantenimiento',
        'inactivo': 'Inactivo'
      };
      return estados[estado] || estado;
    },
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString('es-ES', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      });
    },
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
            <div class="mb-3"><label class="form-label">Nombre:</label><input type="text" id="nombre" class="form-control" placeholder="Ej: Potrero 4" required></div>
            <div class="mb-3">
              <label class="form-label">Estado:</label>
              <select id="estado" class="form-control">
                <option value="disponible">Disponible</option>
                <option value="en_uso">En uso</option>
                <option value="mantenimiento">Mantenimiento</option>
                <option value="inactivo">Inactivo</option>
              </select>
            </div>
            <div class="mb-3"><label class="form-label">Capacidad:</label><input type="number" id="capacidad" class="form-control" placeholder="Ej: 25" min="0"></div>
            <div class="mb-3"><label class="form-label">Ocupación:</label><input type="number" id="ocupacion" class="form-control" placeholder="Ej: 0" min="0" value="0"></div>
            <div class="mb-3"><label class="form-label">Tipo de pasto:</label><input type="text" id="tipo_pasto" class="form-control" placeholder="Ej: Kikuyo"></div>
            <div class="mb-3"><label class="form-label">Fecha de último uso:</label><input type="date" id="fecha_ultimo_uso" class="form-control"></div>
            <div class="mb-3"><label class="form-label">Responsable:</label><input type="text" id="responsable" class="form-control" placeholder="Ej: Juan Pérez"></div>
            <div class="mb-3"><label class="form-label">Próxima limpieza:</label><input type="date" id="proxima_limpieza" class="form-control"></div>
            <div class="mb-3"><label class="form-label">Área:</label><input type="number" id="area" class="form-control" placeholder="Ej: 2.5" step="0.01" min="0"></div>
            <div class="mb-3"><label class="form-label">Última limpieza:</label><input type="date" id="ultima_limpieza" class="form-control"></div>
          </form>
        `,
        showCancelButton: true,
        confirmButtonText: 'Agregar',
        confirmButtonColor: '#00d563',
        preConfirm: () => {
          const nombre = document.getElementById('nombre').value;
          const estado = document.getElementById('estado').value;
          const capacidad = document.getElementById('capacidad').value;
          const ocupacion = document.getElementById('ocupacion').value;
          const tipo_pasto = document.getElementById('tipo_pasto').value;
          const fecha_ultimo_uso = document.getElementById('fecha_ultimo_uso').value;
          const responsable = document.getElementById('responsable').value;
          const proxima_limpieza = document.getElementById('proxima_limpieza').value;
          const area = document.getElementById('area').value;
          const ultima_limpieza = document.getElementById('ultima_limpieza').value;

          if (!nombre) {
            Swal.showValidationMessage('El nombre es requerido');
            return false;
          }

          return {
            nombre,
            estado,
            capacidad: capacidad ? parseInt(capacidad) : null,
            ocupacion: ocupacion ? parseInt(ocupacion) : 0,
            tipo_pasto,
            fecha_ultimo_uso,
            responsable,
            proxima_limpieza,
            area: area ? parseFloat(area) : null,
            ultima_limpieza
          };
        }
      }).then((result) => {
        if (result.isConfirmed) {
          // Aquí se enviaría al backend
          console.log('Datos del nuevo potrero:', result.value);
          // Agregar lógica para enviar al backend
        }
      });
    },
    editarPotrero(id) {
      const potrero = this.potreros.find(p => p.id === id);
      if (!potrero) return;

      Swal.fire({
        title: `<i class="fas fa-edit"></i> Editar Potrero: ${potrero.nombre}`,
        html: `
          <form class="text-start">
            <div class="mb-3"><label class="form-label">Nombre:</label><input type="text" id="edit_nombre" class="form-control" value="${potrero.nombre}" required></div>
            <div class="mb-3">
              <label class="form-label">Estado:</label>
              <select id="edit_estado" class="form-control">
                <option value="disponible" ${potrero.estado === 'Disponible' ? 'selected' : ''}>Disponible</option>
                <option value="en_uso" ${potrero.estado === 'En uso' ? 'selected' : ''}>En uso</option>
                <option value="mantenimiento" ${potrero.estado === 'Mantenimiento' ? 'selected' : ''}>Mantenimiento</option>
                <option value="inactivo" ${potrero.estado === 'Inactivo' ? 'selected' : ''}>Inactivo</option>
              </select>
            </div>
            <div class="mb-3"><label class="form-label">Capacidad:</label><input type="number" id="edit_capacidad" class="form-control" value="${potrero.capacidad}" min="0"></div>
            <div class="mb-3"><label class="form-label">Ocupación:</label><input type="number" id="edit_ocupacion" class="form-control" value="${potrero.ocupacion}" min="0"></div>
            <div class="mb-3"><label class="form-label">Tipo de pasto:</label><input type="text" id="edit_tipo_pasto" class="form-control" value="${potrero.pasto}"></div>
            <div class="mb-3"><label class="form-label">Fecha de último uso:</label><input type="date" id="edit_fecha_ultimo_uso" class="form-control" value="${potrero.fechaUso ? potrero.fechaUso.split('/').reverse().join('-') : ''}"></div>
            <div class="mb-3"><label class="form-label">Responsable:</label><input type="text" id="edit_responsable" class="form-control" value="${potrero.responsable}"></div>
            <div class="mb-3"><label class="form-label">Próxima limpieza:</label><input type="date" id="edit_proxima_limpieza" class="form-control"></div>
            <div class="mb-3"><label class="form-label">Área:</label><input type="number" id="edit_area" class="form-control" value="${potrero.area}" step="0.01" min="0"></div>
            <div class="mb-3"><label class="form-label">Última limpieza:</label><input type="date" id="edit_ultima_limpieza" class="form-control" value="${potrero.ultimaLimpieza ? potrero.ultimaLimpieza.split('/').reverse().join('-') : ''}"></div>
          </form>
        `,
        showCancelButton: true,
        confirmButtonText: 'Actualizar',
        confirmButtonColor: '#00d563',
        preConfirm: () => {
          const nombre = document.getElementById('edit_nombre').value;
          const estado = document.getElementById('edit_estado').value;
          const capacidad = document.getElementById('edit_capacidad').value;
          const ocupacion = document.getElementById('edit_ocupacion').value;
          const tipo_pasto = document.getElementById('edit_tipo_pasto').value;
          const fecha_ultimo_uso = document.getElementById('edit_fecha_ultimo_uso').value;
          const responsable = document.getElementById('edit_responsable').value;
          const proxima_limpieza = document.getElementById('edit_proxima_limpieza').value;
          const area = document.getElementById('edit_area').value;
          const ultima_limpieza = document.getElementById('edit_ultima_limpieza').value;

          if (!nombre) {
            Swal.showValidationMessage('El nombre es requerido');
            return false;
          }

          return {
            id,
            nombre,
            estado,
            capacidad: capacidad ? parseInt(capacidad) : null,
            ocupacion: ocupacion ? parseInt(ocupacion) : 0,
            tipo_pasto,
            fecha_ultimo_uso,
            responsable,
            proxima_limpieza,
            area: area ? parseFloat(area) : null,
            ultima_limpieza
          };
        }
      }).then((result) => {
        if (result.isConfirmed) {
          // Aquí se enviaría al backend
          console.log('Datos actualizados del potrero:', result.value);
          // Agregar lógica para enviar al backend
        }
      });
    },
    prevPotrero() {
      if (this.potreros.length > 1) {
        this.currentIndex = (this.currentIndex - 1 + this.potreros.length) % this.potreros.length;
        this.accordionOpen = true;
      }
    },
    nextPotrero() {
      if (this.potreros.length > 1) {
        this.currentIndex = (this.currentIndex + 1) % this.potreros.length;
        this.accordionOpen = true;
      }
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
