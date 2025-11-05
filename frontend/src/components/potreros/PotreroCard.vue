<template>
  <div class="card border-0 shadow-lg" style="min-width: 450px; max-width: 700px;">
    <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
      <h5 class="mb-0"><i class="fas fa-leaf me-2"></i>{{ potrero.nombre }}</h5>
      <button class="btn btn-light btn-sm" @click="$emit('toggle-accordion')">
        <i :class="accordionOpen ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
      </button>
    </div>
    <div class="card-body p-4 p-sm-5" v-show="accordionOpen">
      <div class="row g-3 mb-3">
        <div class="col-6"><strong>Estado:</strong> <span class="badge" :class="estadoClass(potrero.estado)">{{ potrero.estado }}</span></div>
        <div class="col-6"><strong>Capacidad:</strong> {{ potrero.capacidad || 'No definida' }} Animales</div>
      </div>
      <div class="row g-3 mb-3">
        <div class="col-6"><strong>Ocupación:</strong> {{ potrero.ocupacion || 0 }} Animales</div>
        <div class="col-6"><strong>Hectáreas:</strong> {{ potrero.hectareas || 'No definida' }} ha</div>
      </div>
      <div class="row g-3 mb-3">
        <div class="col-6"><strong>Fecha de último uso:</strong> {{ potrero.fechaUso || 'No registrada' }}</div>
        <div class="col-6"><strong>Responsable:</strong> {{ potrero.responsable }}</div>
      </div>
      <div class="row g-3 mb-3">
        <div class="col-12"><strong>Próxima limpieza:</strong> {{ potrero.proximaLimpieza || 'No programada' }}</div>
      </div>
      <div class="row g-3 mb-3">
        <div class="col-6"><strong>Área:</strong> {{ potrero.area || 'No definida' }} m²</div>
        <div class="col-6"><strong>Última limpieza:</strong> {{ potrero.ultimaLimpieza || 'No registrada' }}</div>
      </div>
      <div class="row g-3 mb-3" v-if="potrero.descripcion">
        <div class="col-12"><strong>Descripción:</strong> {{ potrero.descripcion }}</div>
      </div>
      <div class="d-flex gap-2 justify-content-center">
        <button class="btn btn-primary" @click="$emit('editar', potrero.id)"><i class="fas fa-edit me-1"></i>Editar</button>
        <button class="btn btn-success" @click="$emit('crear')"><i class="fas fa-plus me-1"></i>Crear Potrero</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PotreroCard',
  props: {
    potrero: {
      type: Object,
      required: true
    },
    accordionOpen: {
      type: Boolean,
      default: true
    }
  },
  emits: ['toggle-accordion', 'editar', 'crear'],
  methods: {
    estadoClass(estado) {
      if (estado === 'Disponible') return 'bg-success';
      if (estado === 'En uso') return 'bg-warning';
      if (estado === 'Mantenimiento') return 'bg-danger';
      return 'bg-secondary';
    }
  }
}
</script>