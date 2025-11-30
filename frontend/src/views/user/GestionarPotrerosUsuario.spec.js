import { mount } from '@vue/test-utils'
import { beforeEach, vi, describe, it, expect } from 'vitest'
import GestionarPotrerosUsuario from './GestionarPotrerosUsuario.vue'
import { useGestionarPotrerosUsuario } from '../../assets/js/gestionar-potreros-usuario.js'

vi.mock('../../assets/js/gestionar-potreros-usuario.js', () => ({
  useGestionarPotrerosUsuario: vi.fn(() => ({
    potreros: { value: [] },
    loading: { value: false },
    error: { value: null },
    cargarPotreros: vi.fn(),
    busqueda: { value: '' },
    filtroEstado: { value: '' },
    filtroPasto: { value: '' },
    estadosDisponibles: { value: [] },
    tiposPasto: { value: [] },
    potrerosFiltrados: { value: [] },
    capitalizar: vi.fn((s) => s),
    formatearFecha: vi.fn((d) => d)
  }))
}))

describe('GestionarPotrerosUsuario.vue', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should mount successfully', () => {
    wrapper = mount(GestionarPotrerosUsuario)
    expect(wrapper.exists()).toBe(true)
  })

  it('should render the title', () => {
    wrapper = mount(GestionarPotrerosUsuario)
    expect(wrapper.text()).toContain('Mis Potreros')
  })

  it('should call useGestionarPotrerosUsuario composable', () => {
    mount(GestionarPotrerosUsuario)
    expect(useGestionarPotrerosUsuario).toHaveBeenCalled()
  })
})

