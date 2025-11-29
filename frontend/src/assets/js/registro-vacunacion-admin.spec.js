import { beforeEach, vi, describe, it, expect } from 'vitest'
import registroVacunacionAdmin from './registro-vacunacion-admin.js'
import { registroVacunacionBase } from './registro-vacunacion-base.js'

vi.mock('./registro-vacunacion-base.js', () => ({
  registroVacunacionBase: {
    methods: {
      metodoBase: vi.fn()
    },
    data: () => ({ baseData: 'test' }),
    name: 'BaseComponent'
  }
}))

describe('registro-vacunacion-admin.js', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    document.body.innerHTML = ''
  })

  it('should export a component object', () => {
    expect(registroVacunacionAdmin).toBeDefined()
    expect(typeof registroVacunacionAdmin).toBe('object')
  })

  it('should have correct name', () => {
    expect(registroVacunacionAdmin.name).toBe('RegistroVacunacion')
  })

  it('should have registroVacunacionConfig', () => {
    expect(registroVacunacionAdmin.registroVacunacionConfig).toBeDefined()
    expect(registroVacunacionAdmin.registroVacunacionConfig.registroValidacionMsg).toBeDefined()
    expect(registroVacunacionAdmin.registroVacunacionConfig.eliminarLogPrefix).toBeDefined()
    expect(registroVacunacionAdmin.registroVacunacionConfig.editar).toBeDefined()
  })

  it('should have buildForm function in editar config', () => {
    const buildForm = registroVacunacionAdmin.registroVacunacionConfig.editar.buildForm
    expect(typeof buildForm).toBe('function')
  })

  it('should have collectPayload function in editar config', () => {
    const collectPayload = registroVacunacionAdmin.registroVacunacionConfig.editar.collectPayload
    expect(typeof collectPayload).toBe('function')
  })

  describe('buildAdminEditForm', () => {
    it('should build form HTML with animal select', () => {
      const vacunacion = {
        idAnimal: 1,
        idTipoVacuna: 2,
        fechaAplicacion: '2024-01-15T00:00:00',
        proximaDosis: '2024-07-15T00:00:00',
        responsableId: 3,
        estado: 'aplicado'
      }
      const component = {
        animales: [
          { id: 1, nombre: 'Vaca 1' },
          { id: 2, nombre: 'Toro 1' }
        ],
        tiposVacuna: [
          { id: 1, nombre: 'Vacuna A' },
          { id: 2, nombre: 'Vacuna B' }
        ],
        personas: [
          { id: 1, nombre: 'Juan Pérez' },
          { id: 3, nombre: 'María García' }
        ]
      }

      const buildForm = registroVacunacionAdmin.registroVacunacionConfig.editar.buildForm
      const html = buildForm(vacunacion, component)

      expect(html).toContain('Vaca 1')
      expect(html).toContain('selected')
      expect(html).toContain('Vacuna B')
    })

    it('should handle empty arrays', () => {
      const vacunacion = {
        idAnimal: null,
        idTipoVacuna: null,
        fechaAplicacion: null,
        proximaDosis: null,
        responsableId: null,
        estado: 'pendiente'
      }
      const component = {
        animales: [],
        tiposVacuna: [],
        personas: []
      }

      const buildForm = registroVacunacionAdmin.registroVacunacionConfig.editar.buildForm
      const html = buildForm(vacunacion, component)

      expect(html).toBeDefined()
      expect(typeof html).toBe('string')
    })
  })

  describe('collectAdminEditPayload', () => {
    beforeEach(() => {
      document.body.innerHTML = `
        <select id="animal"><option value="1">Animal 1</option></select>
        <select id="tipoVacuna"><option value="2">Vacuna B</option></select>
        <input id="fechaAplicacion" type="date" value="2024-01-15">
        <input id="proximaDosis" type="date" value="2024-07-15">
        <select id="responsable"><option value="3">Responsable 1</option></select>
        <select id="estado"><option value="aplicado">Aplicado</option></select>
      `
    })

    it('should collect valid payload', () => {
      const collectPayload = registroVacunacionAdmin.registroVacunacionConfig.editar.collectPayload
      const result = collectPayload()

      expect(result.valid).toBe(true)
      expect(result.payload.id_animal).toBe(1)
      expect(result.payload.id_tipo_vacuna).toBe(2)
      expect(result.payload.fecha_aplicacion).toBe('2024-01-15')
      expect(result.payload.proxima_dosis).toBe('2024-07-15')
      expect(result.payload.responsable).toBe(3)
      expect(result.payload.estado).toBe('aplicado')
    })

    it('should return invalid when animal is missing', () => {
      document.getElementById('animal').value = ''
      
      const collectPayload = registroVacunacionAdmin.registroVacunacionConfig.editar.collectPayload
      const result = collectPayload()

      expect(result.valid).toBe(false)
      expect(result.message).toContain('Animal')
    })

    it('should return invalid when fechaAplicacion is missing', () => {
      document.getElementById('fechaAplicacion').value = ''
      
      const collectPayload = registroVacunacionAdmin.registroVacunacionConfig.editar.collectPayload
      const result = collectPayload()

      expect(result.valid).toBe(false)
      expect(result.message).toContain('Fecha Aplicación')
    })

    it('should return invalid when responsable is missing', () => {
      document.getElementById('responsable').value = ''
      
      const collectPayload = registroVacunacionAdmin.registroVacunacionConfig.editar.collectPayload
      const result = collectPayload()

      expect(result.valid).toBe(false)
      expect(result.message).toContain('Responsable')
    })

    it('should handle null tipoVacuna', () => {
      document.getElementById('tipoVacuna').value = ''
      
      const collectPayload = registroVacunacionAdmin.registroVacunacionConfig.editar.collectPayload
      const result = collectPayload()

      expect(result.valid).toBe(true)
      expect(result.payload.id_tipo_vacuna).toBeNull()
    })

    it('should handle null proximaDosis', () => {
      document.getElementById('proximaDosis').value = ''
      
      const collectPayload = registroVacunacionAdmin.registroVacunacionConfig.editar.collectPayload
      const result = collectPayload()

      expect(result.valid).toBe(true)
      expect(result.payload.proxima_dosis).toBeNull()
    })
  })

  it('should include base methods', () => {
    expect(registroVacunacionAdmin.methods).toBeDefined()
    expect(typeof registroVacunacionAdmin.methods).toBe('object')
  })
})

