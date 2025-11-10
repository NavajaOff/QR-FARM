import { ganadoAPI, potreroAPI, userAPI } from '../../services/api.js';

const secureRandomInt = (min, max) => {
  const lower = Number(min);
  const upper = Number(max);
  if (!Number.isFinite(lower) || !Number.isFinite(upper) || lower > upper) {
    return lower;
  }

  if (typeof window !== 'undefined' && window.crypto?.getRandomValues) {
    const range = upper - lower + 1;
    const buffer = new Uint32Array(1);
    window.crypto.getRandomValues(buffer);
    const randomFraction = buffer[0] / 0x100000000;
    return lower + Math.floor(randomFraction * range);
  }

  return lower;
};

export default {
  name: 'DashboardContent',
  data() {
    return {
      estadisticas: {
        usuarios: 0,
        ganado: 0,
        potreros: 0,
        salud: 0
      }
    };
  },
  mounted() {
    this.cargarEstadisticas();
  },
  methods: {
    async cargarEstadisticas() {
      try {
        // Cargar estadísticas de usuarios (con manejo de errores)
        try {
          const usuariosResponse = await userAPI.getAll();
          this.estadisticas.usuarios = usuariosResponse.data?.data?.length || 0;
        } catch (userError) {
          console.warn('Error cargando usuarios, usando valor por defecto:', userError);
          this.estadisticas.usuarios = 1; // Usuario admin por defecto
        }

        // Cargar estadísticas de ganado
        try {
          const ganadoResponse = await ganadoAPI.getAll();
          this.estadisticas.ganado = ganadoResponse.data?.data?.length || 0;
        } catch (ganadoError) {
          console.warn('Error cargando ganado, usando valor por defecto:', ganadoError);
          this.estadisticas.ganado = 0;
        }

        // Cargar estadísticas de potreros
        try {
          const potrerosResponse = await potreroAPI.getAll();
          this.estadisticas.potreros = potrerosResponse.data?.data?.length || 0;
        } catch (potreroError) {
          console.warn('Error cargando potreros, usando valor por defecto:', potreroError);
          this.estadisticas.potreros = 0;
        }

        // Salud promedio simulada
        this.estadisticas.salud = secureRandomInt(80, 99);
      } catch (error) {
        console.error('Error general cargando estadísticas:', error);
        // En caso de error general, mostrar valores por defecto
        this.estadisticas = {
          usuarios: 1,
          ganado: 0,
          potreros: 0,
          salud: 85
        };
      }
    }
  }
};