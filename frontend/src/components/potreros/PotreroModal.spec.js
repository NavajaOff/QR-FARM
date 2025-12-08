import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import PotreroModal from './PotreroModal.vue'

describe('PotreroModal', () => {
  const mockProps = {
    isEditing: false,
    potrero: {},
    tiposPasto: [
      { id: 1, tipo_pasto: 'Alfalfa' },
      { id: 2, nombre: 'Cebada' }
    ],
    estadosPotrero: [
      { id: 1, nombre_estado: 'disponible' },
      { id: 2, nombre_estado: 'ocupado' }
    ],
    personasUsuario: [
      { id: 1, nombre_completo: 'Juan Pérez' },
      { id: 2, nombre_completo: 'María García' }
    ],
    loading: false
  }

  it('should mount correctly', () => {
    const wrapper = mount(PotreroModal, { props: mockProps })
    expect(wrapper.exists()).toBe(true)
  })

  it('should render modal structure', () => {
    const wrapper = mount(PotreroModal, { props: mockProps })
    expect(wrapper.find('.modal').exists()).toBe(true)
    expect(wrapper.find('.modal-dialog').exists()).toBe(true)
    expect(wrapper.find('.modal-content').exists()).toBe(true)
  })

  it('should show "Crear Potrero" title when not editing', () => {
    const wrapper = mount(PotreroModal, { props: { ...mockProps, isEditing: false } })
    expect(wrapper.find('.modal-title').text()).toBe('Crear Potrero')
  })

  it('should show "Editar Potrero" title when editing', () => {
    const wrapper = mount(PotreroModal, { props: { ...mockProps, isEditing: true } })
    expect(wrapper.find('.modal-title').text()).toBe('Editar Potrero')
  })

  it('should emit close event when close button is clicked', async () => {
    const wrapper = mount(PotreroModal, { props: mockProps })
    await wrapper.find('.btn-close').trigger('click')
    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('should render form with required fields', () => {
    const wrapper = mount(PotreroModal, { props: mockProps })
    expect(wrapper.find('#potrero-nombre').exists()).toBe(true)
    expect(wrapper.find('#potrero-nombre').attributes('required')).toBeDefined()
  })

  it('should render estado select only when editing', () => {
    const wrapper = mount(PotreroModal, { props: { ...mockProps, isEditing: true } })
    expect(wrapper.find('#potrero-estado').exists()).toBe(true)

    const wrapperCreate = mount(PotreroModal, { props: { ...mockProps, isEditing: false } })
    expect(wrapperCreate.find('#potrero-estado').exists()).toBe(false)
  })

  it('should render all form fields', () => {
    const wrapper = mount(PotreroModal, { props: { ...mockProps, isEditing: true } })

    // Check all input fields exist
    expect(wrapper.find('#potrero-capacidad').exists()).toBe(true)
    expect(wrapper.find('#potrero-hectareas').exists()).toBe(true)
    expect(wrapper.find('#potrero-tipo-pasto').exists()).toBe(true)
    expect(wrapper.find('#potrero-responsable').exists()).toBe(true)
    expect(wrapper.find('#potrero-fecha-ultimo-uso').exists()).toBe(true)
    expect(wrapper.find('#potrero-proxima-limpieza').exists()).toBe(true)
    expect(wrapper.find('#potrero-area').exists()).toBe(true)
    expect(wrapper.find('#potrero-ultima-limpieza').exists()).toBe(true)
    expect(wrapper.find('#potrero-descripcion').exists()).toBe(true)
  })

  it('should populate tiposPasto select options', () => {
    const wrapper = mount(PotreroModal, { props: mockProps })
    const options = wrapper.find('#potrero-tipo-pasto').findAll('option')
    expect(options.length).toBe(3) // empty option + 2 tipos
    expect(options[1].text()).toBe('Alfalfa')
    expect(options[2].text()).toBe('Cebada')
  })

  it('should populate estadosPotrero select options when editing', () => {
    const wrapper = mount(PotreroModal, { props: { ...mockProps, isEditing: true } })
    const options = wrapper.find('#potrero-estado').findAll('option')
    expect(options.length).toBe(2)
    expect(options[0].text()).toBe('disponible')
    expect(options[1].text()).toBe('ocupado')
  })

  it('should populate personasUsuario select options', () => {
    const wrapper = mount(PotreroModal, { props: mockProps })
    const options = wrapper.find('#potrero-responsable').findAll('option')
    expect(options.length).toBe(3) // empty option + 2 personas
    expect(options[1].text()).toBe('Juan Pérez')
    expect(options[2].text()).toBe('María García')
  })

  it('should bind form data to inputs', async () => {
    const wrapper = mount(PotreroModal, { props: mockProps })

    const nombreInput = wrapper.find('#potrero-nombre')
    await nombreInput.setValue('Test Potrero')
    expect(wrapper.vm.form.nombre).toBe('Test Potrero')

    const capacidadInput = wrapper.find('#potrero-capacidad')
    await capacidadInput.setValue('50')
    expect(wrapper.vm.form.capacidad).toBe(50)

    const hectareasInput = wrapper.find('#potrero-hectareas')
    await hectareasInput.setValue('25.5')
    expect(wrapper.vm.form.hectareas).toBe(25.5)
  })

  it('should bind select values', async () => {
    const wrapper = mount(PotreroModal, { props: mockProps })

    const tipoPastoSelect = wrapper.find('#potrero-tipo-pasto')
    await tipoPastoSelect.setValue(1)
    expect(wrapper.vm.form.id_tipo_pasto).toBe(1)

    const responsableSelect = wrapper.find('#potrero-responsable')
    await responsableSelect.setValue('2')
    expect(wrapper.vm.form.responsable_persona_id).toBe(2)
  })

  it('should bind date inputs', async () => {
    const wrapper = mount(PotreroModal, { props: { ...mockProps, isEditing: true } })

    const fechaUltimoUso = wrapper.find('#potrero-fecha-ultimo-uso')
    await fechaUltimoUso.setValue('2024-01-15')
    expect(wrapper.vm.form.fecha_ultimo_uso).toBe('2024-01-15')

    const proximaLimpieza = wrapper.find('#potrero-proxima-limpieza')
    await proximaLimpieza.setValue('2024-02-01')
    expect(wrapper.vm.form.proxima_limpieza).toBe('2024-02-01')

    const ultimaLimpieza = wrapper.find('#potrero-ultima-limpieza')
    await ultimaLimpieza.setValue('2024-01-01')
    expect(wrapper.vm.form.ultima_limpieza).toBe('2024-01-01')
  })

  it('should bind textarea', async () => {
    const wrapper = mount(PotreroModal, { props: mockProps })

    const descripcionTextarea = wrapper.find('#potrero-descripcion')
    await descripcionTextarea.setValue('Descripción de prueba')
    expect(wrapper.vm.form.descripcion).toBe('Descripción de prueba')
  })

  it('should initialize form with default values', () => {
    const wrapper = mount(PotreroModal, { props: mockProps })

    expect(wrapper.vm.form.nombre).toBe('')
    expect(wrapper.vm.form.id_estado_potrero).toBe(1)
    expect(wrapper.vm.form.capacidad).toBeNull()
    expect(wrapper.vm.form.hectareas).toBeNull()
    expect(wrapper.vm.form.id_tipo_pasto).toBeNull()
    expect(wrapper.vm.form.fecha_ultimo_uso).toBe('')
    expect(wrapper.vm.form.responsable_persona_id).toBeNull()
    expect(wrapper.vm.form.proxima_limpieza).toBe('')
    expect(wrapper.vm.form.area).toBeNull()
    expect(wrapper.vm.form.ultima_limpieza).toBe('')
    expect(wrapper.vm.form.descripcion).toBe('')
  })

  it('should populate form when editing and potrero prop changes', async () => {
    const potreroData = {
      nombre: 'Potrero Editado',
      id_estado_potrero: 2,
      capacidad: 100,
      hectareas: 50.5,
      id_tipo_pasto: 1,
      fecha_ultimo_uso: '2024-01-10',
      responsable_persona_id: 2,
      proxima_limpieza: '2024-02-15',
      area: 50000,
      ultima_limpieza: '2024-01-05',
      descripcion: 'Descripción editada'
    }

    const wrapper = mount(PotreroModal, {
      props: { ...mockProps, isEditing: true, potrero: potreroData }
    })

    await nextTick()

    expect(wrapper.vm.form.nombre).toBe('Potrero Editado')
    expect(wrapper.vm.form.id_estado_potrero).toBe(2)
    expect(wrapper.vm.form.capacidad).toBe(100)
    expect(wrapper.vm.form.hectareas).toBe(50.5)
    expect(wrapper.vm.form.id_tipo_pasto).toBe(1)
    expect(wrapper.vm.form.fecha_ultimo_uso).toBe('2024-01-10')
    expect(wrapper.vm.form.responsable_persona_id).toBe(2)
    expect(wrapper.vm.form.proxima_limpieza).toBe('2024-02-15')
    expect(wrapper.vm.form.area).toBe(50000)
    expect(wrapper.vm.form.ultima_limpieza).toBe('2024-01-05')
    expect(wrapper.vm.form.descripcion).toBe('Descripción editada')
  })

  it('should emit submit event with form data when submitForm is called', async () => {
    const wrapper = mount(PotreroModal, { props: mockProps })

    // Fill form
    wrapper.vm.form.nombre = 'Test Potrero'
    wrapper.vm.form.capacidad = 75
    wrapper.vm.form.descripcion = 'Test description'

    wrapper.vm.submitForm()

    expect(wrapper.emitted('submit')).toBeTruthy()
    expect(wrapper.emitted('submit')[0][0]).toEqual({
      nombre: 'Test Potrero',
      id_estado_potrero: 1,
      capacidad: 75,
      hectareas: null,
      id_tipo_pasto: null,
      fecha_ultimo_uso: '',
      responsable_persona_id: null,
      proxima_limpieza: '',
      area: null,
      ultima_limpieza: '',
      descripcion: 'Test description'
    })
  })

  it('should emit submit event when form is submitted', async () => {
    const wrapper = mount(PotreroModal, { props: mockProps })

    wrapper.vm.form.nombre = 'Test Potrero'
    const form = wrapper.find('form')
    await form.trigger('submit.prevent')

    expect(wrapper.emitted('submit')).toBeTruthy()
  })

  it('should emit submit event when submit button is clicked', async () => {
    const wrapper = mount(PotreroModal, { props: mockProps })

    wrapper.vm.form.nombre = 'Test Potrero'
    const submitButton = wrapper.find('.btn-primary')
    await submitButton.trigger('click')

    expect(wrapper.emitted('submit')).toBeTruthy()
  })

  it('should show loading spinner when loading prop is true', () => {
    const wrapper = mount(PotreroModal, { props: { ...mockProps, loading: true } })

    expect(wrapper.find('.spinner-border').exists()).toBe(true)
    expect(wrapper.find('.btn-primary').attributes('disabled')).toBeDefined()
  })

  it('should not show loading spinner when loading prop is false', () => {
    const wrapper = mount(PotreroModal, { props: { ...mockProps, loading: false } })

    expect(wrapper.find('.spinner-border').exists()).toBe(false)
    expect(wrapper.find('.btn-primary').attributes('disabled')).toBeUndefined()
  })

  it('should show correct button text when creating', () => {
    const wrapper = mount(PotreroModal, { props: { ...mockProps, isEditing: false } })

    expect(wrapper.find('.btn-primary').text().trim()).toBe('Crear')
  })

  it('should show correct button text when editing', () => {
    const wrapper = mount(PotreroModal, { props: { ...mockProps, isEditing: true } })

    expect(wrapper.find('.btn-primary').text().trim()).toBe('Actualizar')
  })

  it('should emit close event when cancel button is clicked', async () => {
    const wrapper = mount(PotreroModal, { props: mockProps })

    const cancelButton = wrapper.find('.btn-secondary')
    await cancelButton.trigger('click')

    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('should reset form to default values', () => {
    const wrapper = mount(PotreroModal, { props: mockProps })

    // Modify form
    wrapper.vm.form.nombre = 'Modified'
    wrapper.vm.form.capacidad = 100
    wrapper.vm.form.descripcion = 'Modified description'

    wrapper.vm.resetForm()

    expect(wrapper.vm.form.nombre).toBe('')
    expect(wrapper.vm.form.id_estado_potrero).toBe(1)
    expect(wrapper.vm.form.capacidad).toBeNull()
    expect(wrapper.vm.form.descripcion).toBe('')
  })

  it('should handle empty tiposPasto array', () => {
    const wrapper = mount(PotreroModal, { props: { ...mockProps, tiposPasto: [] } })

    const options = wrapper.find('#potrero-tipo-pasto').findAll('option')
    expect(options.length).toBe(1) // only empty option
    expect(options[0].text()).toBe('Seleccionar tipo de pasto')
  })

  it('should handle empty estadosPotrero array', () => {
    const wrapper = mount(PotreroModal, { props: { ...mockProps, isEditing: true, estadosPotrero: [] } })

    const options = wrapper.find('#potrero-estado').findAll('option')
    expect(options.length).toBe(0)
  })

  it('should handle empty personasUsuario array', () => {
    const wrapper = mount(PotreroModal, { props: { ...mockProps, personasUsuario: [] } })

    const options = wrapper.find('#potrero-responsable').findAll('option')
    expect(options.length).toBe(1) // only empty option
    expect(options[0].text()).toBe('Seleccionar responsable')
  })

  it('should handle null potrero prop', () => {
    const wrapper = mount(PotreroModal, { props: { ...mockProps, potrero: null } })

    expect(wrapper.vm.form.nombre).toBe('')
  })

  it('should handle undefined potrero prop', () => {
    const wrapper = mount(PotreroModal, { props: { ...mockProps, potrero: undefined } })

    expect(wrapper.vm.form.nombre).toBe('')
  })
})