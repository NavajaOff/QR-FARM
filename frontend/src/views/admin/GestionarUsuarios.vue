<template>
  <div class="container-fluid py-4">
    <div class="row">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h2 class="mb-0">Gestión de Usuarios</h2>
        </div>

        <!-- Tabla de usuarios -->
        <div class="card">
          <div class="card-body">
            <div class="table-responsive">
              <table class="table table-striped">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Nombre</th>
                    <th>Email</th>
                    <th>Rol</th>
                    <th>Estado</th>
                    <th>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="usuario in usuarios" :key="usuario.id">
                    <td>{{ usuario.id }}</td>
                    <td>{{ usuario.nombre }}</td>
                    <td>{{ usuario.email }}</td>
                    <td>
                      <span class="badge" :class="usuario.rol === 'admin' ? 'bg-danger' : 'bg-primary'">
                        {{ usuario.rol }}
                      </span>
                    </td>
                    <td>
                      <span class="badge" :class="usuario.estado === 'activo' ? 'bg-success' : 'bg-secondary'">
                        {{ usuario.estado }}
                      </span>
                    </td>
                    <td>
                      <button class="btn btn-sm btn-outline-primary me-2" @click="editUser(usuario)">
                        <i class="fas fa-edit"></i>
                      </button>
                      <button
                        v-if="isCurrentUserAdmin"
                        class="btn btn-sm"
                        :class="usuario.estado === 'activo' ? 'btn-outline-warning' : 'btn-outline-success'"
                        @click="toggleUserStatus(usuario)"
                        :title="usuario.estado === 'activo' ? 'Desactivar usuario' : 'Activar usuario'"
                      >
                        <i class="fas" :class="usuario.estado === 'activo' ? 'fa-ban' : 'fa-check'"></i>
                        {{ usuario.estado === 'activo' ? 'Desactivar' : 'Activar' }}
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

    <!-- Modal de edición de usuario -->
    <div class="modal fade" :class="{ 'show d-block': showEditModal }" tabindex="-1" role="dialog">
      <div class="modal-dialog modal-lg" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Editar Usuario</h5>
            <button type="button" class="btn-close" @click="closeEditModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="updateUser">
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="primer_nombre" class="form-label">Primer Nombre *</label>
                  <input
                    type="text"
                    class="form-control"
                    id="primer_nombre"
                    v-model="editForm.primer_nombre"
                    required
                  >
                </div>
                <div class="col-md-6 mb-3">
                  <label for="segundo_nombre" class="form-label">Segundo Nombre</label>
                  <input
                    type="text"
                    class="form-control"
                    id="segundo_nombre"
                    v-model="editForm.segundo_nombre"
                  >
                </div>
              </div>
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="primer_apellido" class="form-label">Primer Apellido *</label>
                  <input
                    type="text"
                    class="form-control"
                    id="primer_apellido"
                    v-model="editForm.primer_apellido"
                    required
                  >
                </div>
                <div class="col-md-6 mb-3">
                  <label for="segundo_apellido" class="form-label">Segundo Apellido</label>
                  <input
                    type="text"
                    class="form-control"
                    id="segundo_apellido"
                    v-model="editForm.segundo_apellido"
                  >
                </div>
              </div>
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="email" class="form-label">Email *</label>
                  <input
                    type="email"
                    class="form-control"
                    id="email"
                    v-model="editForm.email"
                    required
                  >
                </div>
                <div class="col-md-6 mb-3">
                  <label for="telefono" class="form-label">Teléfono</label>
                  <input
                    type="tel"
                    class="form-control"
                    id="telefono"
                    v-model="editForm.telefono"
                  >
                </div>
              </div>
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="password" class="form-label">Nueva Contraseña (opcional)</label>
                  <input
                    type="password"
                    class="form-control"
                    id="password"
                    v-model="editForm.password"
                    placeholder="Dejar vacío para mantener la actual"
                  >
                  <div class="form-text">Mínimo 6 caracteres</div>
                </div>
                <div class="col-md-6 mb-3">
                  <label for="estado" class="form-label">Estado</label>
                  <select class="form-select" id="estado" v-model="editForm.estado">
                    <option value="activo">Activo</option>
                    <option value="inactivo">Inactivo</option>
                  </select>
                </div>
              </div>
              <!-- Campo de rol solo visible para administradores -->
              <div v-if="isCurrentUserAdmin" class="row">
                <div class="col-md-6 mb-3">
                  <label for="id_rol" class="form-label">Rol</label>
                  <select class="form-select" id="id_rol" v-model="editForm.id_rol">
                    <option value="1">Administrador</option>
                    <option value="2">Usuario</option>
                  </select>
                </div>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeEditModal">Cancelar</button>
            <button type="button" class="btn btn-primary" @click="updateUser" :disabled="loading">
              <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
              Guardar Cambios
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Backdrop del modal -->
    <div v-if="showEditModal" class="modal-backdrop fade show" @click="closeEditModal"></div>
  </div>
</template>

<script>
import { useUsuarios } from '../../composables/useUsuarios.js';
import authService from '../../services/authService.js';

export default {
  name: 'GestionarUsuarios',
  setup() {
    const {
      usuarios,
      loading,
      error,
      cargarUsuarios,
      actualizarUsuario,
      cambiarEstadoUsuario
    } = useUsuarios();

    return {
      usuarios,
      loading,
      error,
      cargarUsuarios,
      actualizarUsuario,
      cambiarEstadoUsuario
    };
  },
  data() {
    return {
      showAddUserModal: false,
      showEditModal: false,
      editForm: {
        primer_nombre: '',
        segundo_nombre: '',
        primer_apellido: '',
        segundo_apellido: '',
        email: '',
        telefono: '',
        password: '',
        estado: 'activo',
        id_rol: 2
      },
      editingUserId: null
    };
  },
  computed: {
    isCurrentUserAdmin() {
      return authService.isAdmin();
    }
  },
  mounted() {
    this.cargarUsuarios();
  },
  beforeUnmount() {
    console.log('GestionarUsuarios desmontándose...');
  },
  beforeRouteLeave(to, from, next) {
    console.log('Saliendo de vista usuarios, cancelando peticiones...');
    next();
  },
  methods: {
    editUser(usuario) {
      this.editForm = {
        primer_nombre: usuario.persona?.primer_nombre || '',
        segundo_nombre: usuario.persona?.segundo_nombre || '',
        primer_apellido: usuario.persona?.primer_apellido || '',
        segundo_apellido: usuario.persona?.segundo_apellido || '',
        email: usuario.persona?.email || '',
        telefono: usuario.persona?.telefono || '',
        password: '',
        estado: usuario.estado || 'activo',
        id_rol: usuario.id_rol || 2
      };
      this.editingUserId = usuario.id;
      this.showEditModal = true;
    },

    closeEditModal() {
      this.showEditModal = false;
      this.editForm = {
        primer_nombre: '',
        segundo_nombre: '',
        primer_apellido: '',
        segundo_apellido: '',
        email: '',
        telefono: '',
        password: '',
        estado: 'activo',
        id_rol: 2
      };
      this.editingUserId = null;
    },

    async updateUser() {
      if (!this.editingUserId) return;

      if (!this.editForm.primer_nombre.trim()) {
        alert('El primer nombre es requerido');
        return;
      }
      if (!this.editForm.primer_apellido.trim()) {
        alert('El primer apellido es requerido');
        return;
      }
      if (!this.editForm.email.trim()) {
        alert('El email es requerido');
        return;
      }

      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(this.editForm.email)) {
        alert('El formato del email no es válido');
        return;
      }

      if (this.editForm.password && this.editForm.password.length < 6) {
        alert('La contraseña debe tener al menos 6 caracteres');
        return;
      }

      const updateData = {
        primer_nombre: this.editForm.primer_nombre.trim(),
        segundo_nombre: this.editForm.segundo_nombre.trim(),
        primer_apellido: this.editForm.primer_apellido.trim(),
        segundo_apellido: this.editForm.segundo_apellido.trim(),
        email: this.editForm.email.trim(),
        telefono: this.editForm.telefono.trim(),
        estado: this.editForm.estado
      };

      if (this.editForm.password.trim()) {
        updateData.password = this.editForm.password;
      }

      if (this.isCurrentUserAdmin) {
        updateData.id_rol = this.editForm.id_rol;
      }

      const result = await this.actualizarUsuario(this.editingUserId, updateData);
      if (result.success) {
        this.closeEditModal();
        alert('Usuario actualizado exitosamente');
      } else {
        alert('Error al actualizar usuario: ' + result.message);
      }
    },

    async toggleUserStatus(usuario) {
      if (!this.isCurrentUserAdmin) {
        alert('No tienes permisos para cambiar el estado de usuarios');
        return;
      }

      const accion = usuario.estado === 'activo' ? 'desactivar' : 'activar';
      const confirmacion = confirm(`¿Estás seguro de que quieres ${accion} al usuario ${usuario.nombre}?`);

      if (!confirmacion) return;

      const nuevoEstado = usuario.estado === 'activo' ? 'inactivo' : 'activo';
      const result = await this.cambiarEstadoUsuario(usuario.id, nuevoEstado);

      if (result.success) {
        alert(`Usuario ${accion}do exitosamente`);
      } else {
        alert('Error al cambiar el estado del usuario: ' + result.message);
      }
    }
  }
};
</script>

<style scoped>
</style>