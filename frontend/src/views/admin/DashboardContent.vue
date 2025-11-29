<template>
  <div>
    <div class="row">
      <div class="col-12">
        <h2 class="mb-4">Panel de Administración</h2>

        <!-- Mensaje de Bienvenida para Super Admin -->
        <div v-if="isSuperAdmin" class="card border-warning mb-4">
          <div class="card-body">
            <h4 class="card-title mb-3">
              <i class="fas fa-user-crown text-warning me-2"></i>
              ¡Bienvenido, Super Administrador!
            </h4>
            <p class="card-text">
              Como Super Administrador, tienes acceso completo y privilegiado a todo el sistema QR-FARM. 
              Puedes gestionar de forma centralizada todos los aspectos del sistema.
            </p>
            <div class="mt-3">
              <h6 class="fw-bold mb-2">¿Qué puedes hacer como Super Administrador?</h6>
              <ul class="mb-0">
                <li><strong>Gestionar Tenants:</strong> Crear, editar y administrar todas las organizaciones (tenants) del sistema.</li>
                <li><strong>Gestionar Usuarios:</strong> Administrar todos los usuarios de todos los tenants, asignar roles y permisos.</li>
                <li><strong>Supervisión Global:</strong> Visualizar estadísticas y métricas de todo el sistema.</li>
                <li><strong>Control Total:</strong> Acceso completo a todas las funcionalidades sin restricciones de tenant.</li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Selector de Tenant para Super Admin -->
        <TenantSelector v-if="isSuperAdmin" @tenant-changed="onTenantChanged" />

        <!-- Información de Rol y Tenant -->
        <div class="row g-4 mb-4" v-if="!isSuperAdmin && currentTenant">
          <div class="col-12">
            <div class="card border-info">
              <div class="card-body">
                <div class="d-flex align-items-center justify-content-between flex-wrap gap-3">
                  <div>
                    <h5 class="mb-1">
                      <i class="fas fa-building text-primary me-2"></i>
                      Tenant: {{ currentTenant?.nombre || 'N/A' }}
                    </h5>
                    <p class="text-muted mb-0">
                      <code>{{ currentTenant.codigo_tenant }}</code>
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Métricas Clave (solo para Super Admin) -->
        <div v-if="isSuperAdmin" class="row g-4 mb-4">
          <div class="col-md-6">
            <div class="card stats-card border-primary">
              <div class="card-body text-center">
                <i class="fas fa-users fa-3x text-primary mb-3"></i>
                <h2 class="card-title mb-2">{{ estadisticas.usuarios }}</h2>
                <p class="card-text text-muted mb-0">Usuarios Totales</p>
              </div>
            </div>
          </div>
          <div class="col-md-6">
            <div class="card stats-card border-success">
              <div class="card-body text-center">
                <i class="fas fa-building fa-3x text-success mb-3"></i>
                <h2 class="card-title mb-2">{{ estadisticas.tenants }}</h2>
                <p class="card-text text-muted mb-0">Tenants Activos</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Estadísticas para Admin Normal -->
        <div v-else class="row g-4 mb-4">
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

        <!-- Acciones Rápidas (solo para Super Admin según imagen) -->
        <div v-if="isSuperAdmin" class="card">
          <div class="card-header">
            <h5 class="mb-0">Acciones Rápidas</h5>
          </div>
          <div class="card-body">
            <div class="row g-3">
              <div class="col-md-6">
                <router-link class="btn btn-primary w-100" to="/admin/gestionar-tenants">
                  <i class="fas fa-building me-2"></i>Gestionar Tenants
                </router-link>
              </div>
              <div class="col-md-6">
                <router-link class="btn btn-success w-100" to="/admin/gestionar-usuarios">
                  <i class="fas fa-user-plus me-2"></i>Gestionar Usuarios
                </router-link>
              </div>
            </div>
          </div>
        </div>

        <!-- Acciones Rápidas para Admin Normal -->
        <div v-else class="card">
          <div class="card-header">
            <h5 class="mb-0">Acciones Rápidas</h5>
          </div>
          <div class="card-body">
            <div class="row g-3">
              <div class="col-md-4">
                <router-link class="btn btn-success w-100" to="/admin/gestionar-usuarios">
                  <i class="fas fa-user-plus me-2"></i>Agregar Usuario
                </router-link>
              </div>
              <div class="col-md-4">
                <router-link class="btn btn-success w-100" to="/admin/gestionar-ganado">
                  <i class="fas fa-plus-circle me-2"></i>Registrar Ganado
                </router-link>
              </div>
              <div class="col-md-4">
                <router-link class="btn btn-info w-100" to="/admin/reportes">
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
import dashboardContent from '../../assets/js/dashboard-content.js';
import TenantSelector from '../../components/TenantSelector.vue';

export default {
  ...dashboardContent,
  components: {
    TenantSelector
  },
  computed: {
    ...dashboardContent.computed,
    selectedTenantName() {
      const selectedTenantId = localStorage.getItem('qr_farm_selected_tenant_id');
      if (!selectedTenantId) return '';
      const tenantId = Number.parseInt(selectedTenantId, 10);
      if (Number.isNaN(tenantId)) return '';
      // Obtener nombre del tenant desde la lista cargada
      const tenant = this.tenants?.find(t => t.id === tenantId);
      return tenant ? tenant.nombre : '';
    }
  },
  methods: {
    ...dashboardContent.methods,
    onTenantChanged() {
      // Recargar estadísticas cuando cambia el tenant
      this.cargarEstadisticas();
    }
  }
};
</script>

<style scoped>
@import '../../assets/css/dashboard-content.css';
</style>