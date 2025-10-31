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
</style>
