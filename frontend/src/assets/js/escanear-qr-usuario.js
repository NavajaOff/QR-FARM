import { escanearQRBase } from './escanear-qr-base.js';

const { methods, ...baseOptions } = escanearQRBase;

export default {
  ...baseOptions,
  name: 'EscanearQR',
  escanearQRConfig: {
    authorize: service => service.isAuthenticated() && service.isUser(),
    onAuthorized(authService) {
      const user = authService.getUser();
      this.userName = user?.persona?.primer_nombre || 'Usuario';
    },
    successButtonColor: '#28a745',
    recentScans: [
      { id: 1, nombre: 'Rosita', fecha: '2025-10-31 10:30' },
      { id: 2, nombre: 'Luna', fecha: '2025-10-30 15:45' }
    ]
  },
  methods: {
    ...methods
  }
};