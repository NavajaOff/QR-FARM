import { mount } from '@vue/test-utils'
import RegistroVacunacionUsuario from './RegistroVacunacionUsuario.vue'
import RegistroVacunacionBase from '../../components/RegistroVacunacionBase.vue'

describe('RegistroVacunacionUsuario', () => {
  it('should mount correctly', () => {
    const wrapper = mount(RegistroVacunacionUsuario, {
      global: {
        components: {
          RegistroVacunacionBase
        }
      }
    })
    expect(wrapper.exists()).toBe(true)
  })
})