import authService from '../../services/authService.js';

const defaultConfig = {
  authorize: service => service.isAuthenticated(),
  onAuthorized: null,
  successButtonColor: '#28a745',
  recentScans: [],
  defaultUserName: 'Usuario',
  estadisticas: null
};

function getConfig(vm) {
  return vm.$options.escanearQRConfig || {};
}

export const escanearQRBase = {
  data() {
    const config = getConfig(this);
    return {
      isScanning: false,
      userName: config.defaultUserName || defaultConfig.defaultUserName,
      recentScans: Array.isArray(config.recentScans) ? [...config.recentScans] : [...defaultConfig.recentScans],
      estadisticas: config.estadisticas ? { ...config.estadisticas } : defaultConfig.estadisticas
    };
  },

  mounted() {
    const config = getConfig(this);
    const authorize = config.authorize || defaultConfig.authorize;

    if (!authorize(authService)) {
      this.$router.push('/login');
      return;
    }

    if (typeof config.onAuthorized === 'function') {
      config.onAuthorized.call(this, authService);
    }
  },

  methods: {
    async iniciarEscaneo() {
      this.isScanning = true;
      const config = getConfig(this);
      const successColor = config.successButtonColor || defaultConfig.successButtonColor;

      try {
        await new Promise(resolve => setTimeout(resolve, 2000));

        if (typeof Swal === 'undefined') {
          alert('Escaneo completado - Código QR detectado');
        } else {
          Swal.fire({
            title: 'Escaneo completado',
            text: 'Código QR detectado correctamente',
            icon: 'success',
            confirmButtonColor: successColor
          });
        }
      } catch (error) {
        console.error('Error en escaneo:', error);
        if (typeof Swal === 'undefined') {
          console.error('No se pudo completar el escaneo');
        } else {
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
      if (this.$refs?.fileInput) {
        this.$refs.fileInput.click();
      }
    },

    handleFileUpload(event) {
      const file = event?.target?.files ? event.target.files[0] : null;
      if (!file) return;

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

        const config = getConfig(this);
        const successColor = config.successButtonColor || defaultConfig.successButtonColor;

        setTimeout(() => {
          Swal.fire({
            title: 'Imagen procesada',
            text: 'Código QR encontrado en la imagen',
            icon: 'success',
            confirmButtonColor: successColor
          });
        }, 2000);
      }
    }
  }
};

