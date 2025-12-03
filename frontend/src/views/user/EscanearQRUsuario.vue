<template>
  <section class="scan-page">
    <QrScanner
      role="user"
      resource-endpoint="/ganado/{id}"
      @resource-loaded="handleResourceLoaded"
      @error="handleScannerError"
      @action="forwardAction"
    />
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import QrScanner from '../../components/QrScanner.vue';
import type { QrResourceResponse } from '../../services/qr';

const lastResourceId = ref<string>('');

const handleResourceLoaded = (resource: QrResourceResponse): void => {
  lastResourceId.value = resource.id;
  console.debug('[USER QR] Recurso cargado', resource);
};

const handleScannerError = (message: string): void => {
  console.debug('[USER QR] Error recibido', message);
};

const forwardAction = (action: string): void => {
  console.debug('[USER QR] Acción emitida', action, lastResourceId.value);
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
