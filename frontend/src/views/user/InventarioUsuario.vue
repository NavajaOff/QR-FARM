<template>
  <div class="container-fluid py-4">
    <div class="row">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h2 class="mb-0">
            <i class="fas fa-boxes me-2 text-success"></i>Mi Inventario
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
                  <i class="fas fa-cow fa-2x text-success me-2"></i>
                  <span class="fw-bold">Mis Animales: {{ totalAnimales }}</span>
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
                <h5 class="mb-0">Lista de Mis Animales</h5>
              </div>
            </div>
          </div>
          <div class="card-body p-3 p-sm-4">
            <div class="table-responsive">
              <table class="table table-hover">
                <caption class="visually-hidden">Lista de animales del usuario, mostrando ID, nombre/código, raza, edad, estado, ubicación y acciones disponibles</caption>
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
                      <button class="btn btn-sm btn-outline-success me-1" @click="verPerfilAnimal(a.id)">
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
</template>

<script>
import authService from '../../services/authService.js';

export default {
  name: "InventarioUsuario",
  data() {
    return {
      animales: [
        { id: 1, nombre: "Rosita", raza: "Brahman", edad: 2, estado: "Saludable", potrero: "Potrero 1" },
        { id: 2, nombre: "Luna", raza: "Brahman", edad: 1, estado: "En tratamiento", potrero: "Potrero 2" },
        { id: 3, nombre: "Bella", raza: "Holstein", edad: 3, estado: "Saludable", potrero: "Potrero 1" },
        { id: 4, nombre: "Max", raza: "Angus", edad: 4, estado: "Saludable", potrero: "Potrero 2" }
      ]
    };
  },
  mounted() {
    if (!authService.isAuthenticated() || !authService.isUser()) {
      this.$router.push('/login');
      return;
    }

    // Inicializar gráfico si Chart.js está disponible
    this.$nextTick(() => {
      this.initChart();
    });
  },
  computed: {
    totalAnimales() {
      return this.animales.length;
    },
    countSaludable() {
      return this.animales.filter(a => a.estado === 'Saludable').length;
    },
    countTratamiento() {
      return this.animales.filter(a => a.estado === 'En tratamiento').length;
    },
    countRecienNacidos() {
      return this.animales.filter(a => a.edad <= 1).length;
    }
  },
  methods: {
    initChart() {
      // Verificar si Chart.js está disponible
      if (typeof Chart !== 'undefined') {
        const ctx = document.getElementById('inventarioPie');
        if (ctx) {
          const chartCtx = ctx.getContext('2d');
          new Chart(chartCtx, {
            type: 'doughnut',
            data: {
              labels: ['Saludables', 'En tratamiento', 'Otros'],
              datasets: [{
                data: [
                  this.countSaludable,
                  this.countTratamiento,
                  Math.max(0, this.totalAnimales - this.countSaludable - this.countTratamiento)
                ],
                backgroundColor: ['#28a745', '#ffc107', '#6c757d'],
                borderWidth: 2,
                borderColor: '#fff'
              }]
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                legend: {
                  position: 'bottom',
                  labels: {
                    padding: 20,
                    usePointStyle: true
                  }
                }
              }
            }
          });
        }
      }
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

    estadoClass(estado) {
      if (estado === 'Saludable') return 'bg-success';
      if (estado === 'En tratamiento') return 'bg-warning';
      if (estado === 'Enfermo') return 'bg-danger';
      return 'bg-secondary';
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
  border-radius: var(--border-radius-lg) var(--border-radius-lg) 0 0 !important;
}

#inventarioPie {
  max-height: 320px;
  width: 100% !important;
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

.badge {
  font-size: 0.75rem;
  padding: 0.5rem 1rem;
  border-radius: var(--border-radius-sm);
  font-weight: 600;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
}

.btn-outline-success {
  border-color: #28a745;
  color: #28a745;
  transition: var(--transition);
}

.btn-outline-success:hover {
  background: linear-gradient(135deg, #28a745 0%, #1e7e34 100%);
  border-color: #28a745;
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

@media (max-width: 768px) {
  .container-fluid {
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

  .btn {
    padding: 0.5rem 1rem;
    font-size: 0.875rem;
  }

  .card-body {
    padding: 1rem;
  }
}
</style>