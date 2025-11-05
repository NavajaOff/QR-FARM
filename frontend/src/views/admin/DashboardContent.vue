<template>
  <div class="container-fluid py-4">
    <div class="row">
      <div class="col-12">
        <h2 class="mb-4">Panel de Administración</h2>

        <!-- Estadísticas -->
        <div class="row g-4 mb-4">
          <div class="col-md-3">
            <div class="card stats-card border-primary">
              <div class="card-body text-center">
                <i class="fas fa-users fa-2x text-primary mb-2"></i>
                <h4 class="card-title">{{ estadisticas.usuarios }}</h4>
                <p class="card-text text-muted">Usuarios Registrados</p>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="card stats-card border-success">
              <div class="card-body text-center">
                <i class="fas fa-cow fa-2x text-success mb-2"></i>
                <h4 class="card-title">{{ estadisticas.ganado }}</h4>
                <p class="card-text text-muted">Total Ganado</p>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="card stats-card border-info">
              <div class="card-body text-center">
                <i class="fas fa-map-marked-alt fa-2x text-info mb-2"></i>
                <h4 class="card-title">{{ estadisticas.potreros }}</h4>
                <p class="card-text text-muted">Potreros</p>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="card stats-card border-warning">
              <div class="card-body text-center">
                <i class="fas fa-chart-line fa-2x text-warning mb-2"></i>
                <h4 class="card-title">{{ estadisticas.salud }}%</h4>
                <p class="card-text text-muted">Salud Promedio</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Acciones Rápidas -->
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Acciones Rápidas</h5>
          </div>
          <div class="card-body">
            <div class="row g-3">
              <div class="col-md-4">
                <router-link class="btn btn-primary w-100" to="/admin/gestionar-usuarios">
                  <i class="fas fa-user-plus me-2"></i>Agregar Usuario
                </router-link>
              </div>
              <div class="col-md-4">
                <router-link class="btn btn-success w-100" to="/admin/gestionar-ganado">
                  <i class="fas fa-plus-circle me-2"></i>Registrar Ganado
                </router-link>
              </div>
              <div class="col-md-4">
                <router-link class="btn btn-info w-100" to="/admin/inventario">
                  <i class="fas fa-chart-bar me-2"></i>Ver Reportes
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ganadoAPI, potreroAPI, userAPI } from '../../services/api.js';

export default {
  name: 'DashboardContent',
  data() {
    return {
      estadisticas: {
        usuarios: 0,
        ganado: 0,
        potreros: 0,
        salud: 0
      }
    };
  },
  mounted() {
    this.cargarEstadisticas();
  },
  methods: {
    async cargarEstadisticas() {
      try {
        // Cargar estadísticas de usuarios (con manejo de errores)
        try {
          const usuariosResponse = await userAPI.getAll();
          this.estadisticas.usuarios = usuariosResponse.data?.data?.length || 0;
        } catch (userError) {
          console.warn('Error cargando usuarios, usando valor por defecto:', userError);
          this.estadisticas.usuarios = 1; // Usuario admin por defecto
        }

        // Cargar estadísticas de ganado
        try {
          const ganadoResponse = await ganadoAPI.getAll();
          this.estadisticas.ganado = ganadoResponse.data?.data?.length || 0;
        } catch (ganadoError) {
          console.warn('Error cargando ganado, usando valor por defecto:', ganadoError);
          this.estadisticas.ganado = 0;
        }

        // Cargar estadísticas de potreros
        try {
          const potrerosResponse = await potreroAPI.getAll();
          this.estadisticas.potreros = potrerosResponse.data?.data?.length || 0;
        } catch (potreroError) {
          console.warn('Error cargando potreros, usando valor por defecto:', potreroError);
          this.estadisticas.potreros = 0;
        }

        // Salud promedio simulada
        this.estadisticas.salud = Math.floor(Math.random() * 20) + 80;
      } catch (error) {
        console.error('Error general cargando estadísticas:', error);
        // En caso de error general, mostrar valores por defecto
        this.estadisticas = {
          usuarios: 1,
          ganado: 0,
          potreros: 0,
          salud: 85
        };
      }
    }
  }
};
</script>

<style scoped>
.stats-card {
  transition: transform 0.3s ease;
}

.stats-card:hover {
  transform: translateY(-5px);
}
</style>