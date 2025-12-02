import { vi } from 'vitest'
import dashboardContentUsuario from './dashboard-content-usuario.js'
import authService from '../../services/authService.js'
import { ganadoAPI, potreroAPI, vacunacionAPI } from '../../services/api.js'

vi.mock('../../services/authService.js')
vi.mock('../../services/api.js')

describe('dashboard-content-usuario.js', () => {
  let component

  beforeEach(() => {
    component = { ...dashboardContentUsuario }
    component.data = component.data.bind(component)
    component.methods = { ...component.methods }
    Object.setPrototypeOf(component.methods, component)
    component.estadisticas = component.data().estadisticas
    component.userInfo = component.data().userInfo
  })

  it('should initialize data correctly', () => {
    const data = component.data()
    expect(data.estadisticas).toEqual({
      ganado: 0,
      potreros: 0,
      vacunaciones: 0
    })
    expect(data.userInfo).toEqual({
      nombre: '',
      email: ''
    })
  })

  it('should load user data', () => {
    authService.getUser.mockReturnValue({
      persona: {
        nombre_completo: 'Test User',
        email: 'test@example.com'
      }
    })
    component.methods.cargarDatosUsuario.call(component)
    expect(component.userInfo.nombre).toBe('Test User')
    expect(component.userInfo.email).toBe('test@example.com')
  })

  it('should load statistics successfully', async () => {
    ganadoAPI.getAll.mockResolvedValue({ data: { data: [1, 2, 3] } })
    potreroAPI.getAll.mockResolvedValue({ data: { data: [1, 2] } })
    vacunacionAPI.getAll.mockResolvedValue({ data: { data: [1] } })

    await component.methods.cargarEstadisticas.call(component)
    expect(component.estadisticas.ganado).toBe(3)
    expect(component.estadisticas.potreros).toBe(2)
    expect(component.estadisticas.vacunaciones).toBe(1)
  })

  it('should handle statistics loading error', async () => {
    ganadoAPI.getAll.mockRejectedValue(new Error('API Error'))
    potreroAPI.getAll.mockRejectedValue(new Error('API Error'))
    vacunacionAPI.getAll.mockRejectedValue(new Error('API Error'))

    await component.methods.cargarEstadisticas.call(component)
    expect(component.estadisticas.ganado).toBe(0)
    expect(component.estadisticas.potreros).toBe(0)
    expect(component.estadisticas.vacunaciones).toBe(0)
  })

  it('should handle user data with missing persona', () => {
    authService.getUser.mockReturnValue({})
    component.methods.cargarDatosUsuario.call(component)
    // When persona is missing, nombre_completo is undefined, so nombre stays as ''
    expect(component.userInfo.nombre).toBe('')
    expect(component.userInfo.email).toBe('')
  })

  it('should handle user data with null persona', () => {
    authService.getUser.mockReturnValue({ persona: null })
    component.methods.cargarDatosUsuario.call(component)
    // When persona is null, nombre_completo is undefined, so nombre stays as ''
    expect(component.userInfo.nombre).toBe('')
    expect(component.userInfo.email).toBe('')
  })

  it('should handle user data with missing nombre_completo', () => {
    authService.getUser.mockReturnValue({
      persona: { email: 'test@example.com' }
    })
    component.methods.cargarDatosUsuario.call(component)
    expect(component.userInfo.nombre).toBe('Usuario')
    expect(component.userInfo.email).toBe('test@example.com')
  })

  it('should handle user data with missing email', () => {
    authService.getUser.mockReturnValue({
      persona: { nombre_completo: 'Test User' }
    })
    component.methods.cargarDatosUsuario.call(component)
    expect(component.userInfo.nombre).toBe('Test User')
    expect(component.userInfo.email).toBe('')
  })

  it('should handle statistics with null responses', async () => {
    // When response is null, accessing .data will throw, so it goes to catch
    ganadoAPI.getAll.mockResolvedValue(null)
    potreroAPI.getAll.mockResolvedValue(null)
    vacunacionAPI.getAll.mockResolvedValue(null)

    await component.methods.cargarEstadisticas.call(component)
    // Catch block resets all to 0
    expect(component.estadisticas.ganado).toBe(0)
    expect(component.estadisticas.potreros).toBe(0)
    expect(component.estadisticas.vacunaciones).toBe(0)
  })

  it('should handle statistics with responses without data property', async () => {
    ganadoAPI.getAll.mockResolvedValue({})
    potreroAPI.getAll.mockResolvedValue({})
    vacunacionAPI.getAll.mockResolvedValue({})

    await component.methods.cargarEstadisticas.call(component)
    expect(component.estadisticas.ganado).toBe(0)
    expect(component.estadisticas.potreros).toBe(0)
    expect(component.estadisticas.vacunaciones).toBe(0)
  })

  it('should handle statistics with responses with null data', async () => {
    ganadoAPI.getAll.mockResolvedValue({ data: { data: null } })
    potreroAPI.getAll.mockResolvedValue({ data: { data: null } })
    vacunacionAPI.getAll.mockResolvedValue({ data: { data: null } })

    await component.methods.cargarEstadisticas.call(component)
    expect(component.estadisticas.ganado).toBe(0)
    expect(component.estadisticas.potreros).toBe(0)
    expect(component.estadisticas.vacunaciones).toBe(0)
  })

  it('should handle partial API errors', async () => {
    // When one API fails, the catch block resets all statistics to default
    ganadoAPI.getAll.mockRejectedValue(new Error('Ganado Error'))
    potreroAPI.getAll.mockResolvedValue({ data: { data: [1, 2] } })
    vacunacionAPI.getAll.mockResolvedValue({ data: { data: [1] } })

    await component.methods.cargarEstadisticas.call(component)
    // The catch block resets all to 0 when any error occurs
    expect(component.estadisticas.ganado).toBe(0)
    expect(component.estadisticas.potreros).toBe(0)
    expect(component.estadisticas.vacunaciones).toBe(0)
  })

  describe('mounted hook', () => {
    it('should call cargarDatosUsuario and cargarEstadisticas on mount', async () => {
      const mountedComponent = { ...dashboardContentUsuario }
      mountedComponent.data = mountedComponent.data.bind(mountedComponent)
      mountedComponent.methods = { ...mountedComponent.methods }
      
      // Bind methods to component context
      Object.keys(mountedComponent.methods).forEach(key => {
        mountedComponent.methods[key] = mountedComponent.methods[key].bind(mountedComponent)
      })
      
      // Set up component state
      mountedComponent.estadisticas = mountedComponent.data().estadisticas
      mountedComponent.userInfo = mountedComponent.data().userInfo
      
      // Spy on methods
      const cargarDatosUsuarioSpy = vi.spyOn(mountedComponent.methods, 'cargarDatosUsuario')
      const cargarEstadisticasSpy = vi.spyOn(mountedComponent.methods, 'cargarEstadisticas').mockResolvedValue()

      // Bind mounted to component and add methods to 'this'
      mountedComponent.cargarDatosUsuario = mountedComponent.methods.cargarDatosUsuario
      mountedComponent.cargarEstadisticas = mountedComponent.methods.cargarEstadisticas

      // Simulate mounted hook
      if (mountedComponent.mounted) {
        await mountedComponent.mounted.call(mountedComponent)
      }

      expect(cargarDatosUsuarioSpy).toHaveBeenCalled()
      expect(cargarEstadisticasSpy).toHaveBeenCalled()
    })
  })
})