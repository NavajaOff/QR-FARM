import { mount } from '@vue/test-utils'
import { vi } from 'vitest'
import RegistroVacunacionUsuario from './RegistroVacunacionUsuario.vue'
import RegistroVacunacionBase from '../../components/RegistroVacunacionBase.vue'
import { vacunacionAPI } from '../../services/api.js'

vi.mock('../../services/api.js', () => ({
  vacunacionAPI: {
    getAll: vi.fn()
  }
}))

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

  it('should render RegistroVacunacionBase component', () => {
    const wrapper = mount(RegistroVacunacionUsuario, {
      global: {
        components: {
          RegistroVacunacionBase
        }
      }
    })
    const baseComponent = wrapper.findComponent(RegistroVacunacionBase)
    expect(baseComponent.exists()).toBe(true)
  })
})