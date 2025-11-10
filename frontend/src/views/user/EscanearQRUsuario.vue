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
import escanearQrUsuario from '../../assets/js/escanear-qr-usuario.js';

export default escanearQrUsuario;
</script>

<style scoped>
@import '../../assets/css/escanear-qr-usuario.css';
</style>
