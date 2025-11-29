import { computed, onMounted, onUnmounted, ref, watch, nextTick } from 'vue'
import Chart from 'chart.js/auto'
import { useReportes } from '../../composables/useReportes.js'

export default {
  name: 'ReportesAdmin',
  setup() {
    const { resumen, loading, error, cargarResumen, descargarPdf } = useReportes()
    const descargando = ref(false)
    const trendCanvas = ref(null)
    let trendChart = null

    const metricConfig = [
      { clave: 'usuarios', titulo: 'Usuarios', color: '#0d6efd' },
      { clave: 'ganado', titulo: 'Ganado', color: '#198754' },
      { clave: 'potreros', titulo: 'Potreros', color: '#ffc107' },
      { clave: 'vacunaciones', titulo: 'Vacunaciones', color: '#fd7e14' }
    ]

    const construirDetalles = (clave, resumen, usuarios, vacunaciones) => {
      if (clave === 'usuarios') {
        return [
          `Activos: ${usuarios.totales?.activos ?? 0}`,
          `Inactivos: ${usuarios.totales?.inactivos ?? 0}`
        ]
      }
      if (clave === 'vacunaciones') {
        return [
          `Próximas dosis: ${vacunaciones.proximas ?? 0}`
        ]
      }
      const lista = resumen[clave]?.por_estado || []
      return lista.slice(0, 2).map(e => `${formatearEstado(e.estado)}: ${e.cantidad}`)
    }

    onMounted(async () => {
      await cargarResumen()
      await nextTick()
      renderTrendChart()
    })

    const summaryCards = computed(() => {
      if (!resumen.value) return []

      const usuarios = resumen.value.usuarios || {}
      const vacunaciones = resumen.value.vacunaciones || {}
      const tendencias = resumen.value.tendencias || {}

      return metricConfig.map((config) => {
        const totales = resumen.value[config.clave]?.totales || {}
        const total = totales.total ?? 0
        const tendencia = tendencias[config.clave] || {}
        return {
          ...config,
          total,
          detalles: construirDetalles(config.clave, resumen.value, usuarios, vacunaciones),
          variacion: tendencia.variacion ?? 0,
          variacionAbsoluta: tendencia.variacion_absoluta ?? 0,
          promedio: tendencia.promedio_diario ?? 0,
          serie: tendencia.serie || []
        }
      })
    })

    const secciones = computed(() => {
      if (!resumen.value) return []

      return [
        {
          clave: 'usuarios',
          titulo: 'Usuarios',
          total: resumen.value.usuarios?.totales?.total ?? 0,
          detalle: resumen.value.usuarios?.por_estado || [],
          extra: ''
        },
        {
          clave: 'ganado',
          titulo: 'Ganado',
          total: resumen.value.ganado?.totales?.total ?? 0,
          detalle: resumen.value.ganado?.por_estado || [],
          extra: ''
        },
        {
          clave: 'potreros',
          titulo: 'Potreros',
          total: resumen.value.potreros?.totales?.total ?? 0,
          detalle: resumen.value.potreros?.por_estado || [],
          extra: ''
        },
        {
          clave: 'vacunaciones',
          titulo: 'Vacunaciones',
          total: resumen.value.vacunaciones?.totales?.total ?? 0,
          detalle: resumen.value.vacunaciones?.por_estado || [],
          extra: `Próximas dosis programadas: ${resumen.value.vacunaciones?.proximas ?? 0}`
        }
      ]
    })

    const formatearEstado = (estado) => {
      if (!estado) return 'sin estado'
      return estado.replace('_', ' ')
    }

    const formatBadgeClass = (valor) => {
      if (valor > 0) return 'badge-soft-success'
      if (valor < 0) return 'badge-soft-danger'
      return 'badge-soft-muted'
    }

    const formatPromedio = (valor) => {
      if (typeof valor !== 'number' || Number.isNaN(valor)) return '0'
      return Number.isInteger(valor) ? String(valor) : valor.toFixed(1)
    }

    const formatVariacion = (valor) => {
      if (typeof valor !== 'number' || Number.isNaN(valor)) return '0.0'
      return valor.toFixed(1)
    }

    const trendInsights = computed(() => {
      if (!resumen.value?.tendencias) return []
      return summaryCards.value.map(card => ({
        titulo: card.titulo,
        color: card.color,
        promedio: card.promedio ?? 0,
        variacion: card.variacion ?? 0
      }))
    })

    const buildTrendChartData = () => {
      if (!resumen.value?.tendencias) {
        console.debug('[ReportesAdmin] Tendencias no disponibles todavía')
        return { labels: [], datasets: [] }
      }

      const labelsSet = new Set()
      const tendencias = resumen.value.tendencias

      for (const config of metricConfig) {
        const serie = tendencias[config.clave]?.serie || []
        for (const punto of serie) {
          if (punto.fecha) {
            labelsSet.add(punto.fecha)
          }
        }
      }

      const labels = Array.from(labelsSet).sort()

      const datasets = metricConfig.map((config) => {
        const serie = tendencias[config.clave]?.serie || []
        const mapa = new Map(serie.map(p => [p.fecha, p.total]))

        return {
          label: config.titulo,
          data: labels.map(label => mapa.get(label) ?? 0),
          borderColor: config.color,
          backgroundColor: `${config.color}20`,
          tension: 0.35,
          fill: true,
          pointRadius: 4,
          pointHoverRadius: 6,
          borderWidth: 2
        }
      })

      return { labels, datasets }
    }

    const renderTrendChart = async () => {
      if (!trendCanvas.value) return

      await nextTick()

      const { labels, datasets } = buildTrendChartData()

      if (!labels.length) {
        console.debug('[ReportesAdmin] No hay etiquetas para la gráfica')
        if (trendChart) {
          trendChart.destroy()
          trendChart = null
        }
        return
      }

      if (trendChart) {
        console.debug('[ReportesAdmin] Actualizando gráfica existente', labels, datasets)
        trendChart.data.labels = labels
        trendChart.data.datasets = datasets
        trendChart.update()
        return
      }

      trendChart = new Chart(trendCanvas.value, {
        type: 'line',
        data: { labels, datasets },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: true,
              position: 'top'
            },
            tooltip: {
              mode: 'index',
              intersect: false,
              callbacks: {
                label: (context) => {
                  const label = context.dataset.label || ''
                  const rawValue = context.raw ?? 0
                  let value
                  if (rawValue == null) {
                    value = '0'
                  } else if (typeof rawValue === 'object') {
                    value = JSON.stringify(rawValue)
                  } else {
                    value = rawValue.toString()
                  }
                  return `${label}: ${value}`
                }
              }
            }
          },
          scales: {
            x: {
              title: {
                display: true,
                text: 'Fecha'
              }
            },
            y: {
              title: {
                display: true,
                text: 'Total'
              },
              beginAtZero: true,
              ticks: {
                precision: 0
              }
            }
          }
        }
      })
      console.debug('[ReportesAdmin] Gráfica creada', labels, datasets)
    }

    watch(
      [() => resumen.value?.tendencias, () => trendCanvas.value, () => loading.value],
      async () => {
        if (loading.value) return
        await nextTick()
        if (resumen.value?.tendencias && trendCanvas.value) {
          renderTrendChart()
        }
      },
      { deep: true, immediate: true, flush: 'post' }
    )

    onUnmounted(() => {
      if (trendChart) {
        trendChart.destroy()
        trendChart = null
      }
    })

    const formatFecha = (fechaISO) => {
      if (!fechaISO) return 'No disponible'
      try {
        return new Date(fechaISO).toLocaleString()
      } catch (err) {
        return fechaISO
      }
    }

    const descargarReporte = async () => {
      descargando.value = true
      const resultado = await descargarPdf()
      descargando.value = false

      if (!resultado.success) {
        alert('No fue posible descargar el PDF: ' + (resultado.message || 'Error desconocido'))
      }
    }

    return {
      resumen,
      loading,
      error,
      summaryCards,
      secciones,
      trendCanvas,
      trendInsights,
      formatearEstado,
      formatBadgeClass,
      formatPromedio,
      formatVariacion,
      formatFecha,
      descargarReporte,
      descargando
    }
  }
}