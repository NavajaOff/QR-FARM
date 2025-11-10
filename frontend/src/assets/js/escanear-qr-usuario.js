import authService from '../../services/authService.js';

/**
 * Componente EscanearQR para usuarios
 * Maneja la lógica de escaneo de códigos QR
 */
export default {
  name: "EscanearQR",
  data() {
    return {
      isScanning: false,
      userName: 'Usuario',
      recentScans: [
        { id: 1, nombre: 'Rosita', fecha: '2025-10-31 10:30' },
        { id: 2, nombre: 'Luna', fecha: '2025-10-30 15:45' }
      ]
    };
  },
  mounted() {
    if (!authService.isAuthenticated() || !authService.isUser()) {
      this.$router.push('/login');
      return;
    }

    const user = authService.getUser();
    this.userName = user?.persona?.primer_nombre || 'Usuario';
  },
  methods: {
    /**
     * Inicia el proceso de escaneo de QR
     */
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
            confirmButtonColor: '#28a745'
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

    /**
     * Abre el selector de archivos para subir imagen
     */
    subirImagen() {
      this.$refs.fileInput.click();
    },

    /**
     * Maneja la subida de archivos de imagen
     * @param {Event} event - Evento de cambio del input file
     */
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
              confirmButtonColor: '#28a745'
            });
          }, 2000);
        }
      }
    }
  }
};