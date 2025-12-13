<template>
  <div class="container-fluid py-4">
    <div class="row">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h2 class="mb-0">
            <i class="fas fa-key me-2"></i>
            Solicitudes de Recuperación de Contraseña
          </h2>
          <button class="btn btn-outline-primary" @click="refreshRequests">
            <i class="fas fa-sync-alt me-2"></i>
            Actualizar
          </button>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Cargando...</span>
          </div>
          <p class="mt-2">Cargando solicitudes...</p>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="alert alert-danger" role="alert">
          <i class="fas fa-exclamation-triangle me-2"></i>
          {{ error }}
        </div>

        <!-- Empty State -->
        <div v-else-if="requests.length === 0" class="alert alert-info" role="alert">
          <i class="fas fa-info-circle me-2"></i>
          No hay solicitudes de recuperación pendientes.
        </div>

        <!-- Requests List -->
        <div v-else class="row g-4">
          <div
            v-for="request in requests"
            :key="request.id"
            class="col-12 col-md-6 col-lg-4"
          >
            <div class="card shadow-sm h-100">
              <div class="card-header bg-primary text-white">
                <div class="d-flex justify-content-between align-items-center">
                  <h6 class="mb-0">
                    <i class="fas fa-user me-2"></i>
                    Solicitud #{{ request.id }}
                  </h6>
                  <span class="badge bg-light text-dark">
                    {{ request.tipo === 'admin' ? 'Admin' : 'Usuario' }}
                  </span>
                </div>
              </div>
              <div class="card-body">
                <div class="mb-3">
                  <strong>Usuario:</strong>
                  <p class="mb-0">{{ request.usuario_nombre || request.solicitante_email || 'Desconocido' }}</p>
                  <small class="text-muted">{{ request.usuario_email || request.solicitante_email }}</small>
                </div>
                <div class="mb-3">
                  <strong>Rol:</strong>
                  <p class="mb-0">{{ request.usuario_rol || 'N/A' }}</p>
                </div>
                <div class="mb-3">
                  <strong>Fecha de solicitud:</strong>
                  <p class="mb-0">{{ formatDate(request.created_at) }}</p>
                </div>
              </div>
              <div class="card-footer bg-light">
                <div class="d-flex gap-2">
                  <button
                    class="btn btn-success btn-sm flex-fill"
                    @click="approveRequest(request.id)"
                    :disabled="processing === request.id"
                  >
                    <i class="fas fa-check me-1"></i>
                    <span v-if="processing === request.id">Procesando...</span>
                    <span v-else>Aprobar</span>
                  </button>
                  <button
                    class="btn btn-danger btn-sm flex-fill"
                    @click="rejectRequest(request.id)"
                    :disabled="processing === request.id"
                  >
                    <i class="fas fa-times me-1"></i>
                    <span v-if="processing === request.id">Procesando...</span>
                    <span v-else>Rechazar</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Token Modal (when approved) -->
    <div
      v-if="showTokenModal"
      class="modal fade show d-block"
      tabindex="-1"
      style="background-color: rgba(0,0,0,0.5);"
      @click.self="closeTokenModal"
    >
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header bg-success text-white">
            <h5 class="modal-title">
              <i class="fas fa-check-circle me-2"></i>
              Solicitud Aprobada
            </h5>
            <button type="button" class="btn-close btn-close-white" @click="closeTokenModal"></button>
          </div>
          <div class="modal-body">
            <p class="mb-3">La solicitud ha sido aprobada. Se ha generado un token de recuperación:</p>
            <div class="alert alert-warning">
              <strong>Token:</strong>
              <code class="d-block mt-2 p-2 bg-light rounded">{{ approvedToken }}</code>
            </div>
            <p class="text-muted small mb-0">
              <i class="fas fa-info-circle me-1"></i>
              El token expira en 30 minutos. Comparte este token con el usuario para que pueda cambiar su contraseña.
            </p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeTokenModal">Cerrar</button>
            <button type="button" class="btn btn-primary" @click="copyToken">
              <i class="fas fa-copy me-1"></i>
              Copiar Token
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { recoveryAPI } from '../../services/api.js';
import Swal from 'sweetalert2';

export default {
  name: 'GestionarRecuperaciones',
  data() {
    return {
      requests: [],
      loading: false,
      error: null,
      processing: null,
      showTokenModal: false,
      approvedToken: ''
    };
  },
  mounted() {
    this.loadRequests();
  },
  methods: {
    async loadRequests() {
      this.loading = true;
      this.error = null;
      try {
        const response = await recoveryAPI.listRequests();
        if (response.data?.status === 'success') {
          this.requests = response.data.data || [];
        } else {
          this.error = 'Error al cargar las solicitudes';
        }
      } catch (error) {
        console.error('Error loading recovery requests:', error);
        this.error = error.response?.data?.message || 'Error al cargar las solicitudes';
      } finally {
        this.loading = false;
      }
    },
    async approveRequest(recoveryId) {
      const result = await Swal.fire({
        title: '¿Aprobar solicitud?',
        text: 'Se generará un token de recuperación y se enviará al usuario.',
        icon: 'question',
        showCancelButton: true,
        confirmButtonColor: '#28a745',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Sí, aprobar',
        cancelButtonText: 'Cancelar'
      });

      if (!result.isConfirmed) return;

      this.processing = recoveryId;
      try {
        const response = await recoveryAPI.approve(recoveryId);
        if (response.data?.status === 'success') {
          this.approvedToken = response.data.token || '';
          this.showTokenModal = true;
          await this.loadRequests();
          Swal.fire({
            icon: 'success',
            title: 'Solicitud aprobada',
            text: 'El token ha sido generado. Compártelo con el usuario.',
            timer: 2000,
            showConfirmButton: false
          });
        } else {
          throw new Error(response.data?.message || 'Error al aprobar la solicitud');
        }
      } catch (error) {
        console.error('Error approving request:', error);
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: error.response?.data?.message || 'Error al aprobar la solicitud'
        });
      } finally {
        this.processing = null;
      }
    },
    async rejectRequest(recoveryId) {
      const result = await Swal.fire({
        title: '¿Rechazar solicitud?',
        text: 'Esta acción no se puede deshacer.',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#dc3545',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Sí, rechazar',
        cancelButtonText: 'Cancelar'
      });

      if (!result.isConfirmed) return;

      this.processing = recoveryId;
      try {
        const response = await recoveryAPI.reject(recoveryId);
        if (response.data?.status === 'success') {
          await this.loadRequests();
          Swal.fire({
            icon: 'success',
            title: 'Solicitud rechazada',
            timer: 2000,
            showConfirmButton: false
          });
        } else {
          throw new Error(response.data?.message || 'Error al rechazar la solicitud');
        }
      } catch (error) {
        console.error('Error rejecting request:', error);
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: error.response?.data?.message || 'Error al rechazar la solicitud'
        });
      } finally {
        this.processing = null;
      }
    },
    refreshRequests() {
      this.loadRequests();
    },
    formatDate(dateString) {
      if (!dateString) return 'Fecha desconocida';
      try {
        const date = new Date(dateString);
        return date.toLocaleDateString('es-ES', {
          day: '2-digit',
          month: 'short',
          year: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        });
      } catch (error) {
        return dateString;
      }
    },
    closeTokenModal() {
      this.showTokenModal = false;
      this.approvedToken = '';
    },
    async copyToken() {
      try {
        await navigator.clipboard.writeText(this.approvedToken);
        Swal.fire({
          icon: 'success',
          title: 'Token copiado',
          timer: 1500,
          showConfirmButton: false
        });
      } catch (error) {
        console.error('Error copying token:', error);
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'No se pudo copiar el token'
        });
      }
    }
  }
};
</script>

<style scoped>
.card {
  transition: transform 0.2s, box-shadow 0.2s;
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
}

.modal.show {
  display: block;
}

code {
  font-size: 0.9rem;
  word-break: break-all;
}
</style>

