import authService from '../../services/authService.js';
import { ganadoAPI, vacunacionAPI } from '../../services/api.js';

const generarFraccionAleatoriaDemo = () => {
  if (typeof crypto !== 'undefined' && typeof crypto.getRandomValues === 'function') {
    const buffer = new Uint32Array(1);
    crypto.getRandomValues(buffer);
    return buffer[0] / 0xffffffff;
  }
  const timestamp = Date.now();
  const entropia = Number(String(timestamp).slice(-6));
  return (entropia % 1000) / 1000;
};

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

        // Salud promedio simulada de demostración (no representa datos sensibles)
        this.estadisticas.salud = Math.floor(generarFraccionAleatoriaDemo() * 20) + 80;
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