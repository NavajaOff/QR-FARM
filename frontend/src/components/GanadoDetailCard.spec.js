import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import GanadoDetailCard from './GanadoDetailCard.vue'

const createMockGanado = (overrides = {}) => ({
  id: '1',
  nombre: 'Vaca Test',
  estado: 'activo',
  estado_salud: 'bueno',
  fecha_nacimiento: '2020-01-01',
  raza: 'Holstein',
  peso: 500,
  sexo: 'hembra',
  edad: 4,
  codigo_qr: 'QR123',
  propietario: {
    nombre: 'Juan Pérez',
    telefono: '3001234567',
    rol: 'Propietario'
  },
  potrero: {
    nombre: 'Potrero Norte',
    tipo_pasto: 'Cebada',
    capacidad: 50,
    ultima_limpieza: '2023-10-01',
    proxima_limpieza: '2023-11-01',
    fecha_ultimo_uso: '2023-10-15',
    estado: 'activo'
  },
  vacunas: [],
  historial: [],
  ...overrides
})

describe('GanadoDetailCard', () => {
  describe('Component mounting', () => {
    it('should mount correctly', () => {
      const mockGanado = createMockGanado()
      const wrapper = mount(GanadoDetailCard, {
        props: {
          ganado: mockGanado,
          role: 'admin'
        }
      })
      expect(wrapper.exists()).toBe(true)
    })

    it('should render with user role', () => {
      const mockGanado = createMockGanado()
      const wrapper = mount(GanadoDetailCard, {
        props: {
          ganado: mockGanado,
          role: 'user'
        }
      })
      expect(wrapper.exists()).toBe(true)
    })
  })

  describe('Display name', () => {
    it('should display ganado nombre', () => {
      const mockGanado = createMockGanado({ nombre: 'Vaca Test' })
      const wrapper = mount(GanadoDetailCard, {
        props: {
          ganado: mockGanado,
          role: 'admin'
        }
      })
      expect(wrapper.text()).toContain('Vaca Test')
    })

    it('should display fallback when nombre is null', () => {
      const mockGanado = createMockGanado({ nombre: null })
      const wrapper = mount(GanadoDetailCard, {
        props: {
          ganado: mockGanado,
          role: 'admin'
        }
      })
      expect(wrapper.text()).toContain('Sin nombre registrado')
    })
  })

  describe('Badges and chips', () => {
    it('should display estado principal badge', () => {
      const mockGanado = createMockGanado({ estado: 'activo' })
      const wrapper = mount(GanadoDetailCard, {
        props: {
          ganado: mockGanado,
          role: 'admin'
        }
      })
      expect(wrapper.text()).toContain('Activo')
    })

    it('should display estado salud badge', () => {
      const mockGanado = createMockGanado({ estado_salud: 'bueno' })
      const wrapper = mount(GanadoDetailCard, {
        props: {
          ganado: mockGanado,
          role: 'admin'
        }
      })
      expect(wrapper.text()).toContain('Bueno')
    })

    it('should not display estado principal when null', () => {
      const mockGanado = createMockGanado({ estado: null })
      const wrapper = mount(GanadoDetailCard, {
        props: {
          ganado: mockGanado,
          role: 'admin'
        }
      })
      const badges = wrapper.findAll('.ganado-chip--primary')
      expect(badges.length).toBe(0)
    })

    it('should display origin chip for embedded', () => {
      const mockGanado = createMockGanado()
      const wrapper = mount(GanadoDetailCard, {
        props: {
          ganado: mockGanado,
          role: 'admin',
          origin: 'embedded'
        }
      })
      expect(wrapper.text()).toContain('Datos sin conexión')
    })

    it('should display origin chip for api', () => {
      const mockGanado = createMockGanado()
      const wrapper = mount(GanadoDetailCard, {
        props: {
          ganado: mockGanado,
          role: 'admin',
          origin: 'api'
        }
      })
      expect(wrapper.text()).toContain('Datos en línea')
    })

    it('should display syncing chip when syncing', () => {
      const mockGanado = createMockGanado()
      const wrapper = mount(GanadoDetailCard, {
        props: {
          ganado: mockGanado,
          role: 'admin',
          origin: 'embedded',
          syncing: true
        }
      })
      expect(wrapper.text()).toContain('actualizando')
    })
  })

  describe('Banner', () => {
    it('should display banner for embedded origin', () => {
      const mockGanado = createMockGanado()
      const wrapper = mount(GanadoDetailCard, {
        props: {
          ganado: mockGanado,
          role: 'admin',
          origin: 'embedded'
        }
      })
      expect(wrapper.find('.ganado-banner').exists()).toBe(true)
      expect(wrapper.text()).toContain('Mostrando datos embebidos del QR.')
    })

    it('should display banner for api origin', () => {
      const mockGanado = createMockGanado()
      const wrapper = mount(GanadoDetailCard, {
        props: {
          ganado: mockGanado,
          role: 'admin',
          origin: 'api'
        }
      })
      expect(wrapper.find('.ganado-banner').exists()).toBe(true)
      expect(wrapper.text()).toContain('Datos actualizados desde el servidor.')
    })

    it('should display refresh button for embedded origin', () => {
      const mockGanado = createMockGanado()
      const wrapper = mount(GanadoDetailCard, {
        props: {
          ganado: mockGanado,
          role: 'admin',
          origin: 'embedded'
        }
      })
      const refreshButton = wrapper.find('button.ganado-action--ghost')
      expect(refreshButton.exists()).toBe(true)
      expect(refreshButton.text()).toContain('Actualizar datos')
    })

    it('should disable refresh button when syncing', () => {
      const mockGanado = createMockGanado()
      const wrapper = mount(GanadoDetailCard, {
        props: {
          ganado: mockGanado,
          role: 'admin',
          origin: 'embedded',
          syncing: true
        }
      })
      const refreshButton = wrapper.find('button.ganado-action--ghost')
      expect(refreshButton.attributes('disabled')).toBeDefined()
      expect(refreshButton.text()).toContain('Sincronizando...')
    })

    it('should emit refrescar when refresh button is clicked', async () => {
      const mockGanado = createMockGanado()
      const wrapper = mount(GanadoDetailCard, {
        props: {
          ganado: mockGanado,
          role: 'admin',
          origin: 'embedded'
        }
      })
      const refreshButton = wrapper.find('button.ganado-action--ghost')
      await refreshButton.trigger('click')
      expect(wrapper.emitted('refrescar')).toBeTruthy()
    })
  })

  describe('Tabs navigation', () => {
    it('should render all tabs', () => {
      const mockGanado = createMockGanado()
      const wrapper = mount(GanadoDetailCard, {
        props: {
          ganado: mockGanado,
          role: 'admin'
        }
      })
      const tabs = wrapper.findAll('.ganado-tab')
      expect(tabs.length).toBe(4)
      expect(wrapper.text()).toContain('Información general')
      expect(wrapper.text()).toContain('Potrero')
      expect(wrapper.text()).toContain('Vacunas')
      expect(wrapper.text()).toContain('Historial')
    })

    it('should switch to potrero tab', async () => {
      const mockGanado = createMockGanado()
      const wrapper = mount(GanadoDetailCard, {
        props: {
          ganado: mockGanado,
          role: 'admin'
        }
      })
      const potreroTab = wrapper.findAll('.ganado-tab')[1]
      await potreroTab.trigger('click')
      await nextTick()
      expect(wrapper.find('#ganado-panel-potrero').exists()).toBe(true)
    })

    it('should switch to vacunas tab', async () => {
      const mockGanado = createMockGanado()
      const wrapper = mount(GanadoDetailCard, {
        props: {
          ganado: mockGanado,
          role: 'admin'
        }
      })
      const vacunasTab = wrapper.findAll('.ganado-tab')[2]
      await vacunasTab.trigger('click')
      await nextTick()
      expect(wrapper.find('#ganado-panel-vacunas').exists()).toBe(true)
    })

    it('should switch to historial tab', async () => {
      const mockGanado = createMockGanado()
      const wrapper = mount(GanadoDetailCard, {
        props: {
          ganado: mockGanado,
          role: 'admin'
        }
      })
      const historialTab = wrapper.findAll('.ganado-tab')[3]
      await historialTab.trigger('click')
      await nextTick()
      expect(wrapper.find('#ganado-panel-historial').exists()).toBe(true)
    })
  })

  describe('General section', () => {
    it('should display all general fields', () => {
      const mockGanado = createMockGanado()
      const wrapper = mount(GanadoDetailCard, {
        props: {
          ganado: mockGanado,
          role: 'admin'
        }
      })
      expect(wrapper.text()).toContain('Vaca Test')
      expect(wrapper.text()).toContain('Holstein')
      expect(wrapper.text()).toContain('Hembra')
      expect(wrapper.text()).toContain('4 años')
      expect(wrapper.text()).toContain('500.0 kg')
    })

    it('should display propietario information', () => {
      const mockGanado = createMockGanado()
      const wrapper = mount(GanadoDetailCard, {
        props: {
          ganado: mockGanado,
          role: 'admin'
        }
      })
      expect(wrapper.text()).toContain('Juan Pérez')
      expect(wrapper.text()).toContain('3001234567')
      expect(wrapper.text()).toContain('Propietario')
    })

    it('should handle null values in general section', () => {
      const mockGanado = createMockGanado({
        raza: null,
        sexo: null,
        edad: null,
        peso: null,
        propietario: {
          nombre: null,
          telefono: null,
          rol: null
        }
      })
      const wrapper = mount(GanadoDetailCard, {
        props: {
          ganado: mockGanado,
          role: 'admin'
        }
      })
      expect(wrapper.text()).toContain('Sin datos')
    })

    it('should format edad as singular', () => {
      const mockGanado = createMockGanado({ edad: 1 })
      const wrapper = mount(GanadoDetailCard, {
        props: {
          ganado: mockGanado,
          role: 'admin'
        }
      })
      expect(wrapper.text()).toContain('1 año')
    })

    it('should format edad as plural', () => {
      const mockGanado = createMockGanado({ edad: 5 })
      const wrapper = mount(GanadoDetailCard, {
        props: {
          ganado: mockGanado,
          role: 'admin'
        }
      })
      expect(wrapper.text()).toContain('5 años')
    })

    it('should display codigo_qr when present', () => {
      const mockGanado = createMockGanado({ codigo_qr: 'QR123' })
      const wrapper = mount(GanadoDetailCard, {
        props: {
          ganado: mockGanado,
          role: 'admin'
        }
      })
      expect(wrapper.text()).toContain('QR123')
    })

    it('should not display codigo_qr when absent', () => {
      const mockGanado = createMockGanado({ codigo_qr: null })
      const wrapper = mount(GanadoDetailCard, {
        props: {
          ganado: mockGanado,
          role: 'admin'
        }
      })
      expect(wrapper.html()).not.toContain('Código QR')
    })
  })

  describe('Potrero section', () => {
    it('should display potrero information', async () => {
      const mockGanado = createMockGanado()
      const wrapper = mount(GanadoDetailCard, {
        props: {
          ganado: mockGanado,
          role: 'admin'
        }
      })
      const potreroTab = wrapper.findAll('.ganado-tab')[1]
      await potreroTab.trigger('click')
      await nextTick()
      expect(wrapper.text()).toContain('Potrero Norte')
      expect(wrapper.text()).toContain('Cebada')
      expect(wrapper.text()).toContain('50 animales')
    })

    it('should display empty message when no potrero', async () => {
      const mockGanado = createMockGanado({
        potrero: {
          nombre: null,
          tipo_pasto: null,
          capacidad: null
        }
      })
      const wrapper = mount(GanadoDetailCard, {
        props: {
          ganado: mockGanado,
          role: 'admin'
        }
      })
      const potreroTab = wrapper.findAll('.ganado-tab')[1]
      await potreroTab.trigger('click')
      await nextTick()
      expect(wrapper.text()).toContain('No hay información del potrero')
    })
  })

  describe('Vacunas section', () => {
    it('should display empty message when no vacunas', async () => {
      const mockGanado = createMockGanado({ vacunas: [] })
      const wrapper = mount(GanadoDetailCard, {
        props: {
          ganado: mockGanado,
          role: 'admin'
        }
      })
      const vacunasTab = wrapper.findAll('.ganado-tab')[2]
      await vacunasTab.trigger('click')
      await nextTick()
      expect(wrapper.text()).toContain('No hay vacunas registradas aún.')
    })

    it('should display vacunas list', async () => {
      const mockGanado = createMockGanado({
        vacunas: [
          {
            id: '1',
            nombre: 'Vacuna A',
            fecha_aplicacion: '2023-01-01',
            proxima_dosis: '2023-07-01',
            responsable: 'Dr. Juan',
            estado: 'aplicada'
          }
        ]
      })
      const wrapper = mount(GanadoDetailCard, {
        props: {
          ganado: mockGanado,
          role: 'admin'
        }
      })
      const vacunasTab = wrapper.findAll('.ganado-tab')[2]
      await vacunasTab.trigger('click')
      await nextTick()
      expect(wrapper.text()).toContain('Vacuna A')
      expect(wrapper.text()).toContain('Dr. Juan')
    })

    it('should display overdue dose badge', async () => {
      const pastDate = new Date()
      pastDate.setDate(pastDate.getDate() - 5)
      const mockGanado = createMockGanado({
        vacunas: [
          {
            id: '1',
            nombre: 'Vacuna A',
            fecha_aplicacion: '2023-01-01',
            proxima_dosis: pastDate.toISOString(),
            responsable: 'Dr. Juan',
            estado: 'aplicada'
          }
        ]
      })
      const wrapper = mount(GanadoDetailCard, {
        props: {
          ganado: mockGanado,
          role: 'admin'
        }
      })
      const vacunasTab = wrapper.findAll('.ganado-tab')[2]
      await vacunasTab.trigger('click')
      await nextTick()
      expect(wrapper.text()).toContain('Dosis vencida')
    })

    it('should display close dose badge', async () => {
      const futureDate = new Date()
      futureDate.setDate(futureDate.getDate() + 5)
      const mockGanado = createMockGanado({
        vacunas: [
          {
            id: '1',
            nombre: 'Vacuna A',
            fecha_aplicacion: '2023-01-01',
            proxima_dosis: futureDate.toISOString(),
            responsable: 'Dr. Juan',
            estado: 'aplicada'
          }
        ]
      })
      const wrapper = mount(GanadoDetailCard, {
        props: {
          ganado: mockGanado,
          role: 'admin'
        }
      })
      const vacunasTab = wrapper.findAll('.ganado-tab')[2]
      await vacunasTab.trigger('click')
      await nextTick()
      expect(wrapper.text()).toContain('Dosis próxima')
    })
  })

  describe('Historial section', () => {
    it('should display empty message when no historial', async () => {
      const mockGanado = createMockGanado({ historial: [] })
      const wrapper = mount(GanadoDetailCard, {
        props: {
          ganado: mockGanado,
          role: 'admin'
        }
      })
      const historialTab = wrapper.findAll('.ganado-tab')[3]
      await historialTab.trigger('click')
      await nextTick()
      expect(wrapper.text()).toContain('No hay revisiones registradas')
    })

    it('should display historial list', async () => {
      const mockGanado = createMockGanado({
        historial: [
          {
            id: '1',
            fecha: '2023-10-15',
            observaciones: 'Revisión general',
            resultado: 'Saludable',
            veterinario: 'Dr. Juan'
          }
        ]
      })
      const wrapper = mount(GanadoDetailCard, {
        props: {
          ganado: mockGanado,
          role: 'admin'
        }
      })
      const historialTab = wrapper.findAll('.ganado-tab')[3]
      await historialTab.trigger('click')
      await nextTick()
      expect(wrapper.text()).toContain('Revisión general')
      expect(wrapper.text()).toContain('Saludable')
      expect(wrapper.text()).toContain('Dr. Juan')
    })
  })

  describe('Footer actions', () => {
    it('should emit reanudar when button is clicked', async () => {
      const mockGanado = createMockGanado()
      const wrapper = mount(GanadoDetailCard, {
        props: {
          ganado: mockGanado,
          role: 'admin'
        }
      })
      const reanudarButton = wrapper.find('button.ganado-action--primary')
      await reanudarButton.trigger('click')
      expect(wrapper.emitted('reanudar')).toBeTruthy()
    })

    it('should display admin actions for admin role', () => {
      const mockGanado = createMockGanado()
      const wrapper = mount(GanadoDetailCard, {
        props: {
          ganado: mockGanado,
          role: 'admin'
        }
      })
      expect(wrapper.text()).toContain('Ver historial completo')
      expect(wrapper.text()).toContain('Descargar ficha')
    })

    it('should not display admin actions for user role', () => {
      const mockGanado = createMockGanado()
      const wrapper = mount(GanadoDetailCard, {
        props: {
          ganado: mockGanado,
          role: 'user'
        }
      })
      expect(wrapper.text()).not.toContain('Ver historial completo')
      expect(wrapper.text()).not.toContain('Descargar ficha')
    })

    it('should emit accion when admin action is clicked', async () => {
      const mockGanado = createMockGanado()
      const wrapper = mount(GanadoDetailCard, {
        props: {
          ganado: mockGanado,
          role: 'admin'
        }
      })
      const historialButton = wrapper.findAll('button.ganado-action').find(
        btn => btn.text().includes('Ver historial completo')
      )
      if (historialButton) {
        await historialButton.trigger('click')
        expect(wrapper.emitted('accion')).toBeTruthy()
        expect(wrapper.emitted('accion')[0]).toEqual(['ver-historial'])
      }
    })

    it('should emit accion for descargar-ficha', async () => {
      const mockGanado = createMockGanado()
      const wrapper = mount(GanadoDetailCard, {
        props: {
          ganado: mockGanado,
          role: 'admin'
        }
      })
      const descargarButton = wrapper.findAll('button.ganado-action').find(
        btn => btn.text().includes('Descargar ficha')
      )
      if (descargarButton) {
        await descargarButton.trigger('click')
        expect(wrapper.emitted('accion')).toBeTruthy()
        expect(wrapper.emitted('accion')[0]).toEqual(['descargar-ficha'])
      }
    })
  })

  describe('Format functions', () => {
    it('should format date correctly', () => {
      const mockGanado = createMockGanado({ fecha_nacimiento: '2020-01-15' })
      const wrapper = mount(GanadoDetailCard, {
        props: {
          ganado: mockGanado,
          role: 'admin'
        }
      })
      // The date should be formatted in Spanish locale
      expect(wrapper.text()).toMatch(/\d{1,2} de \w+ de \d{4}/)
    })

    it('should handle invalid date', () => {
      const mockGanado = createMockGanado({ fecha_nacimiento: 'invalid-date' })
      const wrapper = mount(GanadoDetailCard, {
        props: {
          ganado: mockGanado,
          role: 'admin'
        }
      })
      // Should display the invalid date as-is or "Sin datos"
      expect(wrapper.text()).toMatch(/invalid-date|Sin datos/)
    })

    it('should format peso with one decimal', () => {
      const mockGanado = createMockGanado({ peso: 500.5 })
      const wrapper = mount(GanadoDetailCard, {
        props: {
          ganado: mockGanado,
          role: 'admin'
        }
      })
      expect(wrapper.text()).toContain('500.5 kg')
    })

    it('should format capacidad correctly', async () => {
      const mockGanado = createMockGanado({
        potrero: {
          ...createMockGanado().potrero,
          capacidad: 25
        }
      })
      const wrapper = mount(GanadoDetailCard, {
        props: {
          ganado: mockGanado,
          role: 'admin'
        }
      })
      const potreroTab = wrapper.findAll('.ganado-tab')[1]
      await potreroTab.trigger('click')
      await nextTick()
      expect(wrapper.text()).toContain('25 animales')
    })

    it('should format estado with capitalization', () => {
      const mockGanado = createMockGanado({ estado: 'activo' })
      const wrapper = mount(GanadoDetailCard, {
        props: {
          ganado: mockGanado,
          role: 'admin'
        }
      })
      expect(wrapper.text()).toContain('Activo')
    })

    it('should handle empty string values', () => {
      const mockGanado = createMockGanado({
        raza: '',
        sexo: ' ',
        propietario: {
          nombre: '',
          telefono: ' ',
          rol: null
        }
      })
      const wrapper = mount(GanadoDetailCard, {
        props: {
          ganado: mockGanado,
          role: 'admin'
        }
      })
      expect(wrapper.text()).toContain('Sin datos')
    })
  })

  describe('Edge cases', () => {
    it('should handle ganado with minimal data', () => {
      const minimalGanado = {
        id: '1',
        nombre: null,
        estado: null,
        estado_salud: null,
        fecha_nacimiento: null,
        raza: null,
        peso: null,
        sexo: null,
        edad: null,
        codigo_qr: null,
        propietario: {
          nombre: null,
          telefono: null,
          rol: null
        },
        potrero: {
          nombre: null,
          tipo_pasto: null,
          capacidad: null,
          ultima_limpieza: null,
          proxima_limpieza: null,
          fecha_ultimo_uso: null,
          estado: null
        },
        vacunas: [],
        historial: []
      }
      const wrapper = mount(GanadoDetailCard, {
        props: {
          ganado: minimalGanado,
          role: 'admin'
        }
      })
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.text()).toContain('Sin nombre registrado')
    })

    it('should handle vacunas without id', async () => {
      const mockGanado = createMockGanado({
        vacunas: [
          {
            nombre: 'Vacuna sin ID',
            fecha_aplicacion: '2023-01-01',
            proxima_dosis: '2023-07-01',
            responsable: 'Dr. Juan'
          }
        ]
      })
      const wrapper = mount(GanadoDetailCard, {
        props: {
          ganado: mockGanado,
          role: 'admin'
        }
      })
      const vacunasTab = wrapper.findAll('.ganado-tab')[2]
      await vacunasTab.trigger('click')
      await nextTick()
      expect(wrapper.text()).toContain('Vacuna sin ID')
    })

    it('should handle historial without id', async () => {
      const mockGanado = createMockGanado({
        historial: [
          {
            fecha: '2023-10-15',
            observaciones: 'Revisión',
            resultado: 'OK'
          }
        ]
      })
      const wrapper = mount(GanadoDetailCard, {
        props: {
          ganado: mockGanado,
          role: 'admin'
        }
      })
      const historialTab = wrapper.findAll('.ganado-tab')[3]
      await historialTab.trigger('click')
      await nextTick()
      expect(wrapper.text()).toContain('Revisión')
    })
  })
})
