<template>
  <div class="container-fluid py-4">
    <div class="row">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-3">
          <h2 class="mb-0">Gestión de Usuarios</h2>
          <button class="btn btn-primary" @click="openAddModal">
            <i class="fas fa-user-plus me-2"></i>Agregar usuario
          </button>
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

    <!-- Modal de creación de usuario -->
    <div class="modal fade" :class="{ 'show d-block': showAddUserModal }" tabindex="-1" role="dialog">
      <div class="modal-dialog modal-lg" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Agregar Usuario</h5>
            <button type="button" class="btn-close" @click="closeAddModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="createUser">
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="add_primer_nombre" class="form-label">Primer Nombre *</label>
                  <input
                    type="text"
                    class="form-control"
                    id="add_primer_nombre"
                    v-model="addForm.primer_nombre"
                    required
                  >
                </div>
                <div class="col-md-6 mb-3">
                  <label for="add_segundo_nombre" class="form-label">Segundo Nombre</label>
                  <input
                    type="text"
                    class="form-control"
                    id="add_segundo_nombre"
                    v-model="addForm.segundo_nombre"
                  >
                </div>
              </div>
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="add_primer_apellido" class="form-label">Primer Apellido *</label>
                  <input
                    type="text"
                    class="form-control"
                    id="add_primer_apellido"
                    v-model="addForm.primer_apellido"
                    required
                  >
                </div>
                <div class="col-md-6 mb-3">
                  <label for="add_segundo_apellido" class="form-label">Segundo Apellido</label>
                  <input
                    type="text"
                    class="form-control"
                    id="add_segundo_apellido"
                    v-model="addForm.segundo_apellido"
                  >
                </div>
              </div>
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="add_email" class="form-label">Email *</label>
                  <input
                    type="email"
                    class="form-control"
                    id="add_email"
                    v-model="addForm.email"
                    required
                  >
                </div>
                <div class="col-md-6 mb-3">
                  <label for="add_telefono" class="form-label">Teléfono</label>
                  <input
                    type="tel"
                    class="form-control"
                    id="add_telefono"
                    v-model="addForm.telefono"
                  >
                </div>
              </div>
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="add_password" class="form-label">Contraseña *</label>
                  <input
                    type="password"
                    class="form-control"
                    id="add_password"
                    v-model="addForm.password"
                    required
                  >
                  <div class="form-text">Mínimo 6 caracteres</div>
                </div>
                <div class="col-md-6 mb-3">
                  <label for="add_confirm_password" class="form-label">Confirmar Contraseña *</label>
                  <input
                    type="password"
                    class="form-control"
                    id="add_confirm_password"
                    v-model="addForm.confirm_password"
                    required
                  >
                </div>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeAddModal">Cancelar</button>
            <button type="button" class="btn btn-primary" @click="createUser" :disabled="creatingUser">
              <span v-if="creatingUser" class="spinner-border spinner-border-sm me-2"></span>
              Guardar usuario
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showAddUserModal" class="modal-backdrop fade show" @click="closeAddModal"></div>

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
                  <label for="primer_nombre" class="form-label">Primer Nombre</label>
                  <input
                    type="text"
                    class="form-control"
                    id="primer_nombre"
                    v-model="editForm.primer_nombre"
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
                  <label for="primer_apellido" class="form-label">Primer Apellido</label>
                  <input
                    type="text"
                    class="form-control"
                    id="primer_apellido"
                    v-model="editForm.primer_apellido"
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
                  <label for="email" class="form-label">Email</label>
                  <input
                    type="email"
                    class="form-control"
                    id="email"
                    v-model="editForm.email"
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
              </div>
              <!-- Campo de rol solo visible para administradores -->
              <div v-if="isCurrentUserAdmin" class="row">
                <div class="col-md-6 mb-3">
                  <label for="id_rol" class="form-label">Rol</label>
                  <select class="form-select" id="id_rol" v-model.number="editForm.id_rol">
                    <option :value="1">Administrador</option>
                    <option :value="2">Usuario</option>
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
import { authAPI } from '../../services/api.js';

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
      creatingUser: false,
      addForm: {
        primer_nombre: '',
        segundo_nombre: '',
        primer_apellido: '',
        segundo_apellido: '',
        email: '',
        telefono: '',
        password: '',
        confirm_password: ''
      },
      editForm: {
        primer_nombre: '',
        segundo_nombre: '',
        primer_apellido: '',
        segundo_apellido: '',
        email: '',
        telefono: '',
        password: '',
        id_rol: 2
      },
      originalEditData: null,
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
    resolveRoleId(usuario) {
      const candidates = [
        usuario?.id_rol,
        usuario?.persona?.id_rol,
        usuario?.rol?.id
      ];
      const found = candidates.find((value) => {
        const parsed = Number(value);
        return !Number.isNaN(parsed) && parsed > 0;
      });
      if (!found && typeof usuario?.rol === 'string') {
        const normalized = usuario.rol.toLowerCase();
        if (normalized.includes('admin')) return 1;
        if (normalized.includes('usuario')) return 2;
      }
      return found ? Number(found) : 2;
    },

    openAddModal() {
      this.resetAddForm();
      this.showAddUserModal = true;
    },

    closeAddModal() {
      this.showAddUserModal = false;
      this.resetAddForm();
    },

    resetAddForm() {
      this.addForm = {
        primer_nombre: '',
        segundo_nombre: '',
        primer_apellido: '',
        segundo_apellido: '',
        email: '',
        telefono: '',
        password: '',
        confirm_password: ''
      };
    },

    async createUser() {
      if (this.creatingUser) return;

      if (!this.addForm.primer_nombre.trim()) {
        alert('El primer nombre es requerido');
        return;
      }
      if (!this.addForm.primer_apellido.trim()) {
        alert('El primer apellido es requerido');
        return;
      }
      if (!this.addForm.email.trim()) {
        alert('El email es requerido');
        return;
      }

      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(this.addForm.email)) {
        alert('El formato del email no es válido');
        return;
      }

      if (!this.addForm.password || this.addForm.password.length < 6) {
        alert('La contraseña debe tener al menos 6 caracteres');
        return;
      }

      if (this.addForm.password !== this.addForm.confirm_password) {
        alert('Las contraseñas no coinciden');
        return;
      }

      this.creatingUser = true;
      try {
        const payload = {
          primer_nombre: this.addForm.primer_nombre.trim(),
          segundo_nombre: this.addForm.segundo_nombre.trim() || null,
          primer_apellido: this.addForm.primer_apellido.trim(),
          segundo_apellido: this.addForm.segundo_apellido.trim() || null,
          email: this.addForm.email.trim(),
          telefono: this.addForm.telefono.trim() || null,
          password: this.addForm.password
        };

        const response = await authAPI.register(payload);
        if (response.data?.status === 'success') {
          alert('Usuario creado exitosamente');
          this.closeAddModal();
          await this.cargarUsuarios();
        } else {
          throw new Error(response.data?.message || 'No se pudo crear el usuario');
        }
      } catch (error) {
        alert('Error al crear usuario: ' + (error.message || 'desconocido'));
      } finally {
        this.creatingUser = false;
      }
    },

    editUser(usuario) {
      const resolvedRoleId = this.resolveRoleId(usuario);
      const baseData = {
        primer_nombre: usuario.persona?.primer_nombre || '',
        segundo_nombre: usuario.persona?.segundo_nombre || '',
        primer_apellido: usuario.persona?.primer_apellido || '',
        segundo_apellido: usuario.persona?.segundo_apellido || '',
        email: usuario.persona?.email || '',
        telefono: usuario.persona?.telefono || '',
        id_rol: resolvedRoleId
      };
      this.originalEditData = { ...baseData };
      this.editForm = {
        ...baseData,
        password: ''
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
        id_rol: 2
      };
      this.originalEditData = null;
      this.editingUserId = null;
    },

    async updateUser() {
      if (!this.editingUserId) return;

      if (this.editForm.password && this.editForm.password.length < 6) {
        alert('La contraseña debe tener al menos 6 caracteres');
        return;
      }

      const fieldsToProcess = [
        'primer_nombre',
        'segundo_nombre',
        'primer_apellido',
        'segundo_apellido',
        'email',
        'telefono'
      ];
      const updateData = {};

      fieldsToProcess.forEach(field => {
        const value = typeof this.editForm[field] === 'string'
          ? this.editForm[field].trim()
          : this.editForm[field];

        const originalValue = this.originalEditData
          ? (typeof this.originalEditData[field] === 'string'
            ? this.originalEditData[field].trim()
            : this.originalEditData[field])
          : null;

        if (!value) {
          return;
        }

        if (value !== (originalValue || '')) {
          updateData[field] = value;
        }
      });

      if (this.editForm.password.trim()) {
        updateData.password = this.editForm.password;
      }

      if (this.isCurrentUserAdmin) {
        const currentRoleId = Number(this.editForm.id_rol);
        const originalRoleId = Number(this.originalEditData?.id_rol);
        if (!Number.isNaN(currentRoleId) && (Number.isNaN(originalRoleId) || currentRoleId !== originalRoleId)) {
          updateData.id_rol = currentRoleId;
        }
      }

      if (Object.keys(updateData).length === 0) {
        alert('No hay cambios para guardar');
        return;
      }

      if (updateData.email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(updateData.email)) {
          alert('El formato del email no es válido');
          return;
        }
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