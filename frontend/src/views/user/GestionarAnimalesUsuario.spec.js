import { mount } from '@vue/test-utils'
import { beforeEach, vi, describe, it, expect } from 'vitest'
import GestionarAnimalesUsuario from './GestionarAnimalesUsuario.vue'
import { useGestionarAnimalesUsuario } from '../../assets/js/gestionar-animales-usuario.js'

vi.mock('../../assets/js/gestionar-animales-usuario.js', () => ({
  useGestionarAnimalesUsuario: vi.fn(() => ({
    busqueda: { value: '' },
    filtroRaza: { value: '' },
    filtroEstado: { value: '' },
    animales: { value: [] },
    loading: { value: false },
    error: { value: null },
    cargarAnimales: vi.fn(),
    razasDisponibles: { value: [] },
    estadosDisponibles: { value: [] },
    animalesFiltrados: { value: [] },
    capitalizar: vi.fn((s) => s),
    estadoClass: vi.fn(() => ''),
    verPerfilAnimal: vi.fn(),
    editarAnimal: vi.fn()
  }))
}))

describe('GestionarAnimalesUsuario.vue', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should mount successfully', () => {
    wrapper = mount(GestionarAnimalesUsuario)
    expect(wrapper.exists()).toBe(true)
  })

  it('should render the title', () => {
    wrapper = mount(GestionarAnimalesUsuario)
    expect(wrapper.text()).toContain('Gestionar Animales')
  })

  it('should call useGestionarAnimalesUsuario composable', () => {
    mount(GestionarAnimalesUsuario)
    expect(useGestionarAnimalesUsuario).toHaveBeenCalled()
  })
})

