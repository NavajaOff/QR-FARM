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
})