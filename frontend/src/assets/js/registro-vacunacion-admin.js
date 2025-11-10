import { registroVacunacionBase } from './registro-vacunacion-base.js';

const { methods, ...baseOptions } = registroVacunacionBase;

const buildAdminEditForm = (vacunacion, component) => `
  <div class="row g-3">
    <div class="col-12">
      <label class="form-label">Animal</label>
      <select id="animal" class="form-select">
        ${component.animales.map(a => `<option value="${a.id}" ${vacunacion.idAnimal == a.id ? 'selected' : ''}>${a.nombre} (ID: ${a.id})</option>`).join('')}
      </select>
    </div>
    <div class="col-12">
      <label class="form-label">Tipo de Vacuna</label>
      <select id="tipoVacuna" class="form-select">
        <option value="">Sin especificar</option>
        ${component.tiposVacuna.map(t => `<option value="${t.id}" ${vacunacion.idTipoVacuna == t.id ? 'selected' : ''}>${t.nombre}</option>`).join('')}
      </select>
    </div>
    <div class="col-6">
      <label class="form-label">Fecha Aplicación</label>
      <input id="fechaAplicacion" type="date" class="form-control" value="${vacunacion.fechaAplicacion ? vacunacion.fechaAplicacion.split('T')[0] : ''}">
    </div>
    <div class="col-6">
      <label class="form-label">Próxima Dosis</label>
      <input id="proximaDosis" type="date" class="form-control" value="${vacunacion.proximaDosis ? vacunacion.proximaDosis.split('T')[0] : ''}">
    </div>
    <div class="col-12">
      <label class="form-label">Responsable</label>
      <select id="responsable" class="form-select">
        ${component.personas.map(p => `<option value="${p.id}" ${vacunacion.responsableId == p.id ? 'selected' : ''}>${p.nombre}</option>`).join('')}
      </select>
    </div>
    <div class="col-12">
      <label class="form-label">Estado</label>
      <select id="estado" class="form-select">
        <option value="pendiente" ${vacunacion.estado === 'pendiente' ? 'selected' : ''}>Pendiente</option>
        <option value="aplicado" ${vacunacion.estado === 'aplicado' ? 'selected' : ''}>Aplicado</option>
      </select>
    </div>
  </div>
`;

function collectAdminEditPayload() {
  const animal = document.getElementById('animal').value;
  const tipoVacuna = document.getElementById('tipoVacuna').value;
  const fechaAplicacion = document.getElementById('fechaAplicacion').value;
  const proximaDosis = document.getElementById('proximaDosis').value;
  const responsable = document.getElementById('responsable').value;
  const estado = document.getElementById('estado').value;

  const result = {
    valid: true,
    payload: {
      id_animal: parseInt(animal, 10),
      id_tipo_vacuna: tipoVacuna ? parseInt(tipoVacuna, 10) : null,
      fecha_aplicacion: fechaAplicacion,
      proxima_dosis: proximaDosis || null,
      responsable: parseInt(responsable, 10),
      estado
    },
    message: ''
  };

  if (!animal || !fechaAplicacion || !responsable) {
    result.valid = false;
    result.message = 'Por favor complete los campos requeridos: Animal, Fecha Aplicación y Responsable';
  }

  return result;
}

export default {
  ...baseOptions,
  name: 'RegistroVacunacion',
  registroVacunacionConfig: {
    registroValidacionMsg: 'Por favor complete los campos Animal, Tipo de Vacuna, Fecha y Responsable',
    eliminarLogPrefix: 'Frontend Admin',
    editar: {
      buildForm: (vacunacion, component) => buildAdminEditForm(vacunacion, component),
      collectPayload: collectAdminEditPayload
    }
  },
  methods: {
    ...methods
  }
};

