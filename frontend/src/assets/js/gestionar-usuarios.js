import { useUsuarios } from '../../composables/useUsuarios.js';
import authService from '../../services/authService.js';
import { authAPI } from '../../services/api.js';
import Swal from 'sweetalert2';

const SAFE_EMAIL_REGEX = /^[A-Za-z0-9._%+-]{1,64}@[A-Za-z0-9.-]{1,253}\.[A-Za-z]{2,}$/;

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

      const numericCandidate = candidates.find((value) => {
        const parsed = Number(value);
        return !Number.isNaN(parsed) && parsed > 0;
      });

      if (numericCandidate) {
        return Number(numericCandidate);
      }

      let roleFromLabel = null;
      if (typeof usuario?.rol === 'string') {
        const normalized = usuario.rol.toLowerCase();
        if (normalized.includes('admin')) {
          roleFromLabel = 1;
        } else if (normalized.includes('usuario')) {
          roleFromLabel = 2;
        }
      }

      if (roleFromLabel !== null) {
        return roleFromLabel;
      }

      return 2;
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
        Swal.fire('Error', 'El primer nombre es requerido', 'error');
        return;
      }
      if (!this.addForm.primer_apellido.trim()) {
        Swal.fire('Error', 'El primer apellido es requerido', 'error');
        return;
      }
      if (!this.addForm.email.trim()) {
        Swal.fire('Error', 'El email es requerido', 'error');
        return;
      }

      if (!SAFE_EMAIL_REGEX.test(this.addForm.email)) {
        Swal.fire('Error', 'El formato del email no es válido', 'error');
        return;
      }

      if (!this.addForm.password || this.addForm.password.length < 6) {
        Swal.fire('Error', 'La contraseña debe tener al menos 6 caracteres', 'error');
        return;
      }

      if (this.addForm.password !== this.addForm.confirm_password) {
        Swal.fire('Error', 'Las contraseñas no coinciden', 'error');
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
          Swal.fire('¡Éxito!', 'Usuario creado exitosamente', 'success');
          this.closeAddModal();
          await this.cargarUsuarios();
        } else {
          throw new Error(response.data?.message || 'No se pudo crear el usuario');
        }
      } catch (error) {
        Swal.fire('Error', 'Error al crear usuario: ' + (error.message || 'desconocido'), 'error');
      } finally {
        this.creatingUser = false;
      }
    },

    editUser(usuario) {
      console.log('Usuario completo:', usuario);
      console.log('Persona del usuario:', usuario.persona);

      const resolvedRoleId = this.resolveRoleId(usuario);
      const baseData = {
        primer_nombre: usuario.persona?.primer_nombre || usuario.primer_nombre || '',
        segundo_nombre: usuario.persona?.segundo_nombre || usuario.segundo_nombre || '',
        primer_apellido: usuario.persona?.primer_apellido || usuario.primer_apellido || '',
        segundo_apellido: usuario.persona?.segundo_apellido || usuario.segundo_apellido || '',
        email: usuario.persona?.email || usuario.email || '',
        telefono: usuario.persona?.telefono || usuario.telefono || '',
        id_rol: resolvedRoleId
      };

      console.log('Datos base para editar:', baseData);

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
        Swal.fire('Error', 'La contraseña debe tener al menos 6 caracteres', 'error');
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
        const currentField = this.editForm[field];
        let value = currentField;
        if (typeof value === 'string') {
          value = value.trim();
        }

        let originalValue = null;
        if (this.originalEditData) {
          const originalField = this.originalEditData[field];
          originalValue = originalField;
          if (typeof originalField === 'string') {
            originalValue = originalField.trim();
          }
        }

        if (!value) {
          return;
        }

        const comparableOriginal = originalValue ?? '';
        if (value !== comparableOriginal) {
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
        Swal.fire('Información', 'No hay cambios para guardar', 'info');
        return;
      }

      if (updateData.email) {
        if (!SAFE_EMAIL_REGEX.test(updateData.email)) {
          Swal.fire('Error', 'El formato del email no es válido', 'error');
          return;
        }
      }

      const result = await this.actualizarUsuario(this.editingUserId, updateData);
      if (result.success) {
        this.closeEditModal();
        Swal.fire('¡Éxito!', 'Usuario actualizado exitosamente', 'success');
      } else {
        Swal.fire('Error', 'Error al actualizar usuario: ' + result.message, 'error');
      }
    },

    async toggleUserStatus(usuario) {
      if (!this.isCurrentUserAdmin) {
        Swal.fire('Error', 'No tienes permisos para cambiar el estado de usuarios', 'error');
        return;
      }

      const accion = usuario.estado === 'activo' ? 'desactiva' : 'activa';
      const result = await Swal.fire({
        title: '¿Estás seguro?',
        text: `¿Estás seguro de que quieres ${accion} al usuario ${usuario.nombre}?`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Sí, ' + accion,
        cancelButtonText: 'Cancelar'
      });

      if (!result.isConfirmed) return;

      const nuevoEstado = usuario.estado === 'activo' ? 'inactivo' : 'activo';
      const cambioResult = await this.cambiarEstadoUsuario(usuario.id, nuevoEstado);

      
      if (cambioResult.success) {
        Swal.fire('¡Éxito!', `Usuario ${accion}do exitosamente`, 'success');
      } else {
        Swal.fire('Error', 'Error al cambiar el estado del usuario: ' + cambioResult.message, 'error');
      }
    }
  }
};