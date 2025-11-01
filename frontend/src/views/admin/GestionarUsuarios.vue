<template>
  <div class="container-fluid py-4">
    <div class="row">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h2 class="mb-0">Gestión de Usuarios</h2>
          <button class="btn btn-success" @click="showAddUserModal = true">
            <i class="fas fa-plus me-2"></i>Agregar Usuario
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
                      <button class="btn btn-sm btn-outline-danger" @click="toggleUserStatus(usuario)">
                        <i class="fas" :class="usuario.estado === 'activo' ? 'fa-ban' : 'fa-check'"></i>
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
import { userAPI } from '../../services/api.js';

export default {
  name: 'GestionarUsuarios',
  data() {
    return {
      usuarios: [],
      showAddUserModal: false
    };
  },
  mounted() {
    this.cargarUsuarios();
  },
  beforeUnmount() {
    // Cancelar cualquier petición pendiente al desmontar
    console.log('GestionarUsuarios desmontándose...');
  },
  beforeRouteLeave(to, from, next) {
    // Cancelar peticiones antes de cambiar de ruta
    console.log('Saliendo de vista usuarios, cancelando peticiones...');
    next();
  },
  methods: {
    async cargarUsuarios() {
      try {
        const response = await userAPI.getAll();
        if (response.data?.status === 'success') {
          this.usuarios = response.data.data;
        }
      } catch (error) {
        console.error('Error cargando usuarios:', error);
      }
    },

    editUser(usuario) {
      console.log('Editar usuario:', usuario);
    },

    async toggleUserStatus(usuario) {
      try {
        const nuevoEstado = usuario.estado === 'activo' ? 'inactivo' : 'activo';
        const response = await userAPI.updateStatus(usuario.id, { estado: nuevoEstado });

        if (response.data?.status === 'success') {
          usuario.estado = nuevoEstado;
        }
      } catch (error) {
        console.error('Error cambiando estado:', error);
      }
    }
  }
};
</script>

<style scoped>
</style>