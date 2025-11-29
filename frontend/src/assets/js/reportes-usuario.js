import { computed, onMounted, onUnmounted, ref, watch, nextTick } from 'vue'
import Chart from 'chart.js/auto'
import { useReportes } from '../../composables/useReportes.js'

/**
 * Componente ReportesUsuario
 * Maneja la lógica de reportes para usuarios
 */
const { resumen, loading, error, cargarResumen, descargarPdf } = useReportes()
const descargando = ref(false)
const chartCanvas = ref(null)
let chartInstance = null

/**
 * Datos de las tarjetas de resumen
 */
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

/**
 * Secciones de detalle del reporte
 */
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

/**
 * Capitaliza la primera letra de un texto
 * @param {string} texto - Texto a capitalizar
 * @returns {string} Texto capitalizado
 */
const capitalizar = (texto) => {
  if (!texto) return 'sin datos'
  return texto.charAt(0).toUpperCase() + texto.slice(1)
}

/**
 * Formatea una fecha para mostrar
 * @param {string} fecha - Fecha en formato string
 * @returns {string} Fecha formateada o 'No disponible'
 */
const formatearFecha = (fecha) => {
  if (!fecha) return 'No disponible'
  try {
    return new Date(fecha).toLocaleString()
  } catch {
    return fecha
  }
}

/**
 * Descarga el reporte en PDF
 */
const descargar = async () => {
  descargando.value = true
  const result = await descargarPdf()
  descargando.value = false
  if (!result.success) {
    alert('No se pudo descargar el reporte. Intenta nuevamente.')
  }
}

/**
 * Genera los datos para el gráfico
 * @returns {Object} Datos del gráfico
 */
const generarDatosGrafica = () => {
  if (!resumen.value) return { labels: [], datasets: [] }
  const categorias = ['ganado', 'potreros', 'vacunaciones']
  const etiquetas = []
  const datos = []

  for (const cat of categorias) {
    const total = resumen.value[cat]?.totales?.total ?? 0
    etiquetas.push(capitalizar(cat))
    datos.push(total)
  }

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

/**
 * Renderiza el gráfico de distribución
 */
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

export default {
  name: "ReportesUsuario",
  setup() {
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

    return {
      resumen,
      loading,
      error,
      descargando,
      chartCanvas,
      cards,
      secciones,
      capitalizar,
      formatearFecha,
      descargar
    }
  }
}