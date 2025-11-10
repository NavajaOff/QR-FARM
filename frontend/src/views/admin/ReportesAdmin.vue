<template>
  <div class="container-fluid py-4">
    <div class="d-flex flex-wrap justify-content-between align-items-center mb-4">
      <div>
        <h2 class="mb-1">Reportes y Analítica</h2>
        <p class="text-muted mb-0">Resumen consolidado del sistema QR-FARM</p>
      </div>
      <button class="btn btn-danger" @click="descargarReporte" :disabled="descargando">
        <span v-if="descargando" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
        <i v-else class="fas fa-file-download me-2"></i>
        Descargar PDF
      </button>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status"></div>
      <p class="mt-3 mb-0">Cargando información...</p>
    </div>

    <div v-else>
      <div v-if="error" class="alert alert-danger" role="alert">
        {{ error }}
      </div>

      <template v-if="resumen">
        <div class="row g-3">
          <div class="col-12 col-sm-6 col-xl-3" v-for="card in summaryCards" :key="card.titulo">
            <div class="card shadow-sm h-100">
              <div class="card-body">
                <h5 class="card-title mb-2">{{ card.titulo }}</h5>
                <p class="display-6 fw-bold mb-2">{{ card.total }}</p>
                <p class="text-muted small mb-0" v-for="detalle in card.detalles" :key="detalle">
                  {{ detalle }}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div class="card shadow-sm mt-4">
          <div class="card-body">
            <h4 class="card-title mb-4">Detalle por módulo</h4>

            <div v-for="seccion in secciones" :key="seccion.titulo" class="mb-4">
              <div class="d-flex justify-content-between align-items-center mb-2">
                <h5 class="mb-0">{{ seccion.titulo }}</h5>
                <span class="badge bg-light text-dark">Total: {{ seccion.total }}</span>
              </div>

              <div class="table-responsive">
                <table class="table table-striped table-sm">
                  <caption class="visually-hidden">Tabla de detalle administrativo de reportes mostrando estado y cantidad para usuarios, ganado, potreros y vacunaciones</caption>
                  <thead>
                    <tr>
                      <th>Estado</th>
                      <th class="text-end">Cantidad</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="detalle in seccion.detalle" :key="detalle.estado">
                      <td class="text-capitalize">{{ formatearEstado(detalle.estado) }}</td>
                      <td class="text-end">{{ detalle.cantidad }}</td>
                    </tr>
                    <tr v-if="!seccion.detalle.length">
                      <td colspan="2" class="text-center text-muted">Sin registros</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <p v-if="seccion.extra" class="text-muted small mb-0">{{ seccion.extra }}</p>
              <hr v-if="seccion !== secciones[secciones.length - 1]" />
            </div>
          </div>
        </div>

        <p class="text-muted small mt-3 mb-0">
          Última actualización: {{ formatFecha(resumen.generado_en) }}
        </p>
      </template>
    </div>
  </div>
</template>

<script>
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
</script>

<style scoped>
.card-title {
  font-weight: 600;
}

table thead th {
  background-color: #f8f9fa;
}
</style>

