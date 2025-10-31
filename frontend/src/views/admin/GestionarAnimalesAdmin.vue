<template>
  <div class="container-fluid py-4">
    <div class="row">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h2 class="mb-0">Gestión de Ganado</h2>
          <button class="btn btn-success" @click="showAddAnimalModal = true">
            <i class="fas fa-plus me-2"></i>Agregar Animal
          </button>
        </div>

        <!-- Tabla de ganado -->
        <div class="card">
          <div class="card-body">
            <div class="table-responsive">
              <table class="table table-striped">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Nombre</th>
                    <th>Raza</th>
                    <th>Edad</th>
                    <th>Peso (kg)</th>
                    <th>Estado</th>
                    <th>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="animal in ganado" :key="animal.id">
                    <td>{{ animal.id }}</td>
                    <td>{{ animal.nombre }}</td>
                    <td>{{ animal.raza }}</td>
                    <td>{{ animal.edad }} años</td>
                    <td>{{ animal.peso }}</td>
                    <td>
                      <span class="badge" :class="animal.estado === 'activo' ? 'bg-success' : 'bg-secondary'">
                        {{ animal.estado }}
                      </span>
                    </td>
                    <td>
                      <button class="btn btn-sm btn-outline-primary me-2" @click="editAnimal(animal)">
                        <i class="fas fa-edit"></i>
                      </button>
                      <button class="btn btn-sm btn-outline-danger" @click="deleteAnimal(animal)">
                        <i class="fas fa-trash"></i>
                      </button>
                    </td>
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
import { ganadoAPI } from '../../services/api.js';

export default {
  name: 'GestionarAnimalesAdmin',
  data() {
    return {
      ganado: [],
      showAddAnimalModal: false
    };
  },
  mounted() {
    this.cargarGanado();
  },
  methods: {
    async cargarGanado() {
      try {
        const response = await ganadoAPI.getAll();
        if (response.data?.status === 'success') {
          this.ganado = response.data.data;
        }
      } catch (error) {
        console.error('Error cargando ganado:', error);
      }
    },

    editAnimal(animal) {
      console.log('Editar animal:', animal);
    },

    deleteAnimal(animal) {
      console.log('Eliminar animal:', animal);
    }
  }
};
</script>

<style scoped>
.container-fluid {
  padding: 2rem 1.5rem;
}

h2 {
  color: #343a40;
  font-weight: 700;
  margin-bottom: 2rem;
}

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

.btn-success {
  background: linear-gradient(135deg, #28a745 0%, #1e7e34 100%);
  border: none;
  font-weight: 600;
  padding: 0.75rem 1.5rem;
  border-radius: var(--border-radius);
  transition: var(--transition);
}

.btn-success:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow);
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
  padding: 0.375rem 0.75rem;
  border-radius: var(--border-radius-sm);
  font-weight: 500;
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

.btn-outline-danger {
  border-color: #dc3545;
  color: #dc3545;
  transition: var(--transition);
}

.btn-outline-danger:hover {
  background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
  border-color: #dc3545;
  color: white;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
}

@media (max-width: 768px) {
  .container-fluid {
    padding: 1rem;
  }

  .d-flex.justify-content-between {
    flex-direction: column;
    gap: 1rem;
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
}
</style>
