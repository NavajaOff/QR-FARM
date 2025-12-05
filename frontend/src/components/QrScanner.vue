<template>
  <section class="qr-wrapper">
    <header class="qr-header">
      <div class="qr-header__texts">
        <h1 class="qr-header__title">
          <span aria-hidden="true">📷</span>
          <span>{{ headerTitle }}</span>
        </h1>
        <p class="qr-header__subtitle">{{ headerSubtitle }}</p>
      </div>
      <div class="qr-header__role">
        <span class="qr-badge" :data-role="roleLabel">{{ roleLabel }}</span>
      </div>
    </header>

    <div class="qr-layout">
      <section class="qr-panel qr-panel--scanner">
        <section class="qr-video" aria-live="polite" aria-label="Vista previa de la cámara">
          <div :id="videoElementId" class="qr-video__viewport"></div>
          <p class="qr-status" :data-status="scannerStatus">{{ scannerStatusLabel }}</p>
        </section>

        <div class="qr-camera-select">
          <label class="qr-camera-select__label" for="qr-camera-options">Selecciona una cámara</label>
          <select
            id="qr-camera-options"
            class="qr-camera-select__input"
            :value="state.selectedCameraId"
            @change="handleCameraChange"
            :disabled="state.isScanning"
          >
            <option disabled value="">Selecciona una cámara</option>
            <option
              v-for="camera in state.availableCameras"
              :key="camera.id"
              :value="camera.id"
            >
              {{ camera.label }}
            </option>
          </select>
          <p v-if="state.availableCameras.length === 0" class="qr-camera-select__error">
            No se detectaron cámaras. Verifica los permisos del navegador.
          </p>
        </div>

        <div class="qr-actions" aria-label="Controles de escaneo">
          <button
            type="button"
            class="qr-btn qr-btn--primary"
            @click="handleStartScan"
            :disabled="state.isScanning || !state.selectedCameraId"
          >
            {{ state.isScanning ? 'Escaneando...' : 'Iniciar escaneo' }}
          </button>
          <button
            type="button"
            class="qr-btn"
            @click="togglePause"
            :disabled="!state.isScanning"
          >
            {{ state.isPaused ? 'Continuar' : 'Pausar' }}
          </button>
          <button
            type="button"
            class="qr-btn"
            @click="handleStopScan"
            :disabled="!state.isScanning"
          >
            Cerrar cámara
          </button>
          <button type="button" class="qr-btn" @click="openFileDialog">
            Subir imagen (fallback)
          </button>
        </div>

        <input
          ref="fileInputRef"
          type="file"
          accept="image/*"
          class="qr-file-input"
          @change="handleFileInput"
        />

        <div v-if="state.lastError" class="qr-alert qr-alert--error" role="alert">
          {{ state.lastError }}
        </div>

        <div v-if="state.telemetryMessages.length > 0" class="qr-telemetry">
          <p class="qr-telemetry__title">Registro de escaneos</p>
          <ul>
            <li v-for="item in state.telemetryMessages" :key="item.id">
              <span class="qr-telemetry__time">{{ item.formatted }}</span>
              <span class="qr-telemetry__message">{{ item.message }}</span>
            </li>
          </ul>
        </div>
      </section>

      <aside class="qr-panel qr-panel--result" aria-live="assertive">
        <div class="qr-result__state" v-if="state.resourceState === 'idle'">
          <h2>Sin resultados todavía</h2>
          <p>Apunta el dispositivo hacia un código QR válido para mostrar los detalles.</p>
        </div>

        <div class="qr-result__state" v-else-if="state.resourceState === 'loading'">
          <h2>Cargando información...</h2>
          <p>Estamos consultando el recurso asociado al código QR.</p>
        </div>

        <div class="qr-result__state qr-result__state--error" v-else-if="state.resourceState === 'error' && state.resourceError">
          <h2>Error al consultar</h2>
          <p>{{ state.resourceError }}</p>
          <button type="button" class="qr-btn" @click="handleRetry">
            Reintentar consulta
          </button>
        </div>

        <template v-else-if="state.resourceState === 'ready' && state.resource">
          <div
            v-if="state.resourceError"
            class="qr-alert qr-alert--warning"
            role="alert"
          >
            {{ state.resourceError }}
          </div>
          <GanadoDetailCard
            :ganado="state.resource"
            :role="role"
            :origin="state.resourceOrigin || undefined"
            :syncing="state.isSyncing"
            @reanudar="resumeScanAfterResult"
          @refrescar="handleRefresh"
            @accion="emitAction"
          />
        </template>

        <div class="qr-result__state" v-else>
          <h2>No hay datos disponibles</h2>
        </div>
      </aside>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref, withDefaults } from 'vue';
import type { CameraDevice, Html5QrcodeResult } from 'html5-qrcode';
import { Html5Qrcode, Html5QrcodeSupportedFormats } from 'html5-qrcode';
import { fetchQrResource, transformEmbeddedPayload } from '../services/qr';
import type { GanadoResource, EmbeddedQrPayload } from '../services/qr';
import GanadoDetailCard from './GanadoDetailCard.vue';

type QrScannerRole = 'admin' | 'user';

interface NormalizedUrlPayload {
  kind: 'url';
  url: string;
  raw: string;
}

interface NormalizedUnknownPayload {
  kind: 'unknown';
  raw: string;
}

type NormalizedPayload = NormalizedResourcePayload | NormalizedUrlPayload | NormalizedUnknownPayload;

interface TelemetryEntry {
  id: string;
  timestamp: number;
  formatted: string;
  message: string;
}

type EmbeddedGanadoPayload = EmbeddedQrPayload;

interface NormalizedResourcePayload {
  kind: 'resource';
  resourceId: string;
  resourceType: string | null;
  raw: string;
  metadata: Record<string, unknown>;
  embeddedResource?: EmbeddedGanadoPayload;
}

type ResourceState = 'idle' | 'loading' | 'ready' | 'error';
type ResourceOrigin = 'api' | 'embedded' | null;

interface ScannerState {
  availableCameras: CameraDevice[];
  selectedCameraId: string;
  isScanning: boolean;
  isPaused: boolean;
  lastError: string;
  resource: GanadoResource | null;
  resourceState: ResourceState;
  resourceError: string;
  lastPayload: NormalizedPayload | null;
  telemetryMessages: TelemetryEntry[];
  resourceOrigin: ResourceOrigin;
  isSyncing: boolean;
}

const props = withDefaults(defineProps<{
  role?: QrScannerRole;
  resourceEndpoint: string;
}>(), {
  role: 'user' as QrScannerRole
});

const emit = defineEmits<{
  (event: 'qr-detected', payload: NormalizedPayload): void;
  (event: 'resource-loaded', payload: GanadoResource): void;
  (event: 'error', payload: string): void;
  (event: 'action', payload: string): void;
}>();

const state = reactive<ScannerState>({
  availableCameras: [],
  selectedCameraId: '',
  isScanning: false,
  isPaused: false,
  lastError: '',
  resource: null,
  resourceState: 'idle',
  resourceError: '',
  lastPayload: null,
  telemetryMessages: [],
  resourceOrigin: null,
  isSyncing: false
});

const html5QrCodeInstance = ref<Html5Qrcode | null>(null);
// Generar ID único para el elemento de video usando CSPRNG
const generateSecureId = (): string => {
  const array = new Uint8Array(8);
  crypto.getRandomValues(array);
  return Array.from(array, byte => byte.toString(36)).join('').slice(0, 8);
};
const videoElementId = `qr-video-${generateSecureId()}`;
const fileInputRef = ref<HTMLInputElement | null>(null);
const abortControllerRef = ref<AbortController | null>(null);

const hasNavigatorSupport = typeof navigator !== 'undefined';
let telemetrySequence = 0;

const isEmbeddedGanadoPayload = (value: unknown): value is EmbeddedGanadoPayload => {
  if (!value || typeof value !== 'object') return false;
  const payload = value as Record<string, unknown>;
  const schema = typeof payload.schema === 'string' ? payload.schema : '';
  const tipo = typeof payload.type === 'string' ? payload.type : '';
  const identifier = payload.id;
  const hasId = typeof identifier === 'string' || typeof identifier === 'number';
  return schema.startsWith('qr-farm') && tipo === 'ganado' && hasId;
};

const canUseNetwork = (): boolean => !hasNavigatorSupport || navigator.onLine;

const mapGanadoResourceFromEmbedded = (payload: EmbeddedGanadoPayload): GanadoResource => transformEmbeddedPayload(payload);

const applyResource = (resource: GanadoResource, origin: ResourceOrigin, syncing: boolean): void => {
  state.resource = resource;
  state.resourceState = 'ready';
  state.resourceOrigin = origin;
  state.isSyncing = syncing;
  state.resourceError = '';
  emit('resource-loaded', resource);
};

const roleLabel = computed(() => {
  if (props.role === 'admin') return 'Administrador';
  return 'Usuario';
});

const headerTitle = computed(() => 'Escáner de códigos QR');
const headerSubtitle = computed(() => 'Apunta el código dentro del recuadro para obtener la información al instante.');

const scannerStatus = computed(() => {
  if (state.lastError) return 'error';
  if (state.isPaused) return 'paused';
  if (state.isScanning) return 'scanning';
  return 'idle';
});

const scannerStatusLabel = computed(() => {
  if (state.lastError) return state.lastError;
  if (state.isPaused) return 'Escaneo en pausa';
  if (state.isScanning) return 'Escaneando...';
  return 'Listo para escanear';
});

const pushTelemetry = (message: string): void => {
  const entry: TelemetryEntry = {
    id: `${Date.now()}-${telemetrySequence++}`,
    timestamp: Date.now(),
    formatted: new Date().toLocaleTimeString(),
    message
  };
  state.telemetryMessages = [...state.telemetryMessages.slice(-9), entry];
  console.info(`[QR-SCANNER] ${message}`);
};

const appendError = (message: string): void => {
  state.lastError = message;
  emit('error', message);
  pushTelemetry(`Error: ${message}`);
};

const clearError = (): void => {
  state.lastError = '';
};

const ensureHtml5QrCodeInstance = async (): Promise<void> => {
  if (html5QrCodeInstance.value) return;
  if (globalThis.window === undefined) {
    appendError('La ventana del navegador no está disponible.');
    return;
  }

  html5QrCodeInstance.value = new Html5Qrcode(videoElementId, {
    formatsToSupport: [
      Html5QrcodeSupportedFormats.QR_CODE,
      Html5QrcodeSupportedFormats.AZTEC,
      Html5QrcodeSupportedFormats.PDF_417
    ]
  });
};

const loadCameras = async (): Promise<void> => {
  try {
    await ensureHtml5QrCodeInstance();
    
    // Verificar si el navegador soporta acceso a cámaras
    if (!navigator?.mediaDevices?.getUserMedia) {
      appendError('Tu navegador no soporta acceso a la cámara. Usa Chrome, Firefox o Edge actualizado.');
      return;
    }
    
    const cameras = await Html5Qrcode.getCameras();
    if (!Array.isArray(cameras) || cameras.length === 0) {
      appendError('No se detectaron cámaras disponibles. Verifica que tengas una cámara conectada.');
      return;
    }
    state.availableCameras = cameras;
    if (!state.selectedCameraId) {
      const preferred = cameras.find(camera => camera.label.toLowerCase().includes('back')) ?? cameras[0];
      state.selectedCameraId = preferred.id;
      pushTelemetry(`Cámara seleccionada: ${preferred.label}`);
    }
    clearError(); // Limpiar errores previos si se cargaron correctamente
  } catch (error: any) {
    console.error('[QR-SCANNER] Error cargando cámaras:', error);
    
    // Mensajes de error más específicos según el tipo de error
    let errorMessage = 'No fue posible obtener las cámaras.';
    
    if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
      errorMessage = 'Permisos de cámara denegados. Por favor, permite el acceso a la cámara en la configuración de tu navegador y recarga la página.';
    } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
      errorMessage = 'No se encontraron cámaras. Verifica que tengas una cámara conectada y habilitada.';
    } else if (error.name === 'NotReadableError' || error.name === 'TrackStartError') {
      errorMessage = 'La cámara está siendo usada por otra aplicación. Cierra otras aplicaciones que usen la cámara e intenta de nuevo.';
    } else if (error.message) {
      errorMessage = `Error al acceder a las cámaras: ${error.message}`;
    }
    
    appendError(errorMessage);
    pushTelemetry(`Error: ${errorMessage}`);
  }
};

const startScanner = async (): Promise<void> => {
  if (!state.selectedCameraId) {
    appendError('Selecciona una cámara antes de iniciar.');
    return;
  }
  try {
    clearError();
    await ensureHtml5QrCodeInstance();
    const instance = html5QrCodeInstance.value;
    if (!instance) {
      appendError('El escáner no se inicializó correctamente.');
      return;
    }
    // Configuración optimizada para mejor detección de QR
    const config = {
      fps: 30,  // Mayor frecuencia de escaneo (30 FPS para mejor detección)
      qrbox: function(viewfinderWidth: number, viewfinderHeight: number) {
        // Usar 90% del viewport para área de escaneo más grande
        const minEdgePercentage = 0.9;
        const minEdgeSize = Math.min(viewfinderWidth, viewfinderHeight);
        const qrboxSize = Math.floor(minEdgeSize * minEdgePercentage);
        return {
          width: qrboxSize,
          height: qrboxSize
        };
      },
      aspectRatio: 1,  // QR es cuadrado
      disableFlip: false,  // Permitir rotación para mejor detección
      videoConstraints: {
        facingMode: "environment",  // Preferir cámara trasera
        width: { ideal: 1280 },  // Resolución más alta para mejor detección
        height: { ideal: 720 }
      },
      experimentalFeatures: {
        useBarCodeDetectorIfSupported: true  // Usar detector nativo del navegador si está disponible
      }
    };
    await instance.start(
      state.selectedCameraId,
      config,
      handleScanSuccess,
      handleScanFailure
    );
    state.isScanning = true;
    state.isPaused = false;
    pushTelemetry('Escaneo iniciado.');
  } catch (error) {
    appendError('No fue posible iniciar el escaneo.');
    console.error(error);
  }
};

const pauseScanner = async (): Promise<void> => {
  const instance = html5QrCodeInstance.value;
  if (!instance || !state.isScanning) return;
  await instance.pause(true);
  state.isPaused = true;
  pushTelemetry('Escaneo en pausa.');
};

const resumeScanner = async (): Promise<void> => {
  const instance = html5QrCodeInstance.value;
  if (!instance || !state.isScanning) return;
  await instance.resume();
  state.isPaused = false;
  pushTelemetry('Escaneo reanudado.');
};

const stopScanner = async (): Promise<void> => {
  const instance = html5QrCodeInstance.value;
  if (!instance) return;
  try {
    if (state.isScanning) {
      await instance.stop();
      await instance.clear();
    }
  } catch (error) {
    console.error(error);
  } finally {
    state.isScanning = false;
    state.isPaused = false;
    pushTelemetry('Escaneo detenido.');
  }
};

const readCandidateIdentifier = (value: unknown): string | null => {
  if (typeof value === 'string') {
    const trimmed = value.trim();
    return trimmed.length > 0 ? trimmed : null;
  }
  if (typeof value === 'number') {
    return String(value);
  }
  return null;
};

const collectAlternativeIdentifiers = (payload: NormalizedResourcePayload): string[] => {
  const alternatives = new Set<string>();
  const register = (candidate: unknown) => {
    const normalized = readCandidateIdentifier(candidate);
    if (!normalized) return;
    if (normalized === payload.resourceId) return;
    alternatives.add(normalized);
  };

  const metadata = payload.metadata ?? {};
  if (metadata && typeof metadata === 'object') {
    const metaRecord = metadata as Record<string, unknown>;
    register(metaRecord.codigo);
    register(metaRecord.code);
    register(metaRecord.codigo_qr);
    register(metaRecord.qr);
  }

  if (payload.embeddedResource) {
    const embedded = payload.embeddedResource;
    register(embedded.codigo);
    register(embedded.code);
    register(embedded.codigo_qr);
    if (embedded.id !== undefined && embedded.id !== null) {
      register(embedded.id);
    }
  }

  return Array.from(alternatives);
};

const normalizePayload = (raw: string): NormalizedPayload => {
  const sanitized = raw.trim();
  if (!sanitized) return unknownPayload(sanitized);

  const jsonResult = parseJsonPayload(sanitized);
  if (jsonResult) return jsonResult;

  const idResult = parseIdPatterns(sanitized);
  if (idResult) return idResult;

  const urlResult = parseUrlPayload(sanitized);
  if (urlResult) return urlResult;

  return unknownPayload(sanitized);
};

// --- Helpers ----

const unknownPayload = (raw: string): NormalizedPayload => ({
  kind: "unknown",
  raw
});

const parseJsonPayload = (sanitized: string): NormalizedPayload | null => {
  try {
    const parsed = JSON.parse(sanitized);
    if (!parsed || typeof parsed !== "object") return null;

    const candidateId = extractCandidateIdFromObject(parsed);
    if (!candidateId) return null;

    const embeddedResource = isEmbeddedGanadoPayload(parsed)
      ? parsed
      : undefined;

    const metadata: Record<string, unknown> = { ...parsed };
    delete metadata.id;
    delete metadata.resourceId;

    return {
      kind: "resource",
      resourceId: candidateId,
      resourceType: getResourceType(parsed),
      raw: sanitized,
      metadata,
      embeddedResource
    };
  } catch {
    return null;
  }
};

const parseIdPatterns = (sanitized: string): NormalizedPayload | null => {
  const numericMatch = sanitized.match(/(?:id|ID|Id)[:=]\s*(\d+)/);
  if (numericMatch) {
    return basicResourcePayload(numericMatch[1], sanitized);
  }

  if (/^\d+$/.test(sanitized)) {
    return basicResourcePayload(sanitized, sanitized);
  }

  return null;
};

const parseUrlPayload = (sanitized: string): NormalizedPayload | null => {
  try {
    const url = new URL(sanitized);
    const segments = url.pathname.split("/").filter(Boolean);
    const last = segments[segments.length - 1];

    if (last && /^\d+$/.test(last)) {
      return {
        kind: "resource",
        resourceId: last,
        resourceType: null,
        raw: sanitized,
        metadata: { url: url.toString() }
      };
    }

    return { kind: "url", url: url.toString(), raw: sanitized };
  } catch {
    return null;
  }
};

const basicResourcePayload = (
  id: string,
  raw: string
): NormalizedPayload => ({
  kind: "resource",
  resourceId: id,
  resourceType: null,
  raw,
  metadata: {}
});

const getResourceType = (obj: any): string | null => {
  if (typeof obj.tipo === "string") return obj.tipo;
  if (typeof obj.type === "string") return obj.type;
  return null;
};

const extractCandidateIdFromObject = (value: Record<string, unknown>): string | null => {
  const candidates = ['id', 'resourceId', 'codigo', 'code'];
  for (const key of candidates) {
    const candidateValue = value[key];
    if (typeof candidateValue === 'string' && candidateValue.trim().length > 0) {
      return candidateValue.trim();
    }
    if (typeof candidateValue === 'number') {
      return String(candidateValue);
    }
  }
  return null;
};

const fetchResource = async (payload: NormalizedPayload): Promise<void> => {
  if (payload.kind !== 'resource') {
    state.resourceState = 'error';
    state.resourceError = 'El código QR no contiene un identificador válido.';
    emit('error', state.resourceError);
    pushTelemetry('Error: QR sin identificador válido.');
    return;
  }

  const embedded = payload.embeddedResource ? mapGanadoResourceFromEmbedded(payload.embeddedResource) : null;
  const networkAvailable = canUseNetwork();

  if (!networkAvailable) {
    if (embedded) {
      applyResource(embedded, 'embedded', false);
      state.lastPayload = payload;
      pushTelemetry('Datos embebidos mostrados en modo offline.');
    } else {
      state.resourceState = 'error';
      state.resourceError = 'No hay conexión y el código QR no contiene datos embebidos.';
      emit('error', state.resourceError);
      pushTelemetry('Error: sin conexión y sin datos embebidos.');
    }
    return;
  }

  if (embedded) {
    applyResource(embedded, 'embedded', true);
    pushTelemetry('Datos embebidos detectados. Sincronizando con el servidor...');
  } else {
    state.resourceState = 'loading';
    state.resource = null;
  }
  state.resourceError = '';
  state.lastPayload = payload;

  abortControllerRef.value?.abort();
  const controller = new AbortController();
  abortControllerRef.value = controller;

  const alternativeIds = collectAlternativeIdentifiers(payload);

  try {
    const resource = await fetchQrResource({
      endpoint: props.resourceEndpoint,
      resourceId: payload.resourceId,
      alternatives: alternativeIds,
      signal: controller.signal
    });
    applyResource(resource, 'api', false);
    pushTelemetry(`Datos sincronizados: ${resource.nombre ?? resource.id}`);
  } catch (error) {
    const message = buildFetchErrorMessage(error);
    if (embedded) {
      state.isSyncing = false;
      state.resourceOrigin = 'embedded';
      state.resourceError = message;
      emit('error', message);
      pushTelemetry(`Sincronización fallida: ${message}`);
    } else {
      state.resourceState = 'error';
      state.resource = null;
      state.resourceError = message;
      emit('error', message);
      pushTelemetry(`Fallo al consultar: ${message}`);
    }
  }
};

const buildFetchErrorMessage = (error: unknown): string => {
  if (typeof error === 'object' && error !== null && 'message' in error && typeof error.message === 'string') {
    return error.message;
  }
  return 'No se pudo consultar el recurso asociado.';
};

const handleScanSuccess = async (decodedText: string, decodedResult: Html5QrcodeResult): Promise<void> => {
  console.debug('QR detectado:', decodedResult);
  await pauseScanner();
  const payload = normalizePayload(decodedText);
  state.lastPayload = payload;
  emit('qr-detected', payload);
  pushTelemetry(`QR leído: ${payload.raw}`);
  await fetchResource(payload);
};

const handleScanFailure = (error: string): void => {
  console.debug('Intento fallido de lectura:', error);
};

const handleCameraChange = async (event: Event): Promise<void> => {
  const target = event.target as HTMLSelectElement;
  state.selectedCameraId = target.value;
  pushTelemetry(`Cámara seleccionada manualmente: ${target.value}`);
  if (state.isScanning) {
    await stopScanner();
    await startScanner();
  }
};

const handleStartScan = async (): Promise<void> => {
  await startScanner();
};

const handleStopScan = async (): Promise<void> => {
  await stopScanner();
};

const togglePause = async (): Promise<void> => {
  if (state.isPaused) {
    await resumeScanner();
  } else {
    await pauseScanner();
  }
};

const handleRefresh = async (): Promise<void> => {
  if (!state.lastPayload) return;
  await fetchResource(state.lastPayload);
};

const handleRetry = async (): Promise<void> => {
  await handleRefresh();
};

const openFileDialog = (): void => {
  fileInputRef.value?.click();
};

const handleFileInput = async (event: Event): Promise<void> => {
  const target = event.target as HTMLInputElement;
  if (!target.files || target.files.length === 0) return;
  const file = target.files[0];
  await stopScanner();
  await ensureHtml5QrCodeInstance();
  const instance = html5QrCodeInstance.value;
  if (!instance) {
    appendError('No se pudo inicializar el lector para la imagen.');
    return;
  }
  try {
    clearError();
    const result = await instance.scanFileV2(file, true);
    await handleScanSuccess(result.decodedText, result);
  } catch (error) {
    appendError('No se encontró un código QR en la imagen proporcionada.');
    console.error(error);
  } finally {
    target.value = '';
  }
};

const resumeScanAfterResult = async (): Promise<void> => {
  state.resourceState = 'idle';
  state.resource = null;
  state.resourceOrigin = null;
  state.isSyncing = false;
  state.resourceError = '';
  state.lastPayload = null;
  if (state.isScanning && state.isPaused) {
    await resumeScanner();
    return;
  }
  await startScanner();
};

const emitAction = (action: string): void => {
  emit('action', action);
  pushTelemetry(`Acción solicitada: ${action}`);
};

onMounted(async () => {
  if (!navigator?.mediaDevices?.getUserMedia) {
    appendError('El navegador no soporta acceso a la cámara. Usa el modo de carga de imagen.');
    return;
  }
  await loadCameras();
  // No iniciar automáticamente - el usuario debe hacer clic en "Iniciar escaneo"
  // Esto permite que el usuario seleccione la cámara primero si lo desea
});

onBeforeUnmount(async () => {
  abortControllerRef.value?.abort();
  await stopScanner();
  html5QrCodeInstance.value = null;
});
</script>

<style scoped>
.qr-wrapper {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.qr-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 1rem;
}

.qr-header__title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.75rem;
  font-weight: 700;
  margin: 0;
}

.qr-header__subtitle {
  margin: 0.25rem 0 0;
  color: #555;
  max-width: 48ch;
}

.qr-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.35rem 0.75rem;
  border-radius: 999px;
  background: #0d6efd;
  color: #fff;
  font-weight: 600;
  text-transform: capitalize;
}

.qr-layout {
  display: grid;
  grid-template-columns: minmax(0, 60%) minmax(0, 40%);
  gap: 1.5rem;
}

.qr-panel {
  background: #fff;
  border-radius: 1rem;
  box-shadow: 0 20px 45px rgba(26, 42, 83, 0.08);
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.qr-video {
  position: relative;
  border-radius: 1rem;
  overflow: hidden;
  aspect-ratio: 4 / 3;
  background: #0d1b2a;
}

.qr-video__viewport {
  width: 100%;
  height: 100%;
}

.qr-status {
  position: absolute;
  bottom: 0.75rem;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.65);
  color: #fff;
  padding: 0.35rem 1rem;
  border-radius: 999px;
  font-size: 0.85rem;
}

.qr-status[data-status='error'] {
  background: rgba(220, 53, 69, 0.85);
}

.qr-status[data-status='paused'] {
  background: rgba(255, 193, 7, 0.85);
}

.qr-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.qr-btn {
  border: none;
  border-radius: 0.75rem;
  background: #f0f4ff;
  color: #1f2a44;
  padding: 0.65rem 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
}

.qr-btn[disabled] {
  opacity: 0.6;
  cursor: not-allowed;
}

.qr-btn:not([disabled]):hover {
  transform: translateY(-1px);
  box-shadow: 0 8px 18px rgba(13, 110, 253, 0.18);
}

.qr-btn--primary {
  background: #0d6efd;
  color: #fff;
}

.qr-camera-select {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.qr-camera-select__label {
  font-weight: 600;
  color: #1f2a44;
}

.qr-camera-select__input {
  border-radius: 0.75rem;
  border: 1px solid #c5d0f6;
  padding: 0.5rem 0.75rem;
}

.qr-camera-select__input[disabled] {
  opacity: 0.6;
  cursor: not-allowed;
}

.qr-camera-select__error {
  margin: 0.5rem 0 0;
  color: #b91c1c;
  font-size: 0.875rem;
}

.qr-file-input {
  display: none;
}

.qr-alert {
  border-radius: 0.75rem;
  padding: 0.9rem 1rem;
  font-weight: 600;
}

.qr-alert--error {
  background: rgba(220, 53, 69, 0.25);
  color: #000;
}

.qr-alert--warning {
  background: rgba(255, 193, 7, 0.25);
  color: #000;
}

.qr-telemetry {
  border-radius: 0.75rem;
  background: #f8f9ff;
  padding: 0.75rem 1rem;
}

.qr-telemetry__title {
  font-size: 0.95rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.qr-telemetry__time {
  display: inline-block;
  width: 5rem;
  font-weight: 600;
  color: #0d6efd;
}

.qr-telemetry__message {
  color: #1f2a44;
}

.qr-panel--result {
  min-height: 100%;
}

.qr-result__state {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  text-align: left;
  color: #1f2a44;
}

.qr-result__state h2 {
  margin: 0;
  font-size: 1.35rem;
}

.qr-result__state--error h2 {
  color: #b91c1c;
}

.qr-result__details {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.qr-result__header h2 {
  margin: 0;
  font-size: 1.4rem;
}

.qr-result__content dl {
  margin: 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 0.75rem 1.5rem;
}

.qr-result__row {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  padding: 0.75rem;
  border-radius: 0.75rem;
  background: #f4f6ff;
}

.qr-result__row dt {
  font-weight: 700;
  color: #1f2a44;
}

.qr-result__row dd {
  margin: 0;
  color: #334155;
}

.qr-result__footer {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

@media (max-width: 992px) {
  .qr-layout {
    grid-template-columns: 1fr;
  }
}
</style>

