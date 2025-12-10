import { computed, onMounted, ref } from 'vue'
import Swal from 'sweetalert2'
import authService from '../../services/authService.js'
import { useGanado } from '../../composables/useGanado.js'

export function useGestionarAnimalesUsuario() {
  const busqueda = ref('')
  const filtroRaza = ref('')
  const filtroEstado = ref('')

  const { ganado: animales, loading, error, cargarGanado } = useGanado()

  const cargarAnimales = () => cargarGanado()

  const razasDisponibles = computed(() => {
    const razas = new Set()
    for (const a of animales.value) {
      if (a.raza) razas.add(a.raza)
    }
    return Array.from(razas)
  })

  const estadosDisponibles = computed(() => {
    const estados = new Set()
    for (const a of animales.value) {
      if (a.estado) estados.add(a.estado)
    }
    return Array.from(estados)
  })

  const animalesFiltrados = computed(() => {
    return animales.value.filter(a => {
      const coincideNombre = !busqueda.value || (a.nombre || '').toLowerCase().includes(busqueda.value.toLowerCase())
      const coincideRaza = !filtroRaza.value || a.raza === filtroRaza.value
      const coincideEstado = !filtroEstado.value || a.estado === filtroEstado.value
      return coincideNombre && coincideRaza && coincideEstado
    })
  })

  const capitalizar = valor => {
    if (!valor) return ''
    return valor.charAt(0).toUpperCase() + valor.slice(1)
  }

  const estadoClass = estado => {
    if (!estado) return 'bg-secondary'
    const map = {
      activo: 'bg-success',
      saludable: 'bg-success',
      enfermo: 'bg-danger',
      revision: 'bg-warning',
      vendido: 'bg-secondary'
    }
    return map[estado] || 'bg-secondary'
  }

  const verPerfilAnimal = animal => {
    const html = `
      <div class="text-start">
        <p><strong>ID:</strong> ${animal.id}</p>
        <p><strong>Nombre:</strong> ${animal.nombre || 'Sin información'}</p>
        <p><strong>Raza:</strong> ${animal.raza || 'Sin información'}</p>
        <p><strong>Edad:</strong> ${animal.edadTexto ?? 'Sin información'}</p>
        <p><strong>Peso:</strong> ${animal.peso ?? 'Sin información'}</p>
        <p><strong>Estado:</strong> ${capitalizar(animal.estado)}</p>
      </div>
    `
    Swal.fire({
      title: 'Detalle del animal',
      html,
      confirmButtonColor: '#28a745'
    })
  }

  const editarAnimal = () => {
    Swal.fire('Funcionalidad en desarrollo', 'Pronto podrás editar tus animales desde aquí.', 'info')
  }

  onMounted(() => {
    if (!authService.isAuthenticated() || !authService.isUser()) {
      globalThis.location.href = '/login'
      return
    }
    cargarGanado()
  })

  return {
    busqueda,
    filtroRaza,
    filtroEstado,
    animales,
    loading,
    error,
    cargarGanado,
    cargarAnimales,
    razasDisponibles,
    estadosDisponibles,
    animalesFiltrados,
    capitalizar,
    estadoClass,
    verPerfilAnimal,
    editarAnimal
  }
}