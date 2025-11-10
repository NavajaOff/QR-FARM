import authService from '../../services/authService.js';

export default {
  name: "EscanearQRAdmin",
  data() {
    return {
      isScanning: false,
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
    };
  },
  mounted() {
    if (!authService.isAuthenticated() || !authService.isAdmin()) {
      this.$router.push('/login');
      return;
    }
  },
  methods: {
    async iniciarEscaneo() {
      this.isScanning = true;

      try {
        // Simular proceso de escaneo
        await new Promise(resolve => setTimeout(resolve, 2000));

        // Aquí iría la lógica real de escaneo con la cámara
        if (typeof Swal !== 'undefined') {
          Swal.fire({
            title: 'Escaneo completado',
            text: 'Código QR detectado correctamente',
            icon: 'success',
            confirmButtonColor: '#007bff'
          });
        } else {
          alert('Escaneo completado - Código QR detectado');
        }
      } catch (error) {
        console.error('Error en escaneo:', error);
        if (typeof Swal !== 'undefined') {
          Swal.fire({
            title: 'Error',
            text: 'No se pudo completar el escaneo',
            icon: 'error'
          });
        }
      } finally {
        this.isScanning = false;
      }
    },

    subirImagen() {
      this.$refs.fileInput.click();
    },

    handleFileUpload(event) {
      const file = event.target.files[0];
      if (file) {
        // Aquí iría la lógica para procesar la imagen
        console.log('Imagen subida:', file.name);

        if (typeof Swal !== 'undefined') {
          Swal.fire({
            title: 'Procesando imagen',
            text: 'Analizando código QR...',
            allowOutsideClick: false,
            didOpen: () => {
              Swal.showLoading();
            }
          });

          // Simular procesamiento
          setTimeout(() => {
            Swal.fire({
              title: 'Imagen procesada',
              text: 'Código QR encontrado en la imagen',
              icon: 'success',
              confirmButtonColor: '#007bff'
            });
          }, 2000);
        }
      }
    },

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