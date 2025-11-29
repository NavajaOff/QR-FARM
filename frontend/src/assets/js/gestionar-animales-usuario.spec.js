import { beforeEach, vi, describe, it, expect } from 'vitest'
import { useGestionarAnimalesUsuario } from './gestionar-animales-usuario.js'
import { useGanado } from '../../composables/useGanado.js'
import authService from '../../services/authService.js'
import Swal from 'sweetalert2'

vi.mock('../../composables/useGanado.js', () => ({
  useGanado: vi.fn()
}))

vi.mock('../../services/authService.js', () => ({
  default: {
    isAuthenticated: vi.fn(),
    isUser: vi.fn()
  }
}))

vi.mock('sweetalert2', () => ({
  default: {
    fire: vi.fn()
  }
}))

describe('useGestionarAnimalesUsuario', () => {
  let mockCargarGanado
  let mockAnimales
  let mockLoading
  let mockError

  beforeEach(() => {
    vi.clearAllMocks()
    
    mockAnimales = { value: [] }
    mockLoading = { value: false }
    mockError = { value: null }
    mockCargarGanado = vi.fn()

    useGanado.mockReturnValue({
      ganado: mockAnimales,
      loading: mockLoading,
      error: mockError,
      cargarGanado: mockCargarGanado
    })

    globalThis.location = { href: '' }
  })

  it('should export useGestionarAnimalesUsuario function', () => {
    expect(useGestionarAnimalesUsuario).toBeDefined()
    expect(typeof useGestionarAnimalesUsuario).toBe('function')
  })

  it('should initialize with default values', () => {
    const result = useGestionarAnimalesUsuario()
    
    expect(result.busqueda.value).toBe('')
    expect(result.filtroRaza.value).toBe('')
    expect(result.filtroEstado.value).toBe('')
  })

  it('should call cargarGanado on mount when authenticated', () => {
    authService.isAuthenticated.mockReturnValue(true)
    authService.isUser.mockReturnValue(true)

    useGestionarAnimalesUsuario()

    expect(mockCargarGanado).toHaveBeenCalled()
  })

  it('should redirect to login when not authenticated', () => {
    authService.isAuthenticated.mockReturnValue(false)

    useGestionarAnimalesUsuario()

    expect(globalThis.location.href).toBe('/login')
    expect(mockCargarGanado).not.toHaveBeenCalled()
  })

  it('should redirect to login when not user', () => {
    authService.isAuthenticated.mockReturnValue(true)
    authService.isUser.mockReturnValue(false)

    useGestionarAnimalesUsuario()

    expect(globalThis.location.href).toBe('/login')
    expect(mockCargarGanado).not.toHaveBeenCalled()
  })

  describe('razasDisponibles computed', () => {
    it('should return empty array when no animals', () => {
      mockAnimales.value = []
      const result = useGestionarAnimalesUsuario()
      
      expect(result.razasDisponibles.value).toEqual([])
    })

    it('should extract unique razas from animals', () => {
      mockAnimales.value = [
        { raza: 'Holstein' },
        { raza: 'Angus' },
        { raza: 'Holstein' },
        { nombre: 'Sin raza' }
      ]
      const result = useGestionarAnimalesUsuario()
      
      expect(result.razasDisponibles.value).toContain('Holstein')
      expect(result.razasDisponibles.value).toContain('Angus')
      expect(result.razasDisponibles.value).toHaveLength(2)
    })
  })

  describe('estadosDisponibles computed', () => {
    it('should return empty array when no animals', () => {
      mockAnimales.value = []
      const result = useGestionarAnimalesUsuario()
      
      expect(result.estadosDisponibles.value).toEqual([])
    })

    it('should extract unique estados from animals', () => {
      mockAnimales.value = [
        { estado: 'saludable' },
        { estado: 'enfermo' },
        { estado: 'saludable' }
      ]
      const result = useGestionarAnimalesUsuario()
      
      expect(result.estadosDisponibles.value).toContain('saludable')
      expect(result.estadosDisponibles.value).toContain('enfermo')
      expect(result.estadosDisponibles.value).toHaveLength(2)
    })
  })

  describe('animalesFiltrados computed', () => {
    it('should return all animals when no filters', () => {
      mockAnimales.value = [
        { nombre: 'Animal 1', raza: 'Holstein', estado: 'saludable' },
        { nombre: 'Animal 2', raza: 'Angus', estado: 'enfermo' }
      ]
      const result = useGestionarAnimalesUsuario()
      
      expect(result.animalesFiltrados.value).toHaveLength(2)
    })

    it('should filter by nombre', () => {
      mockAnimales.value = [
        { nombre: 'Vaca 1', raza: 'Holstein', estado: 'saludable' },
        { nombre: 'Toro 1', raza: 'Angus', estado: 'enfermo' }
      ]
      const result = useGestionarAnimalesUsuario()
      result.busqueda.value = 'vaca'
      
      expect(result.animalesFiltrados.value).toHaveLength(1)
      expect(result.animalesFiltrados.value[0].nombre).toBe('Vaca 1')
    })

    it('should filter by raza', () => {
      mockAnimales.value = [
        { nombre: 'Animal 1', raza: 'Holstein', estado: 'saludable' },
        { nombre: 'Animal 2', raza: 'Angus', estado: 'enfermo' }
      ]
      const result = useGestionarAnimalesUsuario()
      result.filtroRaza.value = 'Holstein'
      
      expect(result.animalesFiltrados.value).toHaveLength(1)
      expect(result.animalesFiltrados.value[0].raza).toBe('Holstein')
    })

    it('should filter by estado', () => {
      mockAnimales.value = [
        { nombre: 'Animal 1', raza: 'Holstein', estado: 'saludable' },
        { nombre: 'Animal 2', raza: 'Angus', estado: 'enfermo' }
      ]
      const result = useGestionarAnimalesUsuario()
      result.filtroEstado.value = 'saludable'
      
      expect(result.animalesFiltrados.value).toHaveLength(1)
      expect(result.animalesFiltrados.value[0].estado).toBe('saludable')
    })

    it('should filter by multiple criteria', () => {
      mockAnimales.value = [
        { nombre: 'Vaca 1', raza: 'Holstein', estado: 'saludable' },
        { nombre: 'Vaca 2', raza: 'Holstein', estado: 'enfermo' },
        { nombre: 'Toro 1', raza: 'Angus', estado: 'saludable' }
      ]
      const result = useGestionarAnimalesUsuario()
      result.busqueda.value = 'vaca'
      result.filtroRaza.value = 'Holstein'
      result.filtroEstado.value = 'saludable'
      
      expect(result.animalesFiltrados.value).toHaveLength(1)
      expect(result.animalesFiltrados.value[0].nombre).toBe('Vaca 1')
    })
  })

  describe('capitalizar', () => {
    it('should capitalize first letter', () => {
      const result = useGestionarAnimalesUsuario()
      
      expect(result.capitalizar('holstein')).toBe('Holstein')
      expect(result.capitalizar('SALUDABLE')).toBe('SALUDABLE')
    })

    it('should return empty string for null/undefined', () => {
      const result = useGestionarAnimalesUsuario()
      
      expect(result.capitalizar(null)).toBe('')
      expect(result.capitalizar(undefined)).toBe('')
      expect(result.capitalizar('')).toBe('')
    })
  })

  describe('estadoClass', () => {
    it('should return correct class for estado', () => {
      const result = useGestionarAnimalesUsuario()
      
      expect(result.estadoClass('activo')).toBe('bg-success')
      expect(result.estadoClass('saludable')).toBe('bg-success')
      expect(result.estadoClass('enfermo')).toBe('bg-danger')
      expect(result.estadoClass('revision')).toBe('bg-warning')
      expect(result.estadoClass('vendido')).toBe('bg-secondary')
    })

    it('should return default class for unknown estado', () => {
      const result = useGestionarAnimalesUsuario()
      
      expect(result.estadoClass('unknown')).toBe('bg-secondary')
      expect(result.estadoClass(null)).toBe('bg-secondary')
      expect(result.estadoClass(undefined)).toBe('bg-secondary')
    })
  })

  describe('verPerfilAnimal', () => {
    it('should show Swal with animal details', () => {
      const result = useGestionarAnimalesUsuario()
      const animal = {
        id: 1,
        nombre: 'Vaca 1',
        raza: 'Holstein',
        edad: 3,
        peso: 450,
        estado: 'saludable'
      }

      result.verPerfilAnimal(animal)

      expect(Swal.fire).toHaveBeenCalled()
      const callArgs = Swal.fire.mock.calls[0][0]
      expect(callArgs.title).toBe('Detalle del animal')
      expect(callArgs.html).toContain('Vaca 1')
      expect(callArgs.html).toContain('Holstein')
    })

    it('should handle missing animal data', () => {
      const result = useGestionarAnimalesUsuario()
      const animal = {
        id: 1,
        nombre: null,
        raza: null,
        edad: null,
        peso: null,
        estado: null
      }

      result.verPerfilAnimal(animal)

      expect(Swal.fire).toHaveBeenCalled()
      const callArgs = Swal.fire.mock.calls[0][0]
      expect(callArgs.html).toContain('Sin información')
    })
  })

  describe('editarAnimal', () => {
    it('should show info message', () => {
      const result = useGestionarAnimalesUsuario()

      result.editarAnimal()

      expect(Swal.fire).toHaveBeenCalledWith(
        'Funcionalidad en desarrollo',
        'Pronto podrás editar tus animales desde aquí.',
        'info'
      )
    })
  })

  describe('cargarAnimales', () => {
    it('should call cargarGanado', () => {
      const result = useGestionarAnimalesUsuario()

      result.cargarAnimales()

      expect(mockCargarGanado).toHaveBeenCalled()
    })
  })
})

