import { computed, onMounted, ref } from 'vue'
import { useReportes } from '../../composables/useReportes.js'

export default {
  name: 'ReportesAdmin',
  setup() {
    const { resumen, loading, error, cargarResumen, descargarPdf } = useReportes()
    const descargando = ref(false)

    onMounted(() => {
      cargarResumen()
    })

    const summaryCards = computed(() => {
      if (!resumen.value) return []

      const usuarios = resumen.value.usuarios || {}
      const ganado = resumen.value.ganado || {}
      const potreros = resumen.value.potreros || {}
      const vacunaciones = resumen.value.vacunaciones || {}

      return [
        {
          titulo: 'Usuarios',
          total: usuarios.totales?.total ?? 0,
          detalles: [
            `Activos: ${usuarios.totales?.activos ?? 0}`,
            `Inactivos: ${usuarios.totales?.inactivos ?? 0}`
          ]
        },
        {
          titulo: 'Ganado',
          total: ganado.totales?.total ?? 0,
          detalles: ganado.por_estado?.slice(0, 2).map(e => `${e.estado}: ${e.cantidad}`) || []
        },
        {
          titulo: 'Potreros',
          total: potreros.totales?.total ?? 0,
          detalles: potreros.por_estado?.slice(0, 2).map(e => `${e.estado}: ${e.cantidad}`) || []
        },
        {
          titulo: 'Vacunaciones',
          total: vacunaciones.totales?.total ?? 0,
          detalles: [
            `Próximas dosis: ${vacunaciones.proximas ?? 0}`
          ]
        }
      ]
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
      formatearEstado,
      formatFecha,
      descargarReporte,
      descargando
    }
  }
}