<template>
  <div class="qr-scanner-container">
    <div class="container-fluid py-4">
      <div class="row justify-content-center">
        <div class="col-12 col-lg-10 col-xl-8">

          <!-- Header Section -->
          <div class="text-center mb-5">
            <div class="qr-header-icon mb-3">
              <i class="fas fa-qrcode fa-4x text-primary"></i>
            </div>
            <h1 class="display-5 fw-bold text-dark mb-2">Escanear Código QR</h1>
            <p class="lead text-muted">Escanea códigos QR para acceder rápidamente a la información del ganado</p>
          </div>

          <!-- Scanner Card -->
          <div class="card qr-scanner-card border-0 shadow-lg">
            <div class="card-body p-4 p-lg-5">

              <!-- Scanner Area -->
              <div class="scanner-area mb-4">
                <div class="scanner-frame">
                  <div class="scanner-overlay">
                    <div class="scanner-corner top-left"></div>
                    <div class="scanner-corner top-right"></div>
                    <div class="scanner-corner bottom-left"></div>
                    <div class="scanner-corner bottom-right"></div>

                    <div class="scanner-center">
                      <div class="scanner-pulse"></div>
                      <i class="fas fa-qrcode fa-3x text-primary scanner-icon"></i>
                    </div>
                  </div>
                </div>

                <div class="scanner-status mt-3">
                  <div class="status-indicator">
                    <div class="status-dot" :class="{ 'active': isScanning }"></div>
                    <span class="status-text">{{ isScanning ? 'Escaneando...' : 'Listo para escanear' }}</span>
                  </div>
                </div>
              </div>

              <!-- Action Buttons -->
              <div class="action-buttons mb-4">
                <div class="row g-3">
                  <div class="col-md-6">
                    <button
                      class="btn btn-primary btn-lg w-100 action-btn"
                      :class="{ 'btn-loading': isScanning }"
                      @click="iniciarEscaneo"
                      :disabled="isScanning"
                    >
                      <i class="fas fa-play me-2" v-if="!isScanning"></i>
                      <i class="fas fa-spinner fa-spin me-2" v-else></i>
                      {{ isScanning ? 'Escaneando...' : 'Iniciar Escaneo' }}
                    </button>
                  </div>
                  <div class="col-md-6">
                    <button
                      class="btn btn-outline-primary btn-lg w-100 action-btn"
                      @click="subirImagen"
                      :disabled="isScanning"
                    >
                      <i class="fas fa-upload me-2"></i>Subir Imagen
                    </button>
                  </div>
                </div>
              </div>

              <!-- Quick Actions for Admin -->
              <div class="admin-actions mb-4">
                <div class="row g-3">
                  <div class="col-md-4">
                    <button class="btn btn-success btn-lg w-100" @click="verTodosAnimales">
                      <i class="fas fa-list me-2"></i>Ver Todos
                    </button>
                  </div>
                  <div class="col-md-4">
                    <button class="btn btn-info btn-lg w-100" @click="generarReporte">
                      <i class="fas fa-chart-bar me-2"></i>Reporte
                    </button>
                  </div>
                  <div class="col-md-4">
                    <button class="btn btn-warning btn-lg w-100" @click="exportarDatos">
                      <i class="fas fa-download me-2"></i>Exportar
                    </button>
                  </div>
                </div>
              </div>

              <!-- Instructions -->
              <div class="instructions-section">
                <div class="alert alert-info border-0 shadow-sm">
                  <div class="d-flex align-items-start">
                    <i class="fas fa-lightbulb fa-lg text-info me-3 mt-1"></i>
                    <div>
                      <h6 class="alert-heading fw-bold mb-2">Instrucciones para administradores</h6>
                      <ul class="mb-0 text-sm">
                        <li>Utiliza el escáner para acceso rápido a información detallada</li>
                        <li>Los códigos QR permiten modificar datos del ganado directamente</li>
                        <li>Revisa el historial de vacunaciones y tratamientos</li>
                        <li>Genera reportes automáticos desde cualquier escaneo</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Hidden File Input -->
              <input
                type="file"
                ref="fileInput"
                @change="handleFileUpload"
                accept="image/*"
                style="display: none"
              />

            </div>
          </div>

          <!-- Recent Scans and Stats -->
          <div class="row mt-4">
            <div class="col-md-6">
              <div class="card recent-scans-card border-0 shadow-sm h-100">
                <div class="card-header bg-light border-0">
                  <h5 class="mb-0 fw-bold">
                    <i class="fas fa-history me-2 text-secondary"></i>Escaneos Recientes
                  </h5>
                </div>
                <div class="card-body">
                  <div class="list-group list-group-flush">
                    <div
                      v-for="scan in recentScans"
                      :key="scan.id"
                      class="list-group-item border-0 px-0"
                    >
                      <div class="d-flex align-items-center">
                        <div class="scan-avatar me-3">
                          <i class="fas fa-cow text-success"></i>
                        </div>
                        <div class="flex-grow-1">
                          <h6 class="mb-1">{{ scan.nombre }}</h6>
                          <small class="text-muted">{{ scan.fecha }}</small>
                        </div>
                        <button class="btn btn-sm btn-outline-primary">
                          <i class="fas fa-edit me-1"></i>Editar
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="col-md-6">
              <div class="card stats-card border-0 shadow-sm h-100">
                <div class="card-header bg-light border-0">
                  <h5 class="mb-0 fw-bold">
                    <i class="fas fa-chart-pie me-2 text-secondary"></i>Estadísticas
                  </h5>
                </div>
                <div class="card-body">
                  <div class="row g-3">
                    <div class="col-6">
                      <div class="stat-item text-center">
                        <div class="stat-number">{{ estadisticas.totalEscaneos }}</div>
                        <div class="stat-label">Escaneos Hoy</div>
                      </div>
                    </div>
                    <div class="col-6">
                      <div class="stat-item text-center">
                        <div class="stat-number">{{ estadisticas.animalesUnicos }}</div>
                        <div class="stat-label">Animales Únicos</div>
                      </div>
                    </div>
                    <div class="col-6">
                      <div class="stat-item text-center">
                        <div class="stat-number">{{ estadisticas.tasaExito }}%</div>
                        <div class="stat-label">Tasa de Éxito</div>
                      </div>
                    </div>
                    <div class="col-6">
                      <div class="stat-item text-center">
                        <div class="stat-number">{{ estadisticas.tiempoPromedio }}s</div>
                        <div class="stat-label">Tiempo Promedio</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>

<script>
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
</script>

<style scoped>
.qr-scanner-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  padding: 2rem 0;
}

.qr-header-icon {
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
}

.qr-scanner-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: var(--border-radius-lg);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.scanner-area {
  position: relative;
  margin-bottom: 2rem;
}

.scanner-frame {
  position: relative;
  width: 300px;
  height: 300px;
  margin: 0 auto;
  background: #000;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.scanner-overlay {
  position: relative;
  width: 100%;
  height: 100%;
  background: linear-gradient(45deg, transparent 40%, rgba(0, 123, 255, 0.1) 50%, transparent 60%);
}

.scanner-corner {
  position: absolute;
  width: 40px;
  height: 40px;
  border: 4px solid #007bff;
}

.top-left {
  top: 0;
  left: 0;
  border-right: none;
  border-bottom: none;
  border-top-left-radius: 20px;
}

.top-right {
  top: 0;
  right: 0;
  border-left: none;
  border-bottom: none;
  border-top-right-radius: 20px;
}

.bottom-left {
  bottom: 0;
  left: 0;
  border-right: none;
  border-top: none;
  border-bottom-left-radius: 20px;
}

.bottom-right {
  bottom: 0;
  right: 0;
  border-left: none;
  border-top: none;
  border-bottom-right-radius: 20px;
}

.scanner-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.scanner-pulse {
  position: absolute;
  top: -10px;
  left: -10px;
  right: -10px;
  bottom: -10px;
  border: 2px solid #007bff;
  border-radius: 50%;
  animation: pulse 2s infinite;
  opacity: 0;
}

@keyframes pulse {
  0% { transform: scale(0.8); opacity: 1; }
  100% { transform: scale(1.2); opacity: 0; }
}

.scanner-icon {
  animation: scan 3s ease-in-out infinite;
}

@keyframes scan {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.scanner-status {
  text-align: center;
}

.status-indicator {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 50px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.status-dot {
  width: 8px;
  height: 8px;
  background: #6c757d;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.status-dot.active {
  background: #28a745;
  box-shadow: 0 0 10px rgba(40, 167, 69, 0.5);
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0.5; }
}

.status-text {
  font-weight: 500;
  color: #495057;
}

.action-buttons .btn, .admin-actions .btn {
  border-radius: 12px;
  font-weight: 600;
  transition: var(--transition);
  position: relative;
  overflow: hidden;
}

.action-buttons .btn::before, .admin-actions .btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.action-buttons .btn:hover::before, .admin-actions .btn:hover::before {
  left: 100%;
}

.btn-loading {
  pointer-events: none;
}

.admin-actions {
  margin-bottom: 2rem;
}

.instructions-section .alert {
  background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
  border-left: 4px solid #17a2b8;
}

.instructions-section .alert i {
  color: #17a2b8;
}

.instructions-section ul li {
  margin-bottom: 0.25rem;
  color: #0c5460;
}

.recent-scans-card, .stats-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
}

.scan-avatar {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.2rem;
}

.list-group-item {
  transition: var(--transition);
}

.list-group-item:hover {
  background-color: #f8f9fa;
  transform: translateX(5px);
}

.stat-item {
  padding: 1rem;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: var(--border-radius);
  margin-bottom: 1rem;
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  color: #007bff;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.875rem;
  color: #6c757d;
  font-weight: 500;
}

/* Responsive */
@media (max-width: 768px) {
  .qr-scanner-container {
    padding: 1rem 0;
  }

  .scanner-frame {
    width: 250px;
    height: 250px;
  }

  .scanner-corner {
    width: 30px;
    height: 30px;
    border-width: 3px;
  }

  .action-buttons .col-md-6, .admin-actions .col-md-4 {
    margin-bottom: 1rem;
  }

  .display-5 {
    font-size: 2rem;
  }

  .row.mt-4 .col-md-6 {
    margin-bottom: 1.5rem;
  }
}

@media (max-width: 576px) {
  .scanner-frame {
    width: 200px;
    height: 200px;
  }

  .qr-header-icon .fa-4x {
    font-size: 3rem !important;
  }

  .card-body {
    padding: 1.5rem !important;
  }

  .stat-number {
    font-size: 1.5rem;
  }
}
</style>