import { vi } from 'vitest'
import registroVacunacionUsuario from './registro-vacunacion-usuario.js'

// Mock de registro-vacunacion-base.js
vi.mock('./registro-vacunacion-base.js', () => ({
  registroVacunacionBase: {
    data() {
      return {
        loading: false,
        message: '',
        messageType: ''
      }
    },
    mounted() {
      // Mock mounted
    },
    methods: {
      cargarDatos: vi.fn(),
      registrarVacunacion: vi.fn(),
      eliminarRegistro: vi.fn()
    }
  }
}))

describe('registro-vacunacion-usuario.js', () => {
  it('should export a Vue component', () => {
    expect(registroVacunacionUsuario).toBeDefined()
    expect(registroVacunacionUsuario.name).toBe('RegistroVacunacionUsuario')
  })

  it('should have registroVacunacionConfig', () => {
    expect(registroVacunacionUsuario.registroVacunacionConfig).toBeDefined()
    expect(registroVacunacionUsuario.registroVacunacionConfig.registroValidacionMsg).toBe('Por favor complete todos los campos requeridos')
    expect(registroVacunacionUsuario.registroVacunacionConfig.eliminarLogPrefix).toBe('Frontend Usuario')
  })

  it('should have methods object', () => {
    expect(registroVacunacionUsuario.methods).toBeDefined()
  })

  it('should be a valid Vue component definition', () => {
    expect(typeof registroVacunacionUsuario).toBe('object')
    expect(registroVacunacionUsuario.name).toBe('RegistroVacunacionUsuario')
  })
})