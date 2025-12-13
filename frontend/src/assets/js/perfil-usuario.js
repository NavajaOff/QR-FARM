import authService from '../../services/authService.js';
import { authAPI } from '../../services/api.js';

/**
 * Componente PerfilUsuario
 * Maneja la lógica del perfil de usuario
 */
export default {
  name: 'PerfilUsuario',
  data() {
    return {
      userName: '',
      userRole: '',
      loading: false,
      message: '',
      messageType: '',
      mostrarResumen: true,
      profile: {
        nombreCompleto: '',
        email: '',
        telefono: '',
        fechaCreacion: '',
        cargo: '',
        cargoId: null
      }
    };
  },
  mounted() {
    if (!authService.isAuthenticated() || !authService.isUser()) {
      this.$router.push('/login');
      return;
    }

    this.userRole = authService.getRole();
    this.userName = authService.getUser()?.persona?.primer_nombre || 'Usuario';

    this.fetchProfile();
  },

  watch: {
    '$route'(to) {
      if (to.name === 'PerfilUsuario') {
        this.fetchProfile();
      }
    }
  },
  methods: {
    /**
     * Obtiene el perfil del usuario desde la API
     */
    async fetchProfile() {
      try {
        const response = await authAPI.getProfile();
        if (response.data?.status === 'success') {
          const data = response.data.data;
          this.profile = {
            nombreCompleto: data.nombre_completo || '',
            email: data.email || '',
            telefono: data.telefono || '',
            fechaCreacion: data.fecha_creacion || '',
            cargo: data.cargo || '',
            cargoId: data.cargo_id || null
          };
          this.mostrarResumen = true; // Mostrar el resumen por defecto
        } else {
          throw new Error(response.data?.message || 'No se pudo cargar el perfil');
        }
      } catch (error) {
        this.message = error.message || 'Error al cargar el perfil';
        this.messageType = 'error';
      }
    },

    /**
     * Actualiza el perfil del usuario
     */
    async updateProfile() {
      this.loading = true;
      this.message = '';

      try {
        const payload = {
          nombre_completo: this.profile.nombreCompleto,
          email: this.profile.email,
          telefono: this.profile.telefono
        };

        const response = await authAPI.updateProfile(payload);
        if (response.data?.status === 'success') {
          this.message = response.data?.message || 'Perfil actualizado exitosamente';
          this.messageType = 'success';
          await this.fetchProfile();
          this.mostrarResumen = true; // Volver a mostrar el resumen después de la actualización
        } else {
          throw new Error(response.data?.message || 'No se pudo actualizar el perfil');
        }
      } catch (error) {
        this.message = error.message || 'Error al actualizar el perfil';
        this.messageType = 'error';
      } finally {
        this.loading = false;
      }
    },

    /**
     * Cancela la edición y vuelve al resumen
     */
    cancelarEdicion() {
      this.mostrarResumen = true;
      this.fetchProfile(); // Recargar los datos para mostrar el resumen actualizado
    },

    /**
     * Formatea una fecha para mostrar
     * @param {string} dateString - Fecha en formato string
     * @returns {string} Fecha formateada o 'N/A'
     */
    formatDate(dateString) {
      if (!dateString) return 'N/A';
      return new Date(dateString).toLocaleDateString();
    }
  }
};