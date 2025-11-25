import { computed, onMounted, ref } from 'vue'
import { usePotreros } from '../../composables/usePotreros.js'

export function useGestionarPotrerosUsuario() {
  const { potreros, loading, error, cargarPotreros } = usePotreros()
  const busqueda = ref('')
  const filtroEstado = ref('')
  const filtroPasto = ref('')

  const estadosDisponibles = computed(() => {
    const estados = new Set()
    potreros.value.forEach(p => {
      if (p.estado) estados.add(p.estado)
    })
    return Array.from(estados)
  })

  const tiposPasto = computed(() => {
    const tipos = new Set()
    potreros.value.forEach(p => {
      if (p.tipo_pasto_nombre) tipos.add(p.tipo_pasto_nombre)
      else if (p.tipo_pasto) tipos.add(p.tipo_pasto)
    })
    return Array.from(tipos)
  })

  const potrerosFiltrados = computed(() => {
    return potreros.value.filter(p => {
      const coincideBusqueda =
        !busqueda.value ||
        (p.nombre && p.nombre.toLowerCase().includes(busqueda.value.toLowerCase()))
      const coincideEstado = !filtroEstado.value || p.estado === filtroEstado.value
      const coincidePasto =
        !filtroPasto.value ||
        p.tipo_pasto === filtroPasto.value ||
        p.tipo_pasto_nombre === filtroPasto.value

      return coincideBusqueda && coincideEstado && coincidePasto
    })
  })

  const capitalizar = (texto) => {
    if (!texto) return ''
    return texto.toString().charAt(0).toUpperCase() + texto.toString().slice(1)
  }

  const formatearFecha = (fecha) => {
    if (!fecha) return 'No registrada'
    try {
      return new Date(fecha).toLocaleDateString()
    } catch {
      return fecha
    }
  }

  onMounted(() => {
    cargarPotreros()
  })

  return {
    potreros,
    loading,
    error,
    cargarPotreros,
    busqueda,
    filtroEstado,
    filtroPasto,
    estadosDisponibles,
    tiposPasto,
    potrerosFiltrados,
    capitalizar,
    formatearFecha
  }
}