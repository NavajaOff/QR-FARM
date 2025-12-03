import { mount } from '@vue/test-utils'
import { vi, beforeEach, describe, it, expect } from 'vitest'
import RegistroVacunacionBase from './RegistroVacunacionBase.vue'
import { vacunacionAPI } from '../services/api.js'

vi.mock('../services/api.js', () => ({
  vacunacionAPI: {
    getAll: vi.fn()
  }
}))

describe('RegistroVacunacionBase', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should mount correctly', () => {
    vacunacionAPI.getAll.mockResolvedValue({ data: { data: [] } })
    const wrapper = mount(RegistroVacunacionBase)
    expect(wrapper.exists()).toBe(true)
  })

  it('should show loading state initially', async () => {
    vacunacionAPI.getAll.mockImplementation(() => new Promise(resolve => setTimeout(() => resolve({ data: { data: [] } }), 100)))
    const wrapper = mount(RegistroVacunacionBase)
    await wrapper.vm.$nextTick()
    
    expect(wrapper.text()).toContain('Cargando')
  })

  it('should show empty state when no vaccinations', async () => {
    vacunacionAPI.getAll.mockResolvedValue({ data: { data: [] } })
    const wrapper = mount(RegistroVacunacionBase)
    
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))
    
    expect(wrapper.text()).toContain('No hay vacunaciones registradas')
    expect(wrapper.text()).toContain('Hasta el momento no se han registrado vacunaciones')
  })

  it('should display vaccinations list when data exists', async () => {
    const mockVacunaciones = [
      {
        id: 1,
        id_animal: 1,
        nombre_animal: 'Vaca 1',
        tipo_vacuna: 'Fiebre Aftosa',
        fecha_aplicacion: '2024-01-15',
        proxima_dosis: '2024-02-15',
        responsable: 'Dr. Juan',
        estado: 'aplicado'
      }
    ]
    
    vacunacionAPI.getAll.mockResolvedValue({ data: { data: mockVacunaciones } })
    const wrapper = mount(RegistroVacunacionBase)
    
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))
    
    expect(wrapper.text()).toContain('Vacunaciones Registradas')
    expect(wrapper.text()).toContain('Vaca 1')
    expect(wrapper.text()).toContain('Fiebre Aftosa')
  })

  it('should handle API error gracefully', async () => {
    vacunacionAPI.getAll.mockRejectedValue(new Error('API Error'))
    const wrapper = mount(RegistroVacunacionBase)
    
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))
    
    // Should show empty state when error occurs
    expect(wrapper.vm.vacunaciones).toEqual([])
    expect(wrapper.vm.loading).toBe(false)
  })

  it('should format dates correctly', () => {
    vacunacionAPI.getAll.mockResolvedValue({ data: { data: [] } })
    const wrapper = mount(RegistroVacunacionBase)
    
    const formatted = wrapper.vm.formatDate('2024-01-15T10:00:00')
    expect(formatted).toMatch(/\d{2}\/\d{2}\/\d{4}/)
  })

  it('should return correct estado class for aplicado', () => {
    vacunacionAPI.getAll.mockResolvedValue({ data: { data: [] } })
    const wrapper = mount(RegistroVacunacionBase)
    
    expect(wrapper.vm.estadoClass('aplicado')).toBe('bg-success')
    expect(wrapper.vm.estadoClass('Aplicado')).toBe('bg-success')
  })

  it('should return correct estado class for pendiente', () => {
    vacunacionAPI.getAll.mockResolvedValue({ data: { data: [] } })
    const wrapper = mount(RegistroVacunacionBase)
    
    expect(wrapper.vm.estadoClass('pendiente')).toBe('bg-warning')
    expect(wrapper.vm.estadoClass('Pendiente')).toBe('bg-warning')
  })

  it('should return correct estado label', () => {
    vacunacionAPI.getAll.mockResolvedValue({ data: { data: [] } })
    const wrapper = mount(RegistroVacunacionBase)
    
    expect(wrapper.vm.estadoLabel('aplicado')).toBe('Aplicado')
    expect(wrapper.vm.estadoLabel('pendiente')).toBe('Pendiente')
    expect(wrapper.vm.estadoLabel(null)).toBe('Sin estado')
  })
})

