import { mount } from '@vue/test-utils'
import { vi } from 'vitest'
import RegistroVacunacionAdmin from './RegistroVacunacionAdmin.vue'
import TenantSelector from '../../components/TenantSelector.vue'
import authService from '../../services/authService.js'

vi.mock('../../services/authService.js', () => ({
  default: {
    getRole: vi.fn(() => 'admin')
  }
}))

describe('RegistroVacunacionAdmin', () => {
  it('should mount correctly', () => {
    const wrapper = mount(RegistroVacunacionAdmin, {
      global: {
        components: {
          TenantSelector
        }
      }
    })
    expect(wrapper.exists()).toBe(true)
  })
})

vi.mock('../../assets/js/registro-vacunacion-admin.js', async (importOriginal) => {
  const actual = await importOriginal()
  return {
    ...actual,
    computed: {},
    methods: {}
  }
})

describe('RegistroVacunacionAdmin', () => {
  it('should mount correctly', () => {
    authService.getRole.mockReturnValue('admin')
    const wrapper = mount(RegistroVacunacionAdmin, {
      global: {
        components: {
          TenantSelector
        }
      }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('should show TenantSelector for super admin', () => {
    authService.getRole.mockReturnValue('super_admin')
    const wrapper = mount(RegistroVacunacionAdmin, {
      global: {
        components: {
          TenantSelector
        }
      }
    })
    expect(wrapper.vm.isSuperAdmin).toBe(true)
  })

  it('should not show TenantSelector for regular admin', () => {
    authService.getRole.mockReturnValue('admin')
    const wrapper = mount(RegistroVacunacionAdmin, {
      global: {
        components: {
          TenantSelector
        }
      }
    })
    expect(wrapper.vm.isSuperAdmin).toBe(false)
  })
})