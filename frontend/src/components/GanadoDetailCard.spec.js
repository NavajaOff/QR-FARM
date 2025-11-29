import { mount } from '@vue/test-utils'
import GanadoDetailCard from './GanadoDetailCard.vue'

describe('GanadoDetailCard', () => {
  it('should mount correctly', () => {
    const mockGanado = {
      nombre: 'Vaca Test',
      estado: 'activo',
      estado_salud: 'bueno',
      fecha_nacimiento: '2020-01-01',
      raza: 'Holstein',
      peso: 500,
      potrero_id: 1
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