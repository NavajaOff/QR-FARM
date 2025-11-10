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
import escanearQrAdmin from '../../assets/js/escanear-qr-admin.js';

export default escanearQrAdmin;
</script>

<style scoped>
@import '../../assets/css/escanear-qr-admin.css';
</style>