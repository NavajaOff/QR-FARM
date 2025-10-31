<template>
  <div class="container-fluid py-4">
    <div class="row">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h2 class="mb-0">
            <i class="fas fa-qrcode me-2 text-primary"></i>Escanear Código QR
          </h2>
        </div>

        <!-- Scanner Section -->
        <div class="card border-0 shadow-sm">
          <div class="card-body p-4">
            <div class="row">
              <div class="col-lg-8">
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

                  <div class="scanner-status mt-3 text-center">
                    <div class="status-indicator">
                      <div class="status-dot" :class="{ 'active': isScanning }"></div>
                      <span class="status-text">{{ isScanning ? 'Escaneando...' : 'Listo para escanear' }}</span>
                    </div>
                  </div>
                </div>

                <!-- Action Buttons -->
                <div class="action-buttons">
                  <div class="row g-3">
                    <div class="col-md-6">
                      <button
                        class="btn btn-primary btn-lg w-100"
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
                        class="btn btn-outline-primary btn-lg w-100"
                        @click="subirImagen"
                        :disabled="isScanning"
                      >
                        <i class="fas fa-upload me-2"></i>Subir Imagen
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <div class="col-lg-4">
                <!-- Instructions -->
                <div class="instructions-section">
                  <div class="alert alert-info border-0">
                    <div class="d-flex align-items-start">
                      <i class="fas fa-lightbulb fa-lg text-info me-3 mt-1"></i>
                      <div>
                        <h6 class="alert-heading fw-bold mb-2">Instrucciones</h6>
                        <ul class="mb-0 small">
                          <li>Asegúrate de tener buena iluminación</li>
                          <li>Mantén el dispositivo estable</li>
                          <li>Coloca el código QR en el marco</li>
                          <li>La información aparecerá automáticamente</li>
                        </ul>
                      </div>
                    </div>
                  </div>

                  <!-- Recent Scans -->
                  <div class="recent-scans-card" v-if="recentScans.length > 0">
                    <h6 class="fw-bold mb-3">
                      <i class="fas fa-history me-2 text-secondary"></i>Escaneos Recientes
                    </h6>
                    <div class="list-group list-group-flush">
                      <div
                        v-for="scan in recentScans"
                        :key="scan.id"
                        class="list-group-item border-0 px-0 py-2"
                      >
                        <div class="d-flex align-items-center">
                          <div class="scan-avatar me-3">
                            <i class="fas fa-cow text-success"></i>
                          </div>
                          <div class="flex-grow-1">
                            <div class="fw-semibold small">{{ scan.nombre }}</div>
                            <small class="text-muted">{{ scan.fecha }}</small>
                          </div>
                          <button class="btn btn-sm btn-outline-primary btn-sm">
                            <i class="fas fa-eye"></i>
                          </button>
                        </div>
                      </div>
                    </div>
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
      </div>
    </div>
  </div>
</template>

<script>
import authService from '../../services/authService.js';

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
              confirmButtonColor: '#28a745'
            });
          }, 2000);
        }
      }
    }
  }
};
</script>

<style scoped>
.scanner-area {
  position: relative;
  margin-bottom: 2rem;
  display: flex;
  justify-content: center;
}

.scanner-frame {
  position: relative;
  width: 300px;
  height: 300px;
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

.action-buttons .btn {
  border-radius: 12px;
  font-weight: 600;
  transition: var(--transition);
  position: relative;
  overflow: hidden;
}

.action-buttons .btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.action-buttons .btn:hover::before {
  left: 100%;
}

.btn-loading {
  pointer-events: none;
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

.recent-scans-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
}

.scan-avatar {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
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

/* Responsive */
@media (max-width: 768px) {
  .scanner-frame {
    width: 250px;
    height: 250px;
  }

  .scanner-corner {
    width: 30px;
    height: 30px;
    border-width: 3px;
  }

  .action-buttons .col-md-6 {
    margin-bottom: 1rem;
  }
}

@media (max-width: 576px) {
  .scanner-frame {
    width: 200px;
    height: 200px;
  }

  .card-body {
    padding: 1.5rem !important;
  }
}
</style>
