import { registroVacunacionBase } from './registro-vacunacion-base.js';
import Swal from 'sweetalert2';
import api from '../../services/api.js';

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

const renderTiposVacunaList = (tipos) => {
  if (!tipos || tipos.length === 0) {
    return '<p class="text-muted mb-0">No hay tipos de vacuna registrados.</p>';
  }

  return tipos
    .map(tipo => `
      <div class="d-flex justify-content-between align-items-center border-bottom py-1">
        <span>${tipo.nombre}</span>
        <button type="button" class="btn btn-sm btn-outline-primary btn-editar-tipo-vacuna" data-id="${tipo.id}" data-nombre="${tipo.nombre}">Editar</button>
      </div>
    `)
    .join('');
};

const crearTipoVacunaBackend = async (nombre) => {
  if (!nombre || !nombre.trim()) {
    throw new Error('El nombre del tipo de vacuna no puede estar vacío.');
  }
  const response = await api.post('/vacunaciones/tipos-vacuna', { nombre: nombre.trim() });
  if (response?.data?.status === 'success') {
    return response.data.data;
  }
  throw new Error(response?.data?.message || 'No fue posible crear el tipo de vacuna.');
};

const actualizarTipoVacunaBackend = async (id, nombre) => {
  if (!nombre || !nombre.trim()) {
    throw new Error('El nombre del tipo de vacuna no puede estar vacío.');
  }
  const response = await api.put(`/vacunaciones/tipos-vacuna/${id}`, { nombre: nombre.trim() });
  if (response?.data?.status === 'success') {
    return response.data.data;
  }
  throw new Error(response?.data?.message || 'No fue posible actualizar el tipo de vacuna.');
};

const refreshTiposVacunaList = (component) => {
  const lista = document.getElementById('gestion-tipos-vacuna-list');
  if (lista) {
    lista.innerHTML = renderTiposVacunaList(component.tiposVacuna);
  }
  attachGestionHandlers(component);
};

const attachGestionHandlers = (component) => {
  const botonesEditar = document.querySelectorAll('.btn-editar-tipo-vacuna');
  botonesEditar.forEach(btn => {
    if (btn.dataset.hook === 'true') return;
    btn.dataset.hook = 'true';
    btn.addEventListener('click', async () => {
      const tipoId = Number(btn.dataset.id);
      const nombreActual = btn.dataset.nombre || '';
      const { value } = await Swal.fire({
        title: 'Editar tipo de vacuna',
        input: 'text',
        inputValue: nombreActual,
        showCancelButton: true,
        confirmButtonText: 'Actualizar',
        preConfirm: (valor) => {
          if (!valor || !valor.trim()) {
            Swal.showValidationMessage('El nombre no puede estar vacío.');
            return false;
          }
          return valor.trim();
        }
      });

      if (value && value !== nombreActual) {
        try {
          await actualizarTipoVacunaBackend(tipoId, value);
          await component.obtenerTiposVacuna();
          refreshTiposVacunaList(component);
          Swal.fire('Actualizado', 'El tipo de vacuna fue actualizado correctamente.', 'success');
        } catch (error) {
          Swal.fire('Error', error.message || 'No se pudo actualizar el tipo de vacuna.', 'error');
        }
      }
    });
  });

  const btnAgregar = document.getElementById('gestion-vacuna-agregar');
  if (btnAgregar) {
    btnAgregar.onclick = async () => {
      const input = document.getElementById('gestion-vacuna-nuevo');
      const valor = input?.value;
      if (!valor || !valor.trim()) {
        Swal.fire('Error', 'El nombre del tipo de vacuna es obligatorio.', 'warning');
        return;
      }
      try {
        await crearTipoVacunaBackend(valor);
        await component.obtenerTiposVacuna();
        refreshTiposVacunaList(component);
        if (input) input.value = '';
        Swal.fire('Creado', 'Nuevo tipo de vacuna registrado.', 'success');
      } catch (error) {
        Swal.fire('Error', error.message || 'No se pudo crear el tipo de vacuna.', 'error');
      }
    };
  }
};

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
      id_animal: Number.parseInt(animal, 10),
      id_tipo_vacuna: tipoVacuna ? Number.parseInt(tipoVacuna, 10) : null,
      fecha_aplicacion: fechaAplicacion,
      proxima_dosis: proximaDosis || null,
      responsable: Number.parseInt(responsable, 10),
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
    ...methods,
    async abrirGestionTiposVacuna() {
      await this.obtenerTiposVacuna();
      await Swal.fire({
        title: 'Gestionar tipos de vacuna',
        html: `
          <p class="mb-2">Edita o agrega nuevos tipos de vacuna disponibles para el registro.</p>
          <div id="gestion-tipos-vacuna-list">${renderTiposVacunaList(this.tiposVacuna)}</div>
          <div class="mt-3">
            <label class="form-label fw-semibold mb-1">Agregar nuevo tipo</label>
            <div class="input-group">
              <input id="gestion-vacuna-nuevo" class="form-control form-control-sm" placeholder="Nombre del tipo de vacuna">
              <button type="button" class="btn btn-sm btn-success" id="gestion-vacuna-agregar">Agregar</button>
            </div>
          </div>
        `,
        width: '600px',
        showCancelButton: true,
        confirmButtonText: 'Cerrar',
        didOpen: () => {
          refreshTiposVacunaList(this);
        }
      });
    }
  }
};

