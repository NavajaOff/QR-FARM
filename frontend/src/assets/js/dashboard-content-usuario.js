import { ganadoAPI, potreroAPI, userAPI, vacunacionAPI } from '../../services/api.js';
import authService from '../../services/authService.js';

export default {
  name: 'DashboardContent',
  data() {
    return {
      estadisticas: {
        ganado: 0,
        potreros: 0,
        vacunaciones: 0
      },
      userInfo: {
        nombre: '',
        email: ''
      }
    };
  },
  mounted() {
    this.cargarDatosUsuario();
    this.cargarEstadisticas();
  },
  methods: {
    cargarDatosUsuario() {
      const user = authService.getUser();
      if (user && user.persona) {
        this.userInfo.nombre = user.persona.nombre_completo || 'Usuario';
        this.userInfo.email = user.persona.email || '';
      }
    },

    async cargarEstadisticas() {
      try {
        const [ganadoResponse, potreroResponse, vacunacionResponse] = await Promise.all([
          ganadoAPI.getAll(),
          potreroAPI.getAll(),
          vacunacionAPI.getAll()
        ]);

        this.estadisticas.ganado = ganadoResponse.data?.data?.length || 0;
        this.estadisticas.potreros = potreroResponse.data?.data?.length || 0;
        this.estadisticas.vacunaciones = vacunacionResponse.data?.data?.length || 0;
      } catch (error) {
        console.error('Error cargando estadísticas:', error);
        this.estadisticas = {
          ganado: this.estadisticas.ganado || 0,
          potreros: this.estadisticas.potreros || 0,
          vacunaciones: this.estadisticas.vacunaciones || 0
        };
      }
    }
  }
};