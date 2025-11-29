import { beforeEach, vi, describe, it, expect } from 'vitest'
import { useGestionarPotrerosUsuario } from './gestionar-potreros-usuario.js'
import { usePotreros } from '../../composables/usePotreros.js'

vi.mock('../../composables/usePotreros.js', () => ({
  usePotreros: vi.fn()
}))

describe('useGestionarPotrerosUsuario', () => {
  let mockCargarPotreros
  let mockPotreros
  let mockLoading
  let mockError

  beforeEach(() => {
    vi.clearAllMocks()
    
    mockPotreros = { value: [] }
    mockLoading = { value: false }
    mockError = { value: null }
    mockCargarPotreros = vi.fn()

    usePotreros.mockReturnValue({
      potreros: mockPotreros,
      loading: mockLoading,
      error: mockError,
      cargarPotreros: mockCargarPotreros
    })
  })

  it('should export useGestionarPotrerosUsuario function', () => {
    expect(useGestionarPotrerosUsuario).toBeDefined()
    expect(typeof useGestionarPotrerosUsuario).toBe('function')
  })

  it('should initialize with default values', () => {
    const result = useGestionarPotrerosUsuario()
    
    expect(result.busqueda.value).toBe('')
    expect(result.filtroEstado.value).toBe('')
    expect(result.filtroPasto.value).toBe('')
  })

  it('should call cargarPotreros on mount', () => {
    useGestionarPotrerosUsuario()
    expect(mockCargarPotreros).toHaveBeenCalled()
  })

  describe('estadosDisponibles computed', () => {
    it('should return empty array when no potreros', () => {
      mockPotreros.value = []
      const result = useGestionarPotrerosUsuario()
      
      expect(result.estadosDisponibles.value).toEqual([])
    })

    it('should extract unique estados from potreros', () => {
      mockPotreros.value = [
        { estado: 'disponible' },
        { estado: 'ocupado' },
        { estado: 'disponible' }
      ]
      const result = useGestionarPotrerosUsuario()
      
      expect(result.estadosDisponibles.value).toContain('disponible')
      expect(result.estadosDisponibles.value).toContain('ocupado')
      expect(result.estadosDisponibles.value).toHaveLength(2)
    })
  })

  describe('tiposPasto computed', () => {
    it('should return empty array when no potreros', () => {
      mockPotreros.value = []
      const result = useGestionarPotrerosUsuario()
      
      expect(result.tiposPasto.value).toEqual([])
    })

    it('should extract tipos from tipo_pasto_nombre', () => {
      mockPotreros.value = [
        { tipo_pasto_nombre: 'Bermuda' },
        { tipo_pasto_nombre: 'Raygrass' },
        { tipo_pasto_nombre: 'Bermuda' }
      ]
      const result = useGestionarPotrerosUsuario()
      
      expect(result.tiposPasto.value).toContain('Bermuda')
      expect(result.tiposPasto.value).toContain('Raygrass')
      expect(result.tiposPasto.value).toHaveLength(2)
    })

    it('should extract tipos from tipo_pasto when tipo_pasto_nombre not available', () => {
      mockPotreros.value = [
        { tipo_pasto: 'Bermuda' },
        { tipo_pasto_nombre: 'Raygrass' }
      ]
      const result = useGestionarPotrerosUsuario()
      
      expect(result.tiposPasto.value).toContain('Bermuda')
      expect(result.tiposPasto.value).toContain('Raygrass')
    })
  })

  describe('potrerosFiltrados computed', () => {
    it('should return all potreros when no filters', () => {
      mockPotreros.value = [
        { nombre: 'Potrero 1', estado: 'disponible', tipo_pasto: 'Bermuda' },
        { nombre: 'Potrero 2', estado: 'ocupado', tipo_pasto: 'Raygrass' }
      ]
      const result = useGestionarPotrerosUsuario()
      
      expect(result.potrerosFiltrados.value).toHaveLength(2)
    })

    it('should filter by nombre', () => {
      mockPotreros.value = [
        { nombre: 'Potrero A', estado: 'disponible' },
        { nombre: 'Potrero B', estado: 'ocupado' }
      ]
      const result = useGestionarPotrerosUsuario()
      result.busqueda.value = 'A'
      
      expect(result.potrerosFiltrados.value).toHaveLength(1)
      expect(result.potrerosFiltrados.value[0].nombre).toBe('Potrero A')
    })

    it('should filter by estado', () => {
      mockPotreros.value = [
        { nombre: 'Potrero 1', estado: 'disponible' },
        { nombre: 'Potrero 2', estado: 'ocupado' }
      ]
      const result = useGestionarPotrerosUsuario()
      result.filtroEstado.value = 'disponible'
      
      expect(result.potrerosFiltrados.value).toHaveLength(1)
      expect(result.potrerosFiltrados.value[0].estado).toBe('disponible')
    })

    it('should filter by tipo_pasto', () => {
      mockPotreros.value = [
        { nombre: 'Potrero 1', tipo_pasto: 'Bermuda' },
        { nombre: 'Potrero 2', tipo_pasto: 'Raygrass' }
      ]
      const result = useGestionarPotrerosUsuario()
      result.filtroPasto.value = 'Bermuda'
      
      expect(result.potrerosFiltrados.value).toHaveLength(1)
      expect(result.potrerosFiltrados.value[0].tipo_pasto).toBe('Bermuda')
    })

    it('should filter by tipo_pasto_nombre', () => {
      mockPotreros.value = [
        { nombre: 'Potrero 1', tipo_pasto_nombre: 'Bermuda' },
        { nombre: 'Potrero 2', tipo_pasto_nombre: 'Raygrass' }
      ]
      const result = useGestionarPotrerosUsuario()
      result.filtroPasto.value = 'Bermuda'
      
      expect(result.potrerosFiltrados.value).toHaveLength(1)
      expect(result.potrerosFiltrados.value[0].tipo_pasto_nombre).toBe('Bermuda')
    })

    it('should filter by multiple criteria', () => {
      mockPotreros.value = [
        { nombre: 'Potrero A', estado: 'disponible', tipo_pasto: 'Bermuda' },
        { nombre: 'Potrero B', estado: 'disponible', tipo_pasto: 'Raygrass' },
        { nombre: 'Potrero C', estado: 'ocupado', tipo_pasto: 'Bermuda' }
      ]
      const result = useGestionarPotrerosUsuario()
      result.busqueda.value = 'A'
      result.filtroEstado.value = 'disponible'
      result.filtroPasto.value = 'Bermuda'
      
      expect(result.potrerosFiltrados.value).toHaveLength(1)
      expect(result.potrerosFiltrados.value[0].nombre).toBe('Potrero A')
    })
  })

  describe('capitalizar', () => {
    it('should capitalize first letter', () => {
      const result = useGestionarPotrerosUsuario()
      
      expect(result.capitalizar('disponible')).toBe('Disponible')
      expect(result.capitalizar('BERMUDA')).toBe('BERMUDA')
    })

    it('should return empty string for null/undefined', () => {
      const result = useGestionarPotrerosUsuario()
      
      expect(result.capitalizar(null)).toBe('')
      expect(result.capitalizar(undefined)).toBe('')
      expect(result.capitalizar('')).toBe('')
    })

    it('should handle non-string values', () => {
      const result = useGestionarPotrerosUsuario()
      
      expect(result.capitalizar(123)).toBe('123')
      expect(typeof result.capitalizar(123)).toBe('string')
    })
  })

  describe('formatearFecha', () => {
    it('should format valid date', () => {
      const result = useGestionarPotrerosUsuario()
      const dateStr = '2024-01-15T00:00:00Z'
      
      const formatted = result.formatearFecha(dateStr)
      
      expect(formatted).toBeTruthy()
      expect(typeof formatted).toBe('string')
    })

    it('should return "No registrada" for null/undefined', () => {
      const result = useGestionarPotrerosUsuario()
      
      expect(result.formatearFecha(null)).toBe('No registrada')
      expect(result.formatearFecha(undefined)).toBe('No registrada')
      expect(result.formatearFecha('')).toBe('No registrada')
    })

    it('should handle invalid date gracefully', () => {
      const result = useGestionarPotrerosUsuario()
      const invalidDate = 'invalid-date-string'
      
      const formatted = result.formatearFecha(invalidDate)
      
      expect(formatted).toBe(invalidDate)
    })
  })
})

