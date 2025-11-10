import authService from '../../services/authService.js';
import { ganadoAPI, potreroAPI, userAPI } from '../../services/api.js';

export default {
  name: 'DashboardAdmin',
  data() {
    return {
      userName: '',
      estadisticas: {
        usuarios: 0,
        ganado: 0,
        potreros: 0,
        salud: 0
      }
    };
  },
  mounted() {
    if (!authService.isAuthenticated() || !authService.isAdmin()) {
      this.$router.push('/login');
      return;
    }

    const user = authService.getUser();
    this.userName = user?.persona?.primer_nombre || 'Administrador';

    this.cargarEstadisticas();
  },
  methods: {
    async cargarEstadisticas() {
      try {
        // Cargar estadísticas de usuarios
        const usuariosResponse = await userAPI.getAll();
        this.estadisticas.usuarios = usuariosResponse.data?.data?.length || 0;

        // Cargar estadísticas de ganado
        const ganadoResponse = await ganadoAPI.getAll();
        this.estadisticas.ganado = ganadoResponse.data?.data?.length || 0;

        // Cargar estadísticas de potreros
        const potrerosResponse = await potreroAPI.getAll();
        this.estadisticas.potreros = potrerosResponse.data?.data?.length || 0;

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