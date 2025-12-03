<template>
  <div class="registro-vacunacion-base">
    <!-- Estado de carga -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Cargando...</span>
      </div>
      <p class="mt-3 text-muted">Cargando vacunaciones...</p>
    </div>

    <!-- Mensaje cuando no hay vacunaciones -->
    <div v-else-if="!loading && vacunaciones.length === 0" class="empty-state">
      <div class="card border-0 shadow-sm">
        <div class="card-body text-center py-5">
          <i class="fas fa-syringe fa-3x text-muted mb-3"></i>
          <h4 class="text-muted mb-3">No hay vacunaciones registradas</h4>
          <p class="text-muted mb-4">
            Hasta el momento no se han registrado vacunaciones en el sistema.
          </p>
          <p class="text-muted small">
            Las vacunaciones registradas aparecerán aquí una vez que sean agregadas.
          </p>
        </div>
      </div>
    </div>

    <!-- Lista de vacunaciones -->
    <div v-else class="vacunaciones-list">
      <div class="card border-0 shadow-sm">
        <div class="card-header bg-white">
          <h5 class="mb-0">
            <i class="fas fa-syringe me-2 text-primary"></i>
            Vacunaciones Registradas ({{ vacunaciones.length }})
          </h5>
        </div>
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-hover mb-0">
              <thead class="table-light">
                <tr>
                  <th>Animal</th>
                  <th>Tipo de Vacuna</th>
                  <th>Fecha Aplicación</th>
                  <th>Próxima Dosis</th>
                  <th>Responsable</th>
                  <th>Estado</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="vacunacion in vacunaciones" :key="vacunacion.id">
                  <td>
                    <strong>{{ vacunacion.nombre_animal || `ID: ${vacunacion.id_animal}` }}</strong>
                  </td>
                  <td>{{ vacunacion.tipo_vacuna || 'No especificado' }}</td>
                  <td>{{ formatDate(vacunacion.fecha_aplicacion) }}</td>
                  <td>{{ formatDate(vacunacion.proxima_dosis) }}</td>
                  <td>{{ vacunacion.responsable || 'No especificado' }}</td>
                  <td>
                    <span :class="['badge', estadoClass(vacunacion.estado)]">
                      {{ estadoLabel(vacunacion.estado) }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { vacunacionAPI } from '../services/api.js';

export default {
  name: 'RegistroVacunacionBase',
  data() {
    return {
      vacunaciones: [],
      loading: true
    };
  },
  async mounted() {
    await this.cargarVacunaciones();
  },
  methods: {
    async cargarVacunaciones() {
      this.loading = true;
      try {
        const response = await vacunacionAPI.getAll();
        this.vacunaciones = response.data?.data || [];
      } catch (error) {
        console.error('Error cargando vacunaciones:', error);
        this.vacunaciones = [];
      } finally {
        this.loading = false;
      }
    },
    formatDate(dateString) {
      if (!dateString) return 'No definida';
      try {
        const date = new Date(dateString);
        return date.toLocaleDateString('es-ES', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit'
        });
      } catch (error) {
        return dateString.split('T')[0] || 'No definida';
      }
    },
    estadoClass(estado) {
      if (estado === 'aplicado' || estado === 'Aplicado') return 'bg-success';
      if (estado === 'pendiente' || estado === 'Pendiente') return 'bg-warning';
      return 'bg-secondary';
    },
    estadoLabel(estado) {
      if (estado === 'aplicado' || estado === 'Aplicado') return 'Aplicado';
      if (estado === 'pendiente' || estado === 'Pendiente') return 'Pendiente';
      return estado || 'Sin estado';
    }
  }
}
</script>

<style scoped>
.registro-vacunacion-base {
  padding: 0;
}

.empty-state {
  margin-top: 2rem;
}

.empty-state .card {
  max-width: 600px;
  margin: 0 auto;
}

.vacunaciones-list {
  margin-top: 1rem;
}

.table th {
  font-weight: 600;
  border-bottom: 2px solid #dee2e6;
}

.table td {
  vertical-align: middle;
}

.spinner-border {
  width: 3rem;
  height: 3rem;
}
</style>