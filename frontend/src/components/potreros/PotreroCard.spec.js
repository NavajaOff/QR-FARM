import { mount } from '@vue/test-utils'
import PotreroCard from './PotreroCard.vue'

describe('PotreroCard', () => {
  it('should mount correctly', () => {
    const mockPotrero = {
      id: 1,
      nombre: 'Potrero Test',
      capacidad: 50,
      area: 1000,
      tipo_suelo: 'pasto',
      estado: 'activo'
    }

    const wrapper = mount(PotreroCard, {
      props: {
        potrero: mockPotrero
      }
    })
    expect(wrapper.exists()).toBe(true)
  })
})