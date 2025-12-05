import { ganadoAPI, potreroAPI, vacunacionAPI } from '../../services/api.js';
import authService from '../../services/authService.js';

/**
 * Componente DashboardContent para usuarios
 * Maneja la lógica del dashboard de usuarios
 */
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
    /**
     * Carga los datos del usuario actual
     */
    cargarDatosUsuario() {
      const user = authService.getUser();
      if (user?.persona) {
        this.userInfo.nombre = user.persona.nombre_completo || 'Usuario';
        this.userInfo.email = user.persona.email || '';
      }
    },

    /**
     * Carga las estadísticas del usuario
     */
    async cargarEstadisticas() {
      try {
        const [ganadoResponse, potreroResponse, vacunacionResponse] = await Promise.all([
          ganadoAPI.getAll(),
          potreroAPI.getAll(),
          vacunacionAPI.getAll()
        ]);

        // Helper function to extract data from API response
        const extractDataFromResponse = (response, checkSuccess = false) => {
          if (!response?.data) return [];
          const data = response.data;
          if (checkSuccess && data.success && Array.isArray(data.data)) {
            return data.data;
          }
          if (data.status === 'success' && Array.isArray(data.data)) {
            return data.data;
          }
          if (Array.isArray(data.data)) {
            return data.data;
          }
          return [];
        };

        // Ganado: formato {status: 'success', data: [...]}
        const ganadoData = extractDataFromResponse(ganadoResponse);
        this.estadisticas.ganado = ganadoData.length || 0;

        // Potreros: formato {data: [...], success: True} o {status: 'success', data: [...]}
        const potrerosData = extractDataFromResponse(potreroResponse, true);
        this.estadisticas.potreros = potrerosData.length || 0;

        // Vacunaciones: formato {status: 'success', data: [...]}
        const vacunacionesData = extractDataFromResponse(vacunacionResponse);
        this.estadisticas.vacunaciones = vacunacionesData.length || 0;
      } catch (error) {
        console.error('[DashboardContent] Error cargando estadísticas:', error);
        console.error('[DashboardContent] Detalles del error:', {
          message: error.message,
          response: error.response?.data,
          status: error.response?.status
        });
        // Mantener valores por defecto en caso de error
        this.estadisticas = {
          ganado: this.estadisticas.ganado || 0,
          potreros: this.estadisticas.potreros || 0,
          vacunaciones: this.estadisticas.vacunaciones || 0
        };
      }
    }
  }
};