import authService from '../../services/authService.js';

export default {
  name: 'PerfilAdmin',
  data() {
    return {
      userName: '',
      user: null,
      userRole: '',
      loading: false,
      passwordLoading: false,
      message: '',
      messageType: '',
      profile: {
        primerNombre: '',
        segundoNombre: '',
        primerApellido: '',
        segundoApellido: '',
        email: '',
        telefono: ''
      },
      passwordData: {
        current: '',
        new: '',
        confirm: ''
      }
    };
  },
  mounted() {
    if (!authService.isAuthenticated() || !authService.isAdmin()) {
      this.$router.push('/login');
      return;
    }

    this.user = authService.getUser();
    this.userRole = authService.getRole();
    this.userName = this.user?.persona?.primer_nombre || 'Administrador';

    this.loadProfile();
  },
  methods: {
    loadProfile() {
      if (this.user?.persona) {
        this.profile = {
          primerNombre: this.user.persona.primer_nombre || '',
          segundoNombre: this.user.persona.segundo_nombre || '',
          primerApellido: this.user.persona.primer_apellido || '',
          segundoApellido: this.user.persona.segundo_apellido || '',
          email: this.user.persona.email || '',
          telefono: this.user.persona.telefono || ''
        };
      }
    },

    async updateProfile() {
      this.loading = true;
      this.message = '';

      try {
        // Aquí iría la llamada a la API para actualizar el perfil
        // Por ahora solo simulamos
        await new Promise(resolve => setTimeout(resolve, 1000));

        this.message = 'Perfil actualizado exitosamente';
        this.messageType = 'success';
      } catch (error) {
        console.error('Error updating profile:', error);
        this.message = 'Error al actualizar el perfil';
        this.messageType = 'error';
      } finally {
        this.loading = false;
      }
    },

    async changePassword() {
      if (this.passwordData.new !== this.passwordData.confirm) {
        this.message = 'Las contraseñas no coinciden';
        this.messageType = 'error';
        return;
      }

      this.passwordLoading = true;
      this.message = '';

      try {
        // Aquí iría la llamada a la API para cambiar contraseña
        await new Promise(resolve => setTimeout(resolve, 1000));

        this.message = 'Contraseña cambiada exitosamente';
        this.messageType = 'success';
        this.passwordData = { current: '', new: '', confirm: '' };
      } catch (error) {
        console.error('Error changing password:', error);
        this.message = 'Error al cambiar la contraseña';
        this.messageType = 'error';
      } finally {
        this.passwordLoading = false;
      }
    },

    formatDate(dateString) {
      if (!dateString) return 'N/A';
      return new Date(dateString).toLocaleDateString();
    },

    logout() {
      authService.logout();
      this.$router.push('/login');
    }
  }
};