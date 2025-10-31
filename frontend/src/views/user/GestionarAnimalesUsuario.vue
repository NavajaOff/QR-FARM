<template>
  <div class="container-fluid py-4">
    <div class="row">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h2 class="mb-0">
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
                      <div v-if="animal.codigo_qr" class="mt-2">
                          <img :src="'http://localhost:5000/api/animales/qr/' + animal.codigo_qr + '.png'" alt="Código QR" class="img-fluid rounded" style="max-width: 200px; max-height: 200px;">
                        </div>
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
</template>

<script>
import authService from '../../services/authService.js';

export default {
  name: 'GestionarAnimalesUsuario',
  data() {
    return {
      userName: 'Usuario',
      busqueda: '',
      filtroRaza: '',
      filtroSalud: '',
      loading: false,
      error: null,
      animales: [
        { id: 1, nombre: 'Rosita', raza: 'Brahman', edad: 2, estado: 'Saludable', potrero: 'Potrero 1', codigo_qr: 'QR_1_rosita' },
        { id: 2, nombre: 'Luna', raza: 'Brahman', edad: 1, estado: 'En tratamiento', potrero: 'Potrero 2', codigo_qr: 'QR_2_rosita' },
        { id: 3, nombre: 'Bella', raza: 'Holstein', edad: 3, estado: 'Saludable', potrero: 'Potrero 1', codigo_qr: 'QR_3_rosita' },
        { id: 4, nombre: 'Max', raza: 'Angus', edad: 4, estado: 'Saludable', potrero: 'Potrero 2', codigo_qr: 'QR_4_rosita' }
      ]
    };
  },
  mounted() {
    if (!authService.isAuthenticated() || !authService.isUser()) {
      this.$router.push('/login');
      return;
    }

    const user = authService.getUser();
    this.userName = user?.persona?.primer_nombre || 'Usuario';
  },
  computed: {
    animalesFiltrados() {
      return this.animales.filter(a => {
        const matchesNombre = !this.busqueda || a.nombre.toLowerCase().includes(this.busqueda.toLowerCase());
        const matchesRaza = !this.filtroRaza || a.raza === this.filtroRaza;
        const matchesSalud = !this.filtroSalud || a.estado === this.filtroSalud;
        return matchesNombre && matchesRaza && matchesSalud;
      });
    }
  },
  methods: {
    filtrarAnimales() {
      // Los filtros se aplican automáticamente en el computed
    },

    verPerfilAnimal(id) {
      const animal = this.animales.find(a => a.id === id);
      if (animal) {
        const html = `
          <div class="text-start">
            <p><strong>ID:</strong> ${animal.id}</p>
            <p><strong>Nombre:</strong> ${animal.nombre}</p>
            <p><strong>Raza:</strong> ${animal.raza}</p>
            <p><strong>Edad:</strong> ${animal.edad} años</p>
            <p><strong>Estado:</strong> ${animal.estado}</p>
            <p><strong>Potrero:</strong> ${animal.potrero}</p>
          </div>
        `;
        if (window.Swal) {
          window.Swal.fire({
            title: `Perfil de ${animal.nombre}`,
            html,
            confirmButtonColor: '#28a745'
          });
        } else {
          alert(`Perfil de ${animal.nombre}\n\nID: ${animal.id}\nNombre: ${animal.nombre}\nRaza: ${animal.raza}\nEdad: ${animal.edad} años\nEstado: ${animal.estado}\nPotrero: ${animal.potrero}`);
        }
      }
    },

    editarAnimal(id) {
      if (window.Swal) {
        window.Swal.fire('Editar Animal', `Funcionalidad para editar animal ${id} próximamente`, 'info');
      } else {
        alert(`Editar animal ${id}`);
      }
    },

    agregarNuevoAnimal() {
      if (window.Swal) {
        window.Swal.fire('Agregar Animal', 'Funcionalidad para agregar nuevo animal próximamente', 'info');
      } else {
        alert('Agregar nuevo animal');
      }
    },

    estadoClass(estado) {
      if (estado === 'Saludable') return 'bg-success';
      if (estado === 'En tratamiento') return 'bg-warning';
      if (estado === 'Enfermo') return 'bg-danger';
      return 'bg-secondary';
    },

    iconClass(animal) {
      if (animal.estado === 'Saludable') return 'text-success';
      if (animal.estado === 'En tratamiento') return 'text-warning';
      if (animal.estado === 'Enfermo') return 'text-danger';
      return 'text-secondary';
    }
  }
};
</script>

<style scoped>
.card {
  border: none;
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow);
  background: white;
}

.card-header {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-bottom: 1px solid #dee2e6;
  font-weight: 600;
  color: #495057;
}

.form-label {
  font-weight: 600;
  color: #495057;
  margin-bottom: 0.5rem;
}

.form-control, .form-select {
  border: 2px solid #e9ecef;
  border-radius: var(--border-radius);
  padding: 0.75rem;
  transition: var(--transition);
}

.form-control:focus, .form-select:focus {
  border-color: #28a745;
  box-shadow: 0 0 0 0.2rem rgba(40, 167, 69, 0.25);
}

.btn-primary {
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
  border: none;
  font-weight: 600;
}

.btn-success {
  background: linear-gradient(135deg, #28a745 0%, #1e7e34 100%);
  border: none;
  font-weight: 600;
}

.btn-outline-primary {
  border-color: #007bff;
  color: #007bff;
  transition: var(--transition);
}

.btn-outline-primary:hover {
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
  border-color: #007bff;
  color: white;
}

.btn-outline-warning {
  border-color: #ffc107;
  color: #ffc107;
  transition: var(--transition);
}

.btn-outline-warning:hover {
  background: linear-gradient(135deg, #ffc107 0%, #e0a800 100%);
  border-color: #ffc107;
  color: white;
}

.spinner-border {
  width: 3rem;
  height: 3rem;
}

.alert {
  border: none;
  border-radius: var(--border-radius);
  font-weight: 500;
}

.badge {
  font-size: 0.75rem;
  padding: 0.5rem 1rem;
  border-radius: var(--border-radius-sm);
  font-weight: 600;
}

.table {
  margin-bottom: 0;
}

.table thead th {
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
  color: white;
  font-weight: 600;
  border: none;
  padding: 1rem 0.75rem;
}

.table tbody tr {
  transition: var(--transition);
}

.table tbody tr:hover {
  background-color: #f8f9fa;
  transform: scale(1.01);
}

.table td {
  padding: 1rem 0.75rem;
  vertical-align: middle;
  border: none;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
}

@media (max-width: 768px) {
  .container-fluid {
    padding: 1rem;
  }

  .row.g-3 {
    --bs-gutter-x: 1rem;
    --bs-gutter-y: 1rem;
  }

  .col-md-4, .col-md-3, .col-md-2 {
    margin-bottom: 1rem;
  }

  .btn {
    padding: 0.5rem 1rem;
    font-size: 0.875rem;
  }

  .card-body {
    padding: 1rem;
  }

  .table-responsive {
    border-radius: var(--border-radius);
    overflow: hidden;
  }

  .table td, .table th {
    padding: 0.5rem;
    font-size: 0.875rem;
  }
}
</style>
