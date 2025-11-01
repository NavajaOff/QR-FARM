<template>
  <div class="container-fluid py-4">
    <div class="row">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h2 class="mb-0">Gestión de Ganado</h2>
          <button class="btn btn-success" @click="addAnimal">
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
                      <button class="btn btn-sm btn-outline-info me-2" @click="viewQR(animal)" title="Ver QR">
                        <i class="fas fa-qrcode"></i>
                      </button>
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

    <!-- Modal para ver QR -->
    <div class="modal fade" id="qrModal" tabindex="-1" aria-labelledby="qrModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="qrModalLabel">Código QR - {{ selectedAnimal?.nombre }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body text-center">
            <div v-if="qrImageUrl" class="qr-container">
              <img :src="qrImageUrl" alt="Código QR" class="img-fluid qr-image" />
            </div>
            <div v-else class="text-muted">
              <i class="fas fa-spinner fa-spin fa-2x"></i>
              <p class="mt-2">Cargando código QR...</p>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ganadoAPI } from '../../services/api.js';
import {
  cargarDatosIniciales,
  animales,
  loading,
  error,
  editarAnimal,
  agregarNuevoAnimal,
  verPerfilAnimal,
  setUpdateCallback
} from '../../assets/js/gestionar_animales.js';

export default {
  name: 'GestionarAnimalesAdmin',
  data() {
    return {
      ganado: [],
      showAddAnimalModal: false,
      showEditAnimalModal: false,
      selectedAnimal: null,
      qrImageUrl: null,
      editingAnimal: null
    };
  },
  mounted() {
    this.cargarGanado();
    // Configurar callback para actualizar la lista desde el JS
    setUpdateCallback(this.actualizarLista);
  },
  methods: {
    async cargarGanado() {
      try {
        // Usar la función del archivo JS existente
        await cargarDatosIniciales();
        // Copiar los datos a la variable local para compatibilidad
        this.ganado = [...animales.value];
      } catch (error) {
        console.error('Error cargando ganado:', error);
      }
    },

    // Método para actualizar la lista después de cambios
    actualizarLista() {
      this.ganado = [...animales.value];
    },

    viewQR(animal) {
      // Usar la función del archivo JS existente para ver perfil con QR
      verPerfilAnimal(animal.id);
    },

    editAnimal(animal) {
      // Usar la función del archivo JS existente
      editarAnimal(animal.id);
    },

    deleteAnimal(animal) {
      if (confirm(`¿Estás seguro de que deseas eliminar al animal "${animal.nombre}"?`)) {
        console.log('Eliminando animal:', animal);
        alert('Funcionalidad de eliminar animal próximamente disponible');
      }
    },

    addAnimal() {
      // Usar la función del archivo JS existente
      agregarNuevoAnimal();
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

.qr-container {
  padding: 2rem;
  background: #f8f9fa;
  border-radius: 10px;
  margin: 1rem 0;
}

.qr-image {
  max-width: 300px;
  max-height: 300px;
  border: 2px solid #dee2e6;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.btn-outline-info {
  border-color: #17a2b8;
  color: #17a2b8;
  transition: var(--transition);
}

.btn-outline-info:hover {
  background: linear-gradient(135deg, #17a2b8 0%, #138496 100%);
  border-color: #17a2b8;
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
