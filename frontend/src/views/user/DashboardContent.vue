<template>
  <div class="container-fluid py-4">
    <div class="row">
      <div class="col-12">
        <h2 class="mb-4">Panel de Usuario</h2>

        <!-- Estadísticas del usuario -->
        <div class="row g-4 mb-4">
          <div class="col-md-4">
            <div class="card stats-card border-success">
              <div class="card-body text-center">
                <i class="fas fa-cow fa-2x text-success mb-2"></i>
                <h4 class="card-title">{{ estadisticas.ganado }}</h4>
                <p class="card-text text-muted">Mi Ganado</p>
              </div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="card stats-card border-info">
              <div class="card-body text-center">
                <i class="fas fa-boxes fa-2x text-info mb-2"></i>
                <h4 class="card-title">{{ estadisticas.inventario }}</h4>
                <p class="card-text text-muted">Items en Inventario</p>
              </div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="card stats-card border-warning">
              <div class="card-body text-center">
                <i class="fas fa-syringe fa-2x text-warning mb-2"></i>
                <h4 class="card-title">{{ estadisticas.vacunaciones }}</h4>
                <p class="card-text text-muted">Vacunaciones Registradas</p>
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
                <router-link class="btn btn-success w-100" to="/user/gestionar-animales">
                  <i class="fas fa-plus-circle me-2"></i>Agregar Ganado
                </router-link>
              </div>
              <div class="col-md-4">
                <router-link class="btn btn-info w-100" to="/user/inventario">
                  <i class="fas fa-boxes me-2"></i>Ver Inventario
                </router-link>
              </div>
              <div class="col-md-4">
                <router-link class="btn btn-warning w-100" to="/user/qr">
                  <i class="fas fa-qrcode me-2"></i>Escanear QR
                </router-link>
              </div>
            </div>
          </div>
        </div>

        <!-- Información del usuario -->
        <div class="card mt-4">
          <div class="card-header">
            <h5 class="mb-0">Mi Información</h5>
          </div>
          <div class="card-body">
            <div class="row">
              <div class="col-md-6">
                <p><strong>Nombre:</strong> {{ userInfo.nombre }}</p>
                <p><strong>Email:</strong> {{ userInfo.email }}</p>
              </div>
              <div class="col-md-6">
                <p><strong>Rol:</strong> Usuario</p>
                <p><strong>Estado:</strong> <span class="badge bg-success">Activo</span></p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ganadoAPI, userAPI } from '../../services/api.js';
import authService from '../../services/authService.js';

export default {
  name: 'DashboardContent',
  data() {
    return {
      estadisticas: {
        ganado: 0,
        inventario: 0,
        vacunaciones: 0
      },
      userInfo: {
        nombre: '',
        email: ''
      }
    };
  },
  mounted() {
    this.cargarDatosUsuario();
    this.cargarEstadisticas();
  },
  methods: {
    cargarDatosUsuario() {
      const user = authService.getUser();
      if (user && user.persona) {
        this.userInfo.nombre = user.persona.nombre_completo || 'Usuario';
        this.userInfo.email = user.persona.email || '';
      }
    },

    async cargarEstadisticas() {
      try {
        // Cargar estadísticas de ganado del usuario
        const ganadoResponse = await ganadoAPI.getAll();
        this.estadisticas.ganado = ganadoResponse.data?.data?.length || 0;

        // Inventario simulado
        this.estadisticas.inventario = Math.floor(Math.random() * 50) + 10;

        // Vacunaciones simuladas
        this.estadisticas.vacunaciones = Math.floor(Math.random() * 20) + 5;
      } catch (error) {
        console.error('Error cargando estadísticas:', error);
        // En caso de error, mostrar valores por defecto
        this.estadisticas = {
          ganado: 8,
          potreros: 3,
          salud: 90
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