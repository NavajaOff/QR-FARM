<template>
  <div class="container-fluid py-4">
    <div class="row">
      <div class="col-12">
        <div class="d-flex flex-wrap justify-content-between align-items-center mb-4 gap-3">
          <div>
            <h2 class="mb-1">
              <i class="fas fa-chart-line me-2 text-success"></i>Reportes de Mis Recursos
            </h2>
            <p class="text-muted mb-0">Resumen de ganado, potreros y vacunaciones</p>
          </div>
          <button class="btn btn-danger" @click="descargar" :disabled="descargando">
            <span v-if="descargando" class="spinner-border spinner-border-sm me-2"></span>
            <i v-else class="fas fa-file-download me-2"></i>
            Descargar PDF
          </button>
        </div>

        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-success" role="status">
            <span class="visually-hidden">Cargando...</span>
          </div>
          <p class="mt-2 text-muted">Generando resumen...</p>
        </div>

        <div v-else-if="error" class="alert alert-danger">
          <i class="fas fa-exclamation-circle me-2"></i>{{ error }}
        </div>

        <template v-else-if="resumen">
          <div class="row g-3 mb-4">
            <div class="col-12 col-sm-6 col-lg-4" v-for="card in cards" :key="card.titulo">
              <div class="card border-0 shadow-sm h-100">
                <div class="card-body">
                  <h6 class="text-muted text-uppercase fw-bold">{{ card.titulo }}</h6>
                  <p class="display-6 fw-bold mb-1">{{ card.total }}</p>
                  <p v-for="detalle in card.detalles" :key="detalle" class="text-muted mb-1">
                    {{ detalle }}
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div class="card border-0 shadow">
            <div class="card-body">
              <h4 class="card-title mb-4">Distribución por estado</h4>
              <div class="d-flex justify-content-center">
                <div class="chart-wrapper">
                  <canvas ref="chartCanvas"></canvas>
                </div>
              </div>
            </div>
          </div>

          <div class="card border-0 shadow mt-4">
            <div class="card-body">
              <h4 class="card-title mb-4">Detalle</h4>

              <div v-for="seccion in secciones" :key="seccion.titulo" class="mb-4">
                <div class="d-flex justify-content-between align-items-center">
                  <h5 class="mb-1">{{ seccion.titulo }}</h5>
                  <span class="badge bg-light text-dark">Total: {{ seccion.total }}</span>
                </div>
                <div class="table-responsive">
                  <table class="table table-sm table-striped">
                    <thead>
                      <tr>
                        <th>Estado</th>
                        <th class="text-end">Cantidad</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="fila in seccion.detalle" :key="fila.estado">
                        <td>{{ capitalizar(fila.estado) }}</td>
                        <td class="text-end">{{ fila.cantidad }}</td>
                      </tr>
                      <tr v-if="seccion.detalle.length === 0">
                        <td colspan="2" class="text-center text-muted">Sin información disponible</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <p v-if="seccion.extra" class="text-muted small mb-0">{{ seccion.extra }}</p>
                <hr v-if="seccion !== secciones[secciones.length - 1]" />
              </div>

              <p class="text-muted small mb-0">Generado el: {{ formatearFecha(resumen.generado_en) }}</p>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch, nextTick } from 'vue'
import Chart from 'chart.js/auto'
import { useReportes } from '../../composables/useReportes.js'

const { resumen, loading, error, cargarResumen, descargarPdf } = useReportes()
const descargando = ref(false)
const chartCanvas = ref(null)
let chartInstance = null

const cards = computed(() => {
  if (!resumen.value) return []
  const ganado = resumen.value.ganado?.totales || {}
  const potreros = resumen.value.potreros?.totales || {}
  const vacunaciones = resumen.value.vacunaciones?.totales || {}
  return [
    {
      titulo: 'Ganado',
      total: ganado.total ?? 0,
      detalles: (resumen.value.ganado?.por_estado || []).slice(0, 2).map(e => `${capitalizar(e.estado)}: ${e.cantidad}`)
    },
    {
      titulo: 'Potreros',
      total: potreros.total ?? 0,
      detalles: (resumen.value.potreros?.por_estado || []).slice(0, 2).map(e => `${capitalizar(e.estado)}: ${e.cantidad}`)
    },
    {
      titulo: 'Vacunaciones',
      total: vacunaciones.total ?? 0,
      detalles: [`Próximas dosis: ${resumen.value.vacunaciones?.proximas ?? 0}`]
    }
  ]
})

const secciones = computed(() => {
  if (!resumen.value) return []
  return [
    {
      titulo: 'Ganado',
      total: resumen.value.ganado?.totales?.total ?? 0,
      detalle: resumen.value.ganado?.por_estado || [],
      extra: ''
    },
    {
      titulo: 'Potreros',
      total: resumen.value.potreros?.totales?.total ?? 0,
      detalle: resumen.value.potreros?.por_estado || [],
      extra: ''
    },
    {
      titulo: 'Vacunaciones',
      total: resumen.value.vacunaciones?.totales?.total ?? 0,
      detalle: resumen.value.vacunaciones?.por_estado || [],
      extra: `Próximas dosis programadas: ${resumen.value.vacunaciones?.proximas ?? 0}`
    }
  ]
})

const capitalizar = (texto) => {
  if (!texto) return 'sin datos'
  return texto.charAt(0).toUpperCase() + texto.slice(1)
}

const formatearFecha = (fecha) => {
  if (!fecha) return 'No disponible'
  try {
    return new Date(fecha).toLocaleString()
  } catch {
    return fecha
  }
}

const descargar = async () => {
  descargando.value = true
  const result = await descargarPdf()
  descargando.value = false
  if (!result.success) {
    alert('No se pudo descargar el reporte. Intenta nuevamente.')
  }
}

const generarDatosGrafica = () => {
  if (!resumen.value) return { labels: [], datasets: [] }
  const categorias = ['ganado', 'potreros', 'vacunaciones']
  const etiquetas = []
  const datos = []

  categorias.forEach(cat => {
    const total = resumen.value[cat]?.totales?.total ?? 0
    etiquetas.push(capitalizar(cat))
    datos.push(total)
  })

  return {
    labels: etiquetas,
    datasets: [
      {
        label: 'Total registrados',
        data: datos,
        backgroundColor: ['#28a745', '#17a2b8', '#ffc107'],
        borderWidth: 1
      }
    ]
  }
}

const renderChart = async () => {
  if (!resumen.value) return

  await nextTick()

  if (!chartCanvas.value) return

  const { labels, datasets } = generarDatosGrafica()
  if (chartInstance) {
    chartInstance.data.labels = labels
    chartInstance.data.datasets = datasets
    chartInstance.update()
    return
  }

  chartInstance = new Chart(chartCanvas.value, {
    type: 'pie',
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom'
        }
      }
    }
  })
}

onMounted(() => {
  cargarResumen()
})

watch([resumen, loading], () => {
  if (!loading.value && resumen.value) {
    renderChart()
  }
})

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }
})
</script>

<style scoped>
.chart-wrapper {
  width: min(420px, 100%);
  height: 320px;
}

.card {
  border-radius: 16px;
}
</style>

