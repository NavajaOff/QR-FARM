<template>
  <article class="ganado-card">
    <header class="ganado-card__header">
      <div class="ganado-card__identity">
        <h2 class="ganado-card__title">
          <i class="fas fa-cow ganado-card__title-icon" aria-hidden="true"></i>
          <span>{{ displayName }}</span>
        </h2>
        <p class="ganado-card__meta">
          <strong>ID:</strong> {{ ganado.id }}
        </p>
        <p class="ganado-card__meta" v-if="ganado.codigo_qr">
          <strong>Código QR:</strong> {{ ganado.codigo_qr }}
        </p>
      </div>
      <div class="ganado-card__badges">
        <span v-if="estadoPrincipal" class="ganado-chip ganado-chip--primary">{{ estadoPrincipal }}</span>
        <span v-if="estadoSalud" class="ganado-chip ganado-chip--accent">{{ estadoSalud }}</span>
        <span v-if="originChip" class="ganado-chip ganado-chip--muted">{{ originChip }}</span>
      </div>
    </header>

    <div
      v-if="origin"
      class="ganado-banner"
      :class="origin === 'embedded' ? 'ganado-banner--warning' : 'ganado-banner--success'"
    >
      <div class="ganado-banner__info">
        <i :class="origin === 'embedded' ? 'fas fa-wifi-slash' : 'fas fa-signal'"></i>
        <span>{{ bannerMessage }}</span>
      </div>
      <button
        v-if="origin === 'embedded'"
        type="button"
        class="ganado-action ganado-action--ghost"
        @click="emit('refrescar')"
        :disabled="syncing"
      >
        <i :class="syncing ? 'fas fa-spinner fa-spin' : 'fas fa-sync-alt'"></i>
        {{ syncing ? 'Sincronizando...' : 'Actualizar datos' }}
      </button>
    </div>

    <nav class="ganado-tabs">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        type="button"
        class="ganado-tab"
        :class="{ 'ganado-tab--active': tab.id === activeSection }"
        @click="activeSection = tab.id"
        :aria-selected="tab.id === activeSection"
        :aria-controls="`ganado-panel-${tab.id}`"
      >
        <i :class="tab.icon" aria-hidden="true"></i>
        <span>{{ tab.label }}</span>
      </button>
    </nav>

    <section
      v-if="activeSection === 'general'"
      :id="'ganado-panel-general'"
      class="ganado-panel"
      role="tabpanel"
    >
      <div class="ganado-grid">
        <div class="ganado-field">
          <span class="ganado-field__label"><i class="fas fa-id-badge"></i>Nombre</span>
          <span class="ganado-field__value">{{ displayName }}</span>
        </div>
        <div class="ganado-field">
          <span class="ganado-field__label"><i class="fas fa-dna"></i>Raza</span>
          <span class="ganado-field__value">{{ formatOrDefault(ganado.raza) }}</span>
        </div>
        <div class="ganado-field">
          <span class="ganado-field__label"><i class="fas fa-venus-mars"></i>Sexo</span>
          <span class="ganado-field__value">{{ formatSexo(ganado.sexo) }}</span>
        </div>
        <div class="ganado-field">
          <span class="ganado-field__label"><i class="fas fa-birthday-cake"></i>Edad</span>
          <span class="ganado-field__value">{{ formatEdad(ganado.edad) }}</span>
        </div>
        <div class="ganado-field">
          <span class="ganado-field__label"><i class="fas fa-calendar-day"></i>Fecha de nacimiento</span>
          <span class="ganado-field__value">{{ formatDate(ganado.fecha_nacimiento) }}</span>
        </div>
        <div class="ganado-field">
          <span class="ganado-field__label"><i class="fas fa-weight-hanging"></i>Peso</span>
          <span class="ganado-field__value">{{ formatPeso(ganado.peso) }}</span>
        </div>
      </div>

      <div class="ganado-subsection">
        <h3 class="ganado-subsection__title">
          <i class="fas fa-user-tie"></i>
          Propietario / Encargado
        </h3>
        <div class="ganado-grid">
          <div class="ganado-field">
            <span class="ganado-field__label">Nombre</span>
            <span class="ganado-field__value">{{ formatOrDefault(ganado.propietario.nombre) }}</span>
          </div>
          <div class="ganado-field">
            <span class="ganado-field__label">Contacto</span>
            <span class="ganado-field__value">{{ formatOrDefault(ganado.propietario.telefono) }}</span>
          </div>
            <div class="ganado-field">
            <span class="ganado-field__label">Rol</span>
            <span class="ganado-field__value">{{ formatRol(ganado.propietario.rol) }}</span>
          </div>
        </div>
      </div>
    </section>

    <section
      v-else-if="activeSection === 'potrero'"
      :id="'ganado-panel-potrero'"
      class="ganado-panel"
      role="tabpanel"
    >
      <div v-if="tienePotrero" class="ganado-grid">
        <div class="ganado-field">
          <span class="ganado-field__label"><i class="fas fa-tractor"></i>Nombre</span>
          <span class="ganado-field__value">{{ formatOrDefault(ganado.potrero.nombre) }}</span>
        </div>
        <div class="ganado-field">
          <span class="ganado-field__label"><i class="fas fa-leaf"></i>Tipo de pasto</span>
          <span class="ganado-field__value">{{ formatOrDefault(ganado.potrero.tipo_pasto) }}</span>
        </div>
        <div class="ganado-field">
          <span class="ganado-field__label"><i class="fas fa-users"></i>Capacidad</span>
          <span class="ganado-field__value">{{ formatCapacidad(ganado.potrero.capacidad) }}</span>
        </div>
        <div class="ganado-field">
          <span class="ganado-field__label"><i class="fas fa-broom"></i>Última limpieza</span>
          <span class="ganado-field__value">{{ formatDate(ganado.potrero.ultima_limpieza) }}</span>
        </div>
        <div class="ganado-field">
          <span class="ganado-field__label"><i class="fas fa-calendar-check"></i>Próxima limpieza</span>
          <span class="ganado-field__value">{{ formatDate(ganado.potrero.proxima_limpieza) }}</span>
        </div>
        <div class="ganado-field">
          <span class="ganado-field__label"><i class="fas fa-clock"></i>Último uso</span>
          <span class="ganado-field__value">{{ formatDate(ganado.potrero.fecha_ultimo_uso) }}</span>
        </div>
        <div class="ganado-field">
          <span class="ganado-field__label"><i class="fas fa-signal"></i>Estado</span>
          <span class="ganado-field__value">{{ formatOrDefault(ganado.potrero.estado) }}</span>
        </div>
      </div>
      <p v-else class="ganado-empty">No hay información del potrero asociada al ganado.</p>
    </section>

    <section
      v-else-if="activeSection === 'vacunas'"
      :id="'ganado-panel-vacunas'"
      class="ganado-panel"
      role="tabpanel"
    >
      <div v-if="ganado.vacunas.length > 0" class="ganado-list">
        <div v-for="vacuna in ganado.vacunas" :key="vacuna.id ?? vacuna.nombre ?? Math.random()" class="ganado-list__item">
          <div class="ganado-list__header">
            <h4 class="ganado-list__title">
              <i class="fas fa-syringe"></i>
              <span>{{ formatOrDefault(vacuna.nombre) }}</span>
            </h4>
            <div class="ganado-list__badges">
              <span v-if="vacuna.estado" class="ganado-chip ganado-chip--muted">{{ vacuna.estado }}</span>
              <span v-if="isDoseOverdue(vacuna.proxima_dosis)" class="ganado-chip ganado-chip--danger">Dosis vencida</span>
              <span v-else-if="isDoseClose(vacuna.proxima_dosis)" class="ganado-chip ganado-chip--warning">Dosis próxima</span>
            </div>
          </div>
          <div class="ganado-grid ganado-grid--condensed">
            <div class="ganado-field">
              <span class="ganado-field__label">Aplicada</span>
              <span class="ganado-field__value">{{ formatDate(vacuna.fecha_aplicacion) }}</span>
            </div>
            <div class="ganado-field">
              <span class="ganado-field__label">Próxima dosis</span>
              <span class="ganado-field__value">{{ formatDate(vacuna.proxima_dosis) }}</span>
            </div>
            <div class="ganado-field">
              <span class="ganado-field__label">Responsable</span>
              <span class="ganado-field__value">{{ formatOrDefault(vacuna.responsable) }}</span>
            </div>
          </div>
        </div>
      </div>
      <p v-else class="ganado-empty">No hay vacunas registradas aún.</p>
    </section>

    <section
      v-else
      :id="'ganado-panel-historial'"
      class="ganado-panel"
      role="tabpanel"
    >
      <div v-if="ganado.historial.length > 0" class="ganado-list">
        <div v-for="evento in ganado.historial" :key="evento.id ?? evento.fecha ?? Math.random()" class="ganado-list__item">
          <div class="ganado-list__header">
            <h4 class="ganado-list__title">
              <i class="fas fa-notes-medical"></i>
              <span>{{ formatDate(evento.fecha) }}</span>
            </h4>
            <div class="ganado-list__badges">
              <span v-if="evento.veterinario" class="ganado-chip ganado-chip--muted">
                {{ evento.veterinario }}
              </span>
            </div>
          </div>
          <p class="ganado-list__text">
            <strong>Observaciones:</strong> {{ formatOrDefault(evento.observaciones) }}
          </p>
          <p class="ganado-list__text">
            <strong>Resultado:</strong> {{ formatOrDefault(evento.resultado) }}
          </p>
        </div>
      </div>
      <p v-else class="ganado-empty">No hay revisiones registradas para este ganado.</p>
    </section>

    <footer class="ganado-card__footer">
      <button type="button" class="ganado-action ganado-action--primary" @click="emit('reanudar')">
        <i class="fas fa-redo"></i>
        Volver a escanear
      </button>
      <div class="ganado-card__actions">
        <button
          v-if="role === 'admin'"
          type="button"
          class="ganado-action"
          @click="emit('accion', 'ver-historial')"
        >
          <i class="fas fa-history"></i>
          Ver historial completo
        </button>
        <button
          v-if="role === 'admin'"
          type="button"
          class="ganado-action"
          @click="emit('accion', 'descargar-ficha')"
        >
          <i class="fas fa-print"></i>
          Descargar ficha
        </button>
      </div>
    </footer>
  </article>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import type { GanadoResource } from '../services/qr';

type TabId = 'general' | 'potrero' | 'vacunas' | 'historial';

const props = defineProps<{
  ganado: GanadoResource;
  role: 'admin' | 'user';
  origin?: 'api' | 'embedded';
  syncing?: boolean;
}>();

const emit = defineEmits<{
  (event: 'reanudar'): void;
  (event: 'accion', value: string): void;
  (event: 'refrescar'): void;
}>();

const tabs = [
  { id: 'general', label: 'Información general', icon: 'fas fa-info-circle' },
  { id: 'potrero', label: 'Potrero', icon: 'fas fa-seedling' },
  { id: 'vacunas', label: 'Vacunas', icon: 'fas fa-syringe' },
  { id: 'historial', label: 'Historial', icon: 'fas fa-clipboard-list' }
] as const;

const activeSection = ref<TabId>('general');

const displayName = computed(() => props.ganado.nombre ?? 'Sin nombre registrado');
const estadoPrincipal = computed(() => formatCapitalized(props.ganado.estado));
const estadoSalud = computed(() => formatCapitalized(props.ganado.estado_salud));
const tienePotrero = computed(() => {
  return Boolean(
    props.ganado.potrero.nombre ||
    props.ganado.potrero.tipo_pasto ||
    props.ganado.potrero.capacidad
  );
});

const originChip = computed(() => {
  if (props.origin === 'embedded' && props.syncing) return 'Datos sin conexión (actualizando)';
  if (props.origin === 'embedded') return 'Datos sin conexión';
  if (props.origin === 'api' && props.syncing) return 'Datos en línea (actualizando)';
  if (props.origin === 'api') return 'Datos en línea';
  return null;
});

const bannerMessage = computed(() => {
  if (props.origin === 'embedded') {
    return props.syncing
      ? 'Sincronizando con el servidor...'
      : 'Mostrando datos embebidos del QR.';
  }
  if (props.origin === 'api') {
    return 'Datos actualizados desde el servidor.';
  }
  return '';
});

const formatOrDefault = (value: string | null): string => {
  return value && value.trim().length > 0 ? value : 'Sin datos';
};

const formatCapitalized = (value: string | null): string | null => {
  if (!value) return null;
  const normalized = value.trim().toLowerCase();
  if (normalized.length === 0) return null;
  return normalized.charAt(0).toUpperCase() + normalized.slice(1);
};

const formatSexo = (value: string | null): string => {
  return formatOrDefault(formatCapitalized(value));
};

const formatEdad = (value: number | null): string => {
  if (value === null) return 'Sin datos';
  return value === 1 ? '1 año' : `${value} años`;
};

const formatPeso = (value: number | null): string => {
  if (value === null) return 'Sin datos';
  return `${value.toFixed(1)} kg`;
};

const formatCapacidad = (value: number | null): string => {
  if (value === null) return 'Sin datos';
  return `${value} animales`;
};

const formatDate = (value: string | null): string => {
  if (!value) return 'Sin datos';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat('es-CO', { dateStyle: 'long' }).format(date);
};

const formatRol = (value: string | null): string => {
  const normalized = formatCapitalized(value);
  return normalized ?? 'Sin datos';
};

const isDoseClose = (value: string | null): boolean => {
  if (!value) return false;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return false;
  const today = new Date();
  const diff = (date.getTime() - today.getTime()) / (1000 * 60 * 60 * 24);
  return diff >= 0 && diff <= 10;
};

const isDoseOverdue = (value: string | null): boolean => {
  if (!value) return false;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return false;
  const today = new Date();
  return date.getTime() < today.getTime();
};
</script>

<style scoped>
.ganado-card {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.ganado-card__header {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.ganado-card__identity {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.ganado-card__title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.65rem;
  font-weight: 700;
  margin: 0;
  color: #1f2937;
}

.ganado-card__title-icon {
  color: #198754;
}

.ganado-card__meta {
  margin: 0;
  font-size: 0.95rem;
  color: #4b5563;
}

.ganado-card__badges {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.ganado-banner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  border-radius: 0.85rem;
  padding: 0.9rem 1rem;
  font-weight: 600;
}

.ganado-banner--warning {
  background: rgba(255, 193, 7, 0.15);
  color: #8a6d1a;
}

.ganado-banner--success {
  background: rgba(25, 135, 84, 0.35);
  color: #0f5132;
}

.ganado-banner__info {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.ganado-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  border-radius: 999px;
  padding: 0.35rem 0.75rem;
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: capitalize;
}

.ganado-chip--primary {
  background: rgba(13, 110, 253, 0.15);
  color: #0b5ed7;
}

.ganado-chip--accent {
  background: rgba(25, 135, 84, 0.15);
  color: #198754;
}

.ganado-chip--muted {
  background: rgba(107, 114, 128, 0.15);
  color: #4b5563;
}

.ganado-chip--warning {
  background: rgba(255, 193, 7, 0.2);
  color: #b58104;
}

.ganado-chip--danger {
  background: rgba(220, 53, 69, 0.2);
  color: #b02a37;
}

.ganado-tabs {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.ganado-tab {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.6rem 1rem;
  border-radius: 0.75rem;
  border: 1px solid transparent;
  background: #f1f5f9;
  color: #1f2937;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.ganado-tab:hover {
  background: #e2e8f0;
}

.ganado-tab--active {
  background: #0d6efd;
  color: #fff;
  box-shadow: 0 12px 24px rgba(13, 110, 253, 0.18);
}

.ganado-panel {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.ganado-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
}

.ganado-grid--condensed {
  gap: 0.75rem;
}

.ganado-field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  background: #f8fafc;
  border-radius: 0.85rem;
  padding: 0.9rem 1rem;
  box-shadow: inset 0 0 0 1px rgba(148, 163, 184, 0.18);
}

.ganado-field__label {
  color: #64748b;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.02em;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.ganado-field__value {
  color: #111827;
  font-weight: 600;
  font-size: 1rem;
}

.ganado-subsection {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.ganado-subsection__title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.1rem;
  font-weight: 700;
  margin: 0;
  color: #1f2937;
}

.ganado-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.ganado-list__item {
  background: #f8fafc;
  border-radius: 1rem;
  padding: 1rem 1.1rem;
  box-shadow: inset 0 0 0 1px rgba(148, 163, 184, 0.18);
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.ganado-list__header {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  flex-wrap: wrap;
  align-items: center;
}

.ganado-list__title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.05rem;
  font-weight: 700;
  margin: 0;
  color: #1e293b;
}

.ganado-list__badges {
  display: inline-flex;
  gap: 0.4rem;
  flex-wrap: wrap;
}

.ganado-list__text {
  margin: 0;
  color: #334155;
  line-height: 1.45;
}

.ganado-empty {
  margin: 0;
  padding: 1rem;
  border-radius: 0.85rem;
  background: rgba(15, 118, 110, 0.08);
  color: #0f766e;
  font-weight: 600;
}

.ganado-card__footer {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  align-items: center;
  justify-content: space-between;
}

.ganado-card__actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.ganado-action {
  border: none;
  border-radius: 0.75rem;
  background: #e2e8f0;
  color: #1f2937;
  padding: 0.65rem 1.1rem;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
}

.ganado-action--primary {
  background: #0d6efd;
  color: #fff;
}

.ganado-action--ghost {
  background: transparent;
  color: inherit;
  border: 1px solid currentColor;
}

.ganado-action:hover {
  transform: translateY(-1px);
  box-shadow: 0 12px 22px rgba(15, 23, 42, 0.1);
}

@media (max-width: 768px) {
  .ganado-card__footer {
    flex-direction: column;
    align-items: stretch;
  }

  .ganado-card__actions {
    width: 100%;
    flex-direction: column;
  }

  .ganado-action,
  .ganado-action--primary {
    width: 100%;
    justify-content: center;
  }
}
</style>

