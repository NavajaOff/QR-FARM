<template>
  <div class="header-dashboard">
    <!-- Dropdown del usuario -->
    <div class="dropdown">
      <button class="btn btn-outline-light dropdown-toggle d-flex align-items-center" type="button" id="userDropdown" data-bs-toggle="dropdown" aria-expanded="false">
        <i class="fas fa-user me-2"></i>
        <span>{{ userName }}</span>
        <span class="badge bg-info ms-2">{{ userRole }}</span>
      </button>
      <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="userDropdown">
        <li><router-link class="dropdown-item" to="/user/perfil"><i class="fas fa-user-edit me-2"></i>Perfil</router-link></li>
        <li><router-link class="dropdown-item" to="/user/qr"><i class="fas fa-qrcode me-2"></i>Escanear QR</router-link></li>
        <li><hr class="dropdown-divider"></li>
        <li><a class="dropdown-item text-danger" href="#" @click="logout"><i class="fas fa-sign-out-alt me-2"></i>Cerrar Sesión</a></li>
      </ul>
    </div>
  </div>
</template>

<script>
import authService from '../services/authService.js';

export default {
  name: 'HeaderDashboard',
  data() {
    return {
      userName: '',
      userRole: ''
    };
  },
  mounted() {
    const user = authService.getUser();
    this.userName = user?.persona?.primer_nombre || user?.primer_nombre || 'Usuario';
    this.userRole = authService.getRole() === 'usuario' ? 'Usuario' : 'Administrador';
  },
  methods: {
    logout() {
      authService.logout();
      this.$router.push('/login');
    }
  }
};
</script>

<style scoped>
.header-dashboard {
  position: relative;
}

.dropdown-toggle {
  border: none;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.dropdown-toggle:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.dropdown-menu {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  border-radius: 0.5rem;
}

.dropdown-item {
  transition: all 0.2s ease;
  padding: 0.75rem 1rem;
}

.dropdown-item:hover {
  background: rgba(0, 123, 255, 0.1);
  transform: translateX(5px);
}

.dropdown-item i {
  width: 16px;
  text-align: center;
}

.text-danger:hover {
  background: rgba(220, 53, 69, 0.1) !important;
  color: #dc3545 !important;
}
</style>
