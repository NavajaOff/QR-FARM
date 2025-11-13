<template>
  <section class="scan-page">
    <QrScanner
      role="admin"
      resource-endpoint="/ganado/{id}"
      @resource-loaded="handleResourceLoaded"
      @error="handleScannerError"
      @action="forwardAction"
    />
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import QrScanner from '../../components/QrScanner.vue';
import type { QrResourceResponse } from '../../services/qr';

const router = useRouter();
const lastResourceId = ref<string>('');

const handleResourceLoaded = (resource: QrResourceResponse): void => {
  lastResourceId.value = resource.id;
  console.debug('[ADMIN QR] Recurso cargado', resource);
};

const handleScannerError = (message: string): void => {
  console.debug('[ADMIN QR] Error recibido', message);
};

const forwardAction = (action: string): void => {
  if (action === 'ver-historial' && lastResourceId.value) {
    router.push({ name: 'GestionarAnimalesAdmin', query: { seleccionado: lastResourceId.value } });
    return;
  }

  if (action === 'editar' && lastResourceId.value) {
    router.push({ name: 'GestionarAnimalesAdmin', query: { editar: lastResourceId.value } });
    return;
  }

  if (action === 'descargar-ficha' && lastResourceId.value) {
    console.debug('[ADMIN QR] Solicitud de descarga de ficha', lastResourceId.value);
    return;
  }

  console.debug('[ADMIN QR] Acción emitida', action);
};
</script>

<style scoped>
.scan-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 1rem 0;
}
</style>