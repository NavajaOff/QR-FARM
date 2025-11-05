<template>
  <div class="modal fade show d-block" tabindex="-1" role="dialog">
    <div class="modal-dialog modal-lg" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">{{ isEditing ? 'Editar' : 'Crear' }} Potrero</h5>
          <button type="button" class="btn-close" @click="$emit('close')"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="submitForm">
            <div class="row">
              <div class="col-md-6 mb-3">
                <label class="form-label">Nombre *</label>
                <input type="text" class="form-control" v-model="form.nombre" required>
              </div>
              <div class="col-md-6 mb-3">
                <label class="form-label">Estado</label>
                <select class="form-select" v-model="form.estado">
                  <option v-for="estado in estadosPotrero" :key="estado.id" :value="estado.nombre">
                    {{ estado.nombre }}
                  </option>
                </select>
              </div>
            </div>
            <div class="row">
              <div class="col-md-6 mb-3">
                <label class="form-label">Capacidad</label>
                <input type="number" class="form-control" v-model.number="form.capacidad" min="0">
              </div>
              <div class="col-md-6 mb-3">
                <label class="form-label">Hectáreas</label>
                <input type="number" class="form-control" v-model.number="form.hectareas" step="0.01" min="0">
              </div>
            </div>
            <div class="row">
              <div class="col-md-6 mb-3">
                <label class="form-label">Tipo de Pasto</label>
                <select class="form-select" v-model="form.id_tipo_pasto">
                  <option value="">Seleccionar tipo de pasto</option>
                  <option v-for="tipo in tiposPasto" :key="tipo.id" :value="tipo.id">
                    {{ tipo.nombre }}
                  </option>
                </select>
              </div>
              <div class="col-md-6 mb-3">
                <label class="form-label">Responsable</label>
                <select class="form-select" v-model="form.responsable_persona_id">
                  <option value="">Seleccionar responsable</option>
                  <option v-for="persona in personasUsuario" :key="persona.id" :value="persona.id">
                    {{ persona.nombre_completo }}
                  </option>
                </select>
              </div>
            </div>
            <div class="row">
              <div class="col-md-6 mb-3">
                <label class="form-label">Fecha último uso</label>
                <input type="date" class="form-control" v-model="form.fecha_ultimo_uso">
              </div>
              <div class="col-md-6 mb-3">
                <label class="form-label">Próxima limpieza</label>
                <input type="date" class="form-control" v-model="form.proxima_limpieza">
              </div>
            </div>
            <div class="row">
              <div class="col-md-6 mb-3">
                <label class="form-label">Área (m²)</label>
                <input type="number" class="form-control" v-model.number="form.area" step="0.01" min="0">
              </div>
              <div class="col-md-6 mb-3">
                <label class="form-label">Última limpieza</label>
                <input type="date" class="form-control" v-model="form.ultima_limpieza">
              </div>
            </div>
            <div class="mb-3">
              <label class="form-label">Descripción</label>
              <textarea class="form-control" v-model="form.descripcion" rows="2"></textarea>
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
        estado: 'disponible',
        capacidad: null,
        hectareas: null,
        ocupacion: 0,
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
    }
  },
  methods: {
    submitForm() {
      this.$emit('submit', { ...this.form })
    },

    resetForm() {
      this.form = {
        nombre: '',
        estado: 'disponible',
        capacidad: null,
        hectareas: null,
        ocupacion: 0,
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