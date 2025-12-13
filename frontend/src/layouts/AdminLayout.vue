<template>
  <div class="admin-layout">
    <!-- Barra superior -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-gradient-primary shadow-sm" aria-label="Barra de navegación del administrador">
      <div class="container-fluid px-4">
  <div class="d-flex align-items-center w-100">
          <button
            class="btn btn-outline-light d-md-none me-3"
            type="button"
            data-bs-toggle="offcanvas"
            data-bs-target="#adminSidebar"
            aria-controls="adminSidebar"
          >
            <i class="fas fa-bars"></i>
          </button>

          <!-- Logo y título -->
          <router-link class="navbar-brand d-flex align-items-center me-4" to="/admin/dashboard">
            <i class="fas fa-tractor text-warning me-2 fa-lg"></i>
            <span class="fw-bold fs-3 text-white">QR FARM</span>
            <i class="fas fa-cow ms-2 text-light"></i>
          </router-link>

          <!-- Espaciador -->
          <div class="flex-grow-1"></div>

          <!-- Selector de Tenant (solo para super admin) -->
          <TenantSelector />

          <!-- Notificaciones -->
          <div class="notification-wrapper me-3" ref="notificationWrapper">
            <button
              class="btn btn-outline-light btn-sm notification-button d-flex align-items-center"
              type="button"
              @click.stop="toggleNotifications"
              title="Ver alertas"
            >
              <i class="fas fa-bell"></i>
              <span v-if="notifications.length" class="badge bg-danger ms-1">
                {{ notifications.length }}
              </span>
              <span class="visually-hidden">Notificaciones</span>
            </button>
            <div v-if="notificationsVisible" class="notification-popover shadow" ref="notificationPopover">
              <div class="notification-header">
                <strong>Alertas próximas</strong>
                <button class="btn btn-link btn-sm text-decoration-none" @click.stop="refreshNotifications">
                  <i class="fas fa-sync-alt"></i>
                </button>
              </div>
              <div v-if="notificationsLoading" class="text-center py-3">
                <div class="spinner-border spinner-border-sm text-primary" role="status"></div>
                <small class="d-block mt-1">Cargando...</small>
              </div>
              <div v-else-if="notificationsError" class="text-danger px-3 py-2 small">
                {{ notificationsError }}
              </div>
              <div v-else-if="notifications.length === 0" class="px-3 py-2 small text-muted">
                Sin alertas próximas en los próximos {{ notificationWindow }} días.
              </div>
            <div v-else class="notification-list">
              <article
                v-for="(notificacion, index) in notifications"
                :key="`${notificacion.tipo}-${index}-${notificacion.id}`"
                class="notification-card"
              >
                <header class="notification-card-header">
                  <span class="badge bg-info text-dark text-uppercase">
                    {{ notificacion.tipo }}
                  </span>
                  <span class="notification-card-date">
                    {{ formatDate(notificacion.fecha) }}
                  </span>
                </header>
                <h6 class="notification-card-title">
                  {{ notificacion.titulo }}
                </h6>
                <p class="notification-card-description">
                  {{ notificacion.descripcion }}
                </p>
                <div class="notification-card-meta">
                  <span>
                    <i class="fas fa-hourglass-half me-1"></i>
                    {{ notificacion.dias_restantes }} días restantes
                  </span>
                </div>
                <div class="notification-card-footer">
                  <div>
                    <strong>Responsable:</strong>
                    <span>{{ notificacion.responsable }}</span>
                  </div>
                  <div>
                    <strong>Contexto:</strong>
                    <span>{{ contextLabel(notificacion) }}</span>
                  </div>
                </div>
              </article>
            </div>
            </div>
          </div>

          <!-- Información del usuario -->
          <div class="d-flex align-items-center me-3">
            <div class="d-flex align-items-center text-white">
              <i class="fas me-2" :class="isSuperAdmin ? 'fa-user-crown' : 'fa-user-shield'"></i>
              <div class="d-none d-sm-block">
                <div class="fw-semibold small">{{ userName }}</div>
                <div class="badge small" :class="isSuperAdmin ? 'bg-warning text-dark' : 'bg-light text-primary'">
                  {{ userRoleDisplay }}
                </div>
              </div>
            </div>
          </div>

          <!-- Botón salir -->
          <button class="btn btn-outline-light btn-sm" @click="logout" title="Cerrar sesión">
            <i class="fas fa-sign-out-alt me-1"></i>
            <span class="d-none d-sm-inline">Salir</span>
          </button>
        </div>
      </div>
    </nav>

    <!-- Menú lateral -->
    <div class="d-none d-md-block admin-sidebar">
      <nav class="nav flex-column py-3" aria-label="Menú lateral de administración">
        <!-- Inicio -->
        <router-link class="nav-link mb-2" to="/admin/dashboard">
          <div class="d-flex align-items-center">
            <i class="fas fa-home me-3 fa-lg"></i>
            <span class="fw-medium">Inicio</span>
          </div>
        </router-link>

        <!-- Gestión (Collapsible) -->
        <div class="nav-item">
          <button class="nav-link mb-2 d-flex align-items-center justify-content-between w-100 text-start"
             data-bs-toggle="collapse"
             data-bs-target="#gestionMenu"
             type="button"
             aria-expanded="false"
             aria-controls="gestionMenu">
            <div class="d-flex align-items-center">
              <i class="fas fa-tasks me-3 fa-lg"></i>
              <span class="fw-medium">Gestión</span>
            </div>
            <i class="fas fa-chevron-down transition-all"></i>
          </button>
          <div class="collapse ps-4" id="gestionMenu">
            <!-- Tenants solo para super admin -->
            <router-link v-if="isSuperAdmin" class="nav-link mb-1 small" to="/admin/gestionar-tenants">
              <i class="fas fa-building me-2"></i>Tenants
            </router-link>
            <!-- Usuarios para admin y super admin -->
            <router-link class="nav-link mb-1 small" to="/admin/gestionar-usuarios">
              <i class="fas fa-users me-2"></i>{{ isSuperAdmin ? 'Administradores' : 'Usuarios' }}
            </router-link>
            <!-- Ganado solo para admin (NO super admin) -->
            <router-link v-if="!isSuperAdmin" class="nav-link mb-1 small" to="/admin/gestionar-animales">
              <i class="fas fa-cow me-2"></i>Ganado
            </router-link>
            <!-- Potreros solo para admin (NO super admin) -->
            <router-link v-if="!isSuperAdmin" class="nav-link mb-1 small" to="/admin/gestionar-potreros">
              <i class="fas fa-map-marked-alt me-2"></i>Potreros
            </router-link>
            <!-- Vacunación solo para admin (NO super admin) -->
            <router-link v-if="!isSuperAdmin" class="nav-link mb-1 small" to="/admin/vacunacion">
              <i class="fas fa-syringe me-2"></i>Vacunación
            </router-link>
            <!-- Reportes solo para admin (NO super admin) -->
            <router-link v-if="!isSuperAdmin" class="nav-link mb-1 small" to="/admin/reportes">
              <i class="fas fa-chart-line me-2"></i>Reportes
            </router-link>
            <!-- Escanear QR solo para admin (NO super admin) -->
            <router-link v-if="!isSuperAdmin" class="nav-link mb-1 small" to="/admin/scan-qr">
              <i class="fas fa-qrcode me-2"></i>Escanear QR
            </router-link>
          </div>
        </div>


        <!-- Espaciador para empujar elementos abajo -->
        <div class="flex-grow-1"></div>
      </nav>
    </div>

    <!-- Main Content -->
    <div class="admin-main-content">
      <router-view />
    </div>
  </div>
</template>

<script>
import authService from '../services/authService.js';
import TenantSelector from '../components/TenantSelector.vue';
import { notificationAPI } from '../services/api.js';

export default {
  components: {
    TenantSelector
  },
  name: 'AdminLayout',
  data() {
    return {
      userName: '',
      notifications: [],
      notificationsVisible: false,
      notificationsLoading: false,
      notificationsError: null,
      notificationWindow: 7
    };
  },
  computed: {
    isSuperAdmin() {
      return authService.getRole() === 'super_admin';
    },
    isAdmin() {
      const role = authService.getRole();
      return role === 'admin' || role === 'administrador';
    },
    userRoleDisplay() {
      const role = authService.getRole();
      if (role === 'super_admin') return 'Super Admin';
      if (role === 'admin' || role === 'administrador') return 'Administrador';
      return 'Admin';
    }
  },
  mounted() {
    console.log("[AdminLayout] Componente montado");

    try {
      // Verificar autenticación y rol con validación explícita
      const isAuth = authService.isAuthenticated();
      const token = authService.getToken();
      const role = authService.getRole();
      const isAdmin = authService.isAdmin();
      const isSuperAdmin = role === 'super_admin';

      console.log("[AdminLayout] Verificación de autenticación:");
      console.log("  - isAuthenticated:", isAuth);
      console.log("  - Token presente:", !!token);
      console.log("  - Rol actual:", role);
      console.log("  - isAdmin():", isAdmin);
      console.log("  - isSuperAdmin:", isSuperAdmin);

      // Validar que el usuario esté autenticado
      if (!isAuth) {
        console.warn("[AdminLayout] Usuario no autenticado, redirigiendo a login");
        this.$router.push('/login');
        return;
      }

      // Validar que el usuario tenga rol de admin o super_admin
      if (!isAdmin && !isSuperAdmin) {
        console.warn("[AdminLayout] Usuario no tiene permisos de administrador, redirigiendo a login");
        console.warn("[AdminLayout] Rol recibido:", role);
        this.$router.push('/login');
        return;
      }

      // Cargar información del usuario
      const user = authService.getUser();
      console.log("[AdminLayout] Datos del usuario:", user);
      
      if (user) {
        this.userName = user?.persona?.primer_nombre || user?.primer_nombre || user?.email || 'Administrador';
        this.fetchNotifications();
        document.addEventListener('click', this.handleDocumentClick);
        console.log("[AdminLayout] Nombre de usuario establecido:", this.userName);
      } else {
        console.warn("[AdminLayout] No se encontraron datos del usuario, usando valor por defecto");
        this.userName = 'Administrador';
      }

      console.log("[AdminLayout] Inicialización completada correctamente");
    } catch (error) {
      console.error('[AdminLayout] Error en mounted:', error);
      console.error('[AdminLayout] Stack trace:', error.stack);
      this.$router.push('/login');
    }
  },
  methods: {
    async logout(event) {
      try {
        if (event) {
          event.preventDefault();
          event.stopPropagation();
        }

        authService.logout();
        localStorage.clear();
        sessionStorage.clear();
        await this.$router.push('/login');
      } catch (error) {
        console.error('[AdminLayout] logout error', error);
        localStorage.clear();
        sessionStorage.clear();
        globalThis.location.reload();
      }
    },
    async fetchNotifications() {
      this.notificationsLoading = true;
      this.notificationsError = null;
      try {
        const response = await notificationAPI.getUpcoming();
        this.notifications = response.data?.data || [];
      } catch (error) {
        this.notificationsError = 'No se pudieron cargar las alertas.';
      } finally {
        this.notificationsLoading = false;
      }
    },
    toggleNotifications() {
      this.notificationsVisible = !this.notificationsVisible;
      if (this.notificationsVisible && !this.notifications.length && !this.notificationsLoading) {
        this.fetchNotifications();
      }
    },
    refreshNotifications() {
      this.fetchNotifications();
    },
    formatDate(value) {
      if (!value) {
        return 'Fecha desconocida';
      }
      try {
        return new Date(value).toLocaleDateString('es-ES', {
          day: '2-digit',
          month: 'short',
          year: 'numeric'
        });
      } catch (error) {
        return value;
      }
    },
    contextLabel(notificacion) {
      const contexto = notificacion.contexto || {};
      return (
        contexto.nombre_tipo_vacuna ||
        contexto.nombre_vacuna ||
        contexto.nombre_potrero ||
        contexto.nombre_animal ||
        'Contexto sin detalle'
      );
    },
    handleDocumentClick(event) {
      const popover = this.$refs.notificationPopover;
      const wrapper = this.$refs.notificationWrapper;
      if (!popover || !wrapper) return;
      if (!wrapper.contains(event.target)) {
        this.notificationsVisible = false;
      }
    }
  },
  unmounted() {
    document.removeEventListener('click', this.handleDocumentClick);
  }
};
</script>

<style scoped>
.admin-layout {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}

/* Header con gradiente profesional */
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 76px;
  z-index: 1030;
  background: linear-gradient(135deg, #2c3e50 0%, #3498db 50%, #2980b9 100%) !important;
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
}

.navbar-brand {
  font-weight: 700 !important;
  letter-spacing: 0.5px;
}

.navbar-brand:hover {
  transform: scale(1.02);
  transition: transform 0.2s ease;
}

/* Sidebar moderna */
.admin-sidebar {
  position: fixed;
  top: 76px;
  left: 0;
  width: 280px;
  height: calc(100vh - 76px);
  background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
  backdrop-filter: blur(10px);
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 2px 0 20px rgba(0, 0, 0, 0.1);
  overflow-y: auto;
  overflow-x: hidden;
  z-index: 1020;
}

.admin-sidebar::-webkit-scrollbar {
  width: 6px;
}

.admin-sidebar::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
}

.admin-sidebar::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 3px;
}

.admin-sidebar .nav-link {
  color: rgba(255, 255, 255, 0.85);
  padding: 0.875rem 1.25rem;
  margin: 0.125rem 0.5rem;
  border-radius: 0.5rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-weight: 500;
  position: relative;
  overflow: hidden;
}

.admin-sidebar .nav-link::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  transition: left 0.5s;
}

.admin-sidebar .nav-link:hover::before {
  left: 100%;
}

.admin-sidebar .nav-link:hover {
  color: #fff;
  background: rgba(0, 0, 0, 0.25);
  transform: translateX(5px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.admin-sidebar .nav-link.router-link-active {
  color: #000;
  background: linear-gradient(135deg, #3498db, #2980b9);
  box-shadow: 0 4px 20px rgba(52, 152, 219, 0.4);
  transform: translateX(8px);
}

.admin-sidebar .nav-link.router-link-active::after {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 60%;
  background: #fff;
  border-radius: 0 2px 2px 0;
}

/* Submenú */
.admin-sidebar .collapse .nav-link {
  padding: 0.5rem 1rem 0.5rem 2rem;
  margin: 0.125rem 0.5rem;
  font-size: 0.875rem;
  background: rgba(255, 255, 255, 0.05);
  border-left: 2px solid rgba(255, 255, 255, 0.2);
}

.admin-sidebar .collapse .nav-link:hover {
  background: rgba(255, 255, 255, 0.1);
  border-left-color: rgba(255, 255, 255, 0.4);
}

.admin-sidebar .collapse .nav-link.router-link-active {
  background: rgba(52, 152, 219, 0.3);
  border-left-color: #3498db;
}

/* Separador */
.admin-sidebar hr {
  border-color: rgba(255, 255, 255, 0.2);
  margin: 1rem 1rem;
}

/* Sección de reportes */
.admin-sidebar .text-muted {
  color: rgba(255, 255, 255, 0.6) !important;
  font-size: 0.75rem;
  letter-spacing: 0.5px;
}

/* Botón logout */
.admin-sidebar .text-danger {
  color: #e74c3c !important;
}

.admin-sidebar .text-danger:hover {
  background: rgba(231, 76, 60, 0.2) !important;
  color: #000 !important;
}

/* Contenido principal */
.admin-main-content {
  margin-left: 280px;
  padding: 2rem;
  min-height: calc(100vh - 76px);
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  padding-top: calc(2rem + 76px);
  margin-top: 0;
  position: relative;
  z-index: 1;
  overflow-y: auto;
  overflow-x: hidden;
}

/* Animaciones */
.transition-all {
  transition: all 0.3s ease;
}

/* Responsive */
@media (max-width: 991px) {
  .admin-sidebar {
    width: 260px;
  }

  .admin-main-content {
    margin-left: 260px;
  }
}

@media (max-width: 767px) {
  .admin-sidebar {
    display: none !important;
  }

  .admin-main-content {
    margin-left: 0 !important;
    padding: 1rem;
  }

  .navbar-brand span {
    display: none;
  }

  .navbar-brand i.fa-tractor {
    margin-right: 0.5rem !important;
  }
}

/* Efectos adicionales */
.admin-sidebar .nav-link i {
  width: 20px;
  text-align: center;
}


.notification-wrapper {
  position: relative;
}

.notification-button {
  position: relative;
}

.notification-popover {
  position: absolute;
  right: 0;
  top: calc(100% + 0.5rem);
  width: 320px;
  background: #fff;
  color: #212529;
  border-radius: 0.5rem;
  padding: 0.75rem;
  box-shadow: 0 6px 25px rgba(0, 0, 0, 0.15);
  z-index: 1050;
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.notification-list {
  max-height: 320px;
  overflow-y: auto;
}

.notification-item {
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  padding: 0.45rem 0;
}

.notification-item:last-child {
  border-bottom: none;
}

.notification-title {
  font-weight: 600;
  font-size: 0.95rem;
}

.notification-meta {
  font-size: 0.8rem;
}

.notification-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 0.75rem;
  padding: 0.85rem;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
  margin-bottom: 0.85rem;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.notification-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.25rem;
}

.notification-card-title {
  font-size: 1rem;
  margin: 0;
  font-weight: 600;
}

.notification-card-description {
  margin: 0.35rem 0;
  font-size: 0.9rem;
}

.notification-card-meta {
  display: flex;
  justify-content: flex-start;
  gap: 1rem;
  font-size: 0.8rem;
  color: #4a4a4a;
}

.notification-card-footer {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  color: #2f2f2f;
  margin-top: 0.5rem;
  border-top: 1px dashed rgba(0, 0, 0, 0.12);
  padding-top: 0.45rem;
}

.notification-card-footer span {
  margin-left: 0.35rem;
  font-weight: 500;
}


/* Gradiente para el fondo */
.admin-layout::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle at 20% 80%, rgba(52, 152, 219, 0.1) 0%, transparent 50%),
              radial-gradient(circle at 80% 20%, rgba(155, 89, 182, 0.1) 0%, transparent 50%);
  pointer-events: none;
  z-index: -1;
}
</style>