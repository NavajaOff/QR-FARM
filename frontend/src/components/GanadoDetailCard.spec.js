import { mount } from '@vue/test-utils'
import GanadoDetailCard from './GanadoDetailCard.vue'

describe('GanadoDetailCard', () => {
  it('should mount correctly', () => {
    const mockGanado = {
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
      historial: []
    }

    const wrapper = mount(GanadoDetailCard, {
      props: {
        ganado: mockGanado,
        role: 'admin'
      }
    })
    expect(wrapper.exists()).toBe(true)
  })
})