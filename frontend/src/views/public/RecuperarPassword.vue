<template>
  <div class="recovery-page">
    <div class="card recovery-card">
      <div class="card-body">
        <h3 class="card-title mb-3 text-center">Recuperar contraseña</h3>
        <p class="text-muted text-center mb-4">
          Si olvidaste tu contraseña, ingresa tu email y avisaremos al administrador o superadmin correspondiente.
        </p>

        <form @submit.prevent="solicitarToken" class="mb-4">
          <div class="mb-3">
            <label class="form-label">Email registrado</label>
            <input v-model="emailRequest" type="email" class="form-control" placeholder="usuario@empresa.com" required />
          </div>
          <button type="submit" class="btn btn-primary w-100" :disabled="requestLoading">
            <span v-if="requestLoading" class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>
            Solicitar token
          </button>
          <p v-if="requestMessage" class="form-text text-success mt-2">{{ requestMessage }}</p>
          <p v-if="requestError" class="form-text text-danger mt-2">{{ requestError }}</p>
        </form>

        <hr />

        <form @submit.prevent="confirmarToken">
          <div class="mb-3">
            <label class="form-label">Token recibido</label>
            <input v-model="token" class="form-control" placeholder="Código que llegó al administrador" required />
          </div>
          <div class="mb-3">
            <label class="form-label">Nueva contraseña</label>
            <input v-model="password" type="password" class="form-control" placeholder="Nueva contraseña" required minlength="6" />
          </div>
          <div class="mb-3">
            <label class="form-label">Confirmar contraseña</label>
            <input v-model="passwordConfirm" type="password" class="form-control" placeholder="Repetir contraseña" required minlength="6" />
          </div>
          <button type="submit" class="btn btn-outline-success w-100" :disabled="confirmLoading">
            <span v-if="confirmLoading" class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>
            Confirmar cambio
          </button>
          <p v-if="confirmMessage" class="form-text text-success mt-2">{{ confirmMessage }}</p>
          <p v-if="confirmError" class="form-text text-danger mt-2">{{ confirmError }}</p>
        </form>

        <div class="text-end mt-3">
          <router-link to="/login" class="text-decoration-none">Volver al login</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import Swal from 'sweetalert2';
import { recoveryAPI } from '@/services/api.js';

const emailRequest = ref('');
const requestLoading = ref(false);
const requestMessage = ref('');
const requestError = ref('');

const token = ref('');
const password = ref('');
const passwordConfirm = ref('');
const confirmLoading = ref(false);
const confirmMessage = ref('');
const confirmError = ref('');

const validatePasswordConfirmation = () => {
  return password.value === passwordConfirm.value;
};

const solicitarToken = async () => {
  if (!emailRequest.value) {
    requestError.value = 'Ingresa un email válido';
    return;
  }
  requestLoading.value = true;
  requestError.value = '';
  requestMessage.value = '';

  try {
    await recoveryAPI.request(emailRequest.value);
    requestMessage.value = 'Se envió el token. Pídelo a tu administrador.';
  } catch (error) {
    requestError.value = error.response?.data?.message || 'No se pudo generar el token.';
  } finally {
    requestLoading.value = false;
  }
};

const confirmarToken = async () => {
  if (!validatePasswordConfirmation()) {
    confirmError.value = 'Las contraseñas deben coincidir';
    return;
  }
  confirmLoading.value = true;
  confirmError.value = '';
  confirmMessage.value = '';

  try {
    await recoveryAPI.confirm({
      token: token.value,
      password: password.value
    });
    confirmMessage.value = 'Contraseña actualizada correctamente.';
    await Swal.fire({
      icon: 'success',
      title: 'Contraseña actualizada',
      text: 'Puedes iniciar sesión con tu nueva contraseña',
      timer: 1900,
      showConfirmButton: false
    });
  } catch (error) {
    confirmError.value = error.response?.data?.message || 'Error al confirmar el token.';
  } finally {
    confirmLoading.value = false;
  }
};
</script>

<style scoped>
.recovery-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #e9f7ff 0%, #f7faff 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.recovery-card {
  width: 100%;
  max-width: 520px;
  border-radius: 1rem;
  box-shadow: 0 20px 40px rgba(15, 23, 42, 0.15);
}

@media (max-width: 575px) {
  .recovery-page {
    padding: 1rem;
  }
}
</style>

