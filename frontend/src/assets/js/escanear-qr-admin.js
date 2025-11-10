import { escanearQRBase } from './escanear-qr-base.js';

const { methods, ...baseOptions } = escanearQRBase;

export default {
  ...baseOptions,
  name: 'EscanearQRAdmin',
  escanearQRConfig: {
    authorize: service => service.isAuthenticated() && service.isAdmin(),
    successButtonColor: '#007bff',
    recentScans: [
      { id: 1, nombre: 'Rosita', fecha: '2025-10-31 10:30' },
      { id: 2, nombre: 'Luna', fecha: '2025-10-30 15:45' },
      { id: 3, nombre: 'Bella', fecha: '2025-10-30 12:20' }
    ],
    estadisticas: {
      totalEscaneos: 24,
      animalesUnicos: 18,
      tasaExito: 96,
      tiempoPromedio: 2.3
    }
  },
  methods: {
    ...methods,
    verTodosAnimales() {
      this.$router.push('/admin/gestionar-animales');
    },

    generarReporte() {
      if (typeof Swal !== 'undefined') {
        Swal.fire({
          title: 'Generando reporte',
          text: 'El reporte se está generando...',
          allowOutsideClick: false,
          didOpen: () => {
            Swal.showLoading();
          }
        });

        setTimeout(() => {
          Swal.fire({
            title: 'Reporte generado',
            text: 'El reporte ha sido generado exitosamente',
            icon: 'success',
            confirmButtonColor: '#007bff'
          });
        }, 1500);
      }
    },

    exportarDatos() {
      if (typeof Swal !== 'undefined') {
        Swal.fire({
          title: 'Exportando datos',
          text: 'Los datos se están exportando...',
          allowOutsideClick: false,
          didOpen: () => {
            Swal.showLoading();
          }
        });

        setTimeout(() => {
          Swal.fire({
            title: 'Exportación completada',
            text: 'Los datos han sido exportados exitosamente',
            icon: 'success',
            confirmButtonColor: '#007bff'
          });
        }, 2000);
      }
    }
  }
};