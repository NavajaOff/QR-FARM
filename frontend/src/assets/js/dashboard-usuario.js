import authService from '../../services/authService.js';
import { ganadoAPI, vacunacionAPI } from '../../services/api.js';

export default {
  name: 'DashboardUsuario',
  data() {
    return {
      userName: '',
      userRole: 'Usuario',
      estadisticas: {
        ganado: 0,
        vacunas: 0,
        salud: 0
      }
    };
  },
  mounted() {
    if (!authService.isAuthenticated() || !authService.isUser()) {
      this.$router.push('/login');
      return;
    }

    const user = authService.getUser();
    this.userName = user?.persona?.primer_nombre || 'Usuario';
    this.userRole = user?.rol?.rol || 'Usuario';

    this.cargarEstadisticas();
  },
  methods: {
    async cargarEstadisticas() {
      try {
        const user = authService.getUser();
        const userId = user?.id;

        // Cargar ganado del usuario
        const ganadoResponse = await ganadoAPI.getAll();
        const ganadoUsuario = ganadoResponse.data?.data?.filter(g => g.id_persona === userId) || [];
        this.estadisticas.ganado = ganadoUsuario.length;

        // Cargar vacunas aplicadas
        const vacunasResponse = await vacunacionAPI.getAll();
        this.estadisticas.vacunas = vacunasResponse.data?.data?.length || 0;

        // Salud promedio simulada
        this.estadisticas.salud = Math.floor(Math.random() * 20) + 80;
      } catch (error) {
        console.error('Error cargando estadísticas:', error);
      }
    },

    logout() {
      authService.logout();
      this.$router.push('/login');
    }
  }
};