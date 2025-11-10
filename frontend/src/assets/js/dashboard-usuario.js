import authService from '../../services/authService.js';
import { ganadoAPI, vacunacionAPI } from '../../services/api.js';

/**
 * Componente DashboardUsuario
 * Maneja la lógica del dashboard principal de usuarios
 */
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
    /**
     * Carga las estadísticas del usuario
     */
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

        // Salud promedio simulada para demo - en producción calcular con datos reales
        // Usando Math.random() de manera segura ya que es solo para mostrar datos de ejemplo
        // eslint-disable-next-line sonarjs/pseudo-random
        this.estadisticas.salud = Math.floor(Math.random() * 20) + 80;
      } catch (error) {
        console.error('Error cargando estadísticas:', error);
      }
    },

    /**
     * Cierra la sesión del usuario
     */
    logout() {
      authService.logout();
      this.$router.push('/login');
    }
  }
};