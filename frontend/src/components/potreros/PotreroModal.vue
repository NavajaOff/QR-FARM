<template>
  <div class="modal fade show d-block" tabindex="-1" aria-modal="true" aria-labelledby="potreroModalLabel">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">{{ isEditing ? 'Editar' : 'Crear' }} Potrero</h5>
          <button type="button" class="btn-close" @click="$emit('close')"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="submitForm">
            <div class="row">
              <div class="col-md-6 mb-3">
                <label class="form-label" for="potrero-nombre">Nombre *</label>
                <input type="text" id="potrero-nombre" class="form-control" v-model="form.nombre" required>
              </div>
              <div v-if="isEditing" class="col-md-6 mb-3">
                <label class="form-label" for="potrero-estado">Estado</label>
                <select id="potrero-estado" class="form-select" v-model="form.id_estado_potrero">
                  <option v-for="estado in estadosPotrero" :key="estado.id" :value="estado.id">
                    {{ estado.nombre_estado || estado.estado || estado.nombre }}
                  </option>
                </select>
              </div>
            </div>
            <div class="row">
              <div class="col-md-6 mb-3">
                <label class="form-label" for="potrero-capacidad">Capacidad</label>
                <input type="number" id="potrero-capacidad" class="form-control" v-model.number="form.capacidad" min="0">
              </div>
              <div class="col-md-6 mb-3">
                <label class="form-label" for="potrero-hectareas">Hectáreas</label>
                <input type="number" id="potrero-hectareas" class="form-control" v-model.number="form.hectareas" step="0.01" min="0">
              </div>
            </div>
            <div class="row">
              <div class="col-md-6 mb-3">
                <label class="form-label" for="potrero-tipo-pasto">Tipo de Pasto</label>
                <select id="potrero-tipo-pasto" class="form-select" v-model="form.id_tipo_pasto">
                  <option value="">Seleccionar tipo de pasto</option>
                  <option v-for="tipo in tiposPasto" :key="tipo.id" :value="tipo.id">
                    {{ tipo.tipo_pasto || tipo.nombre }}
                  </option>
                </select>
              </div>
              <div class="col-md-6 mb-3">
                <label class="form-label" for="potrero-responsable">Responsable</label>
                <select id="potrero-responsable" class="form-select" v-model="form.responsable_persona_id">
                  <option value="">Seleccionar responsable</option>
                  <option v-for="persona in personasUsuario" :key="persona.id" :value="persona.id">
                    {{ persona.nombre_completo }}
                  </option>
                </select>
              </div>
            </div>
            <div class="row" v-if="isEditing">
              <div class="col-md-6 mb-3">
                <label class="form-label" for="potrero-fecha-ultimo-uso">Fecha último uso</label>
                <input type="date" id="potrero-fecha-ultimo-uso" class="form-control" v-model="form.fecha_ultimo_uso">
              </div>
              <div class="col-md-6 mb-3">
                <label class="form-label" for="potrero-proxima-limpieza">Próxima limpieza</label>
                <input type="date" id="potrero-proxima-limpieza" class="form-control" v-model="form.proxima_limpieza">
              </div>
            </div>
            <div class="row">
              <div v-if="isEditing" class="col-md-6 mb-3">
                <label class="form-label" for="potrero-area">Área (m²)</label>
                <input type="number" id="potrero-area" class="form-control" v-model.number="form.area" step="0.01" min="0">
              </div>
              <div class="col-md-6 mb-3" :class="{ 'offset-md-6': !isEditing }">
                <label class="form-label" for="potrero-ultima-limpieza">Última limpieza</label>
                <input type="date" id="potrero-ultima-limpieza" class="form-control" v-model="form.ultima_limpieza">
              </div>
            </div>
            <div class="mb-3">
              <label class="form-label" for="potrero-descripcion">Descripción</label>
              <textarea id="potrero-descripcion" class="form-control" v-model="form.descripcion" rows="2"></textarea>
            </div>
          </form>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="$emit('close')">Cancelar</button>
          <button type="button" class="btn btn-primary" @click="submitForm" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
            {{ isEditing ? 'Actualizar' : 'Crear' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PotreroModal',
  props: {
    isEditing: {
      type: Boolean,
      default: false
    },
    potrero: {
      type: Object,
      default: () => ({})
    },
    tiposPasto: {
      type: Array,
      default: () => []
    },
    estadosPotrero: {
      type: Array,
      default: () => []
    },
    personasUsuario: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['close', 'submit'],
  data() {
    return {
      form: {
        nombre: '',
        id_estado_potrero: 1,
        capacidad: null,
        hectareas: null,
        id_tipo_pasto: null,
        fecha_ultimo_uso: '',
        responsable_persona_id: null,
        proxima_limpieza: '',
        area: null,
        ultima_limpieza: '',
        descripcion: ''
      }
    }
  },
  watch: {
    potrero: {
      handler(newPotrero) {
        if (newPotrero && this.isEditing) {
          this.form = { ...newPotrero }
        }
      },
      immediate: true,
      deep: true
    },
    'form.hectareas'(newHectareas) {
      // Calcular área automáticamente cuando se cambian las hectáreas (solo en creación)
      if (!this.isEditing && newHectareas !== null && newHectareas !== undefined && newHectareas > 0) {
        this.form.area = newHectareas * 10000; // 1 hectárea = 10,000 m²
      }
    }
  },
  methods: {
    submitForm() {
      this.$emit('submit', { ...this.form })
    },

    resetForm() {
      this.form = {
        nombre: '',
        id_estado_potrero: 1,
        capacidad: null,
        hectareas: null,
        id_tipo_pasto: null,
        fecha_ultimo_uso: '',
        responsable_persona_id: null,
        proxima_limpieza: '',
        area: null,
        ultima_limpieza: '',
        descripcion: ''
      }
    }
  }
}
</script>