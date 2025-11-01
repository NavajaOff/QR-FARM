import { ref } from 'vue';
import Swal from 'sweetalert2';

// Variables reactivas
export const currentIndex = ref(0);
export const accordionOpen = ref(true);
export const potreros = ref([]);
export const tiposPasto = ref([]);
export const estadosPotrero = ref([]);
export const personasUsuario = ref([]);
export const loading = ref(true);
export const error = ref(null);

// API configuration
const API_BASE = 'http://localhost:5000/api';

// API calls
export const cargarDatosIniciales = async () => {
  try {
    loading.value = true;
    error.value = null;

    // Cargar personas primero para que estén disponibles al cargar potreros
    await cargarPersonasUsuario();

    await Promise.all([
      cargarTiposPasto(),
      cargarEstadosPotrero()
    ]);

    await cargarPotreros();
  } catch (error) {
    error.value = error.message;
    console.error('Error cargando datos iniciales:', error);
    loading.value = false;
  }
};

export const cargarTiposPasto = async () => {
  try {
    const response = await fetch(`${API_BASE}/potreros/tipos-pasto`);
    if (response.ok) {
      const data = await response.json();
      tiposPasto.value = data.success ? data.data : [];
    } else {
      tiposPasto.value = [];
    }
  } catch (error) {
    console.error('Error cargando tipos de pasto:', error);
    tiposPasto.value = [];
  }
};

export const cargarEstadosPotrero = async () => {
  try {
    const response = await fetch(`${API_BASE}/potreros/estados`);
    if (response.ok) {
      const data = await response.json();
      estadosPotrero.value = data.success ? data.data : [];
    } else {
      estadosPotrero.value = [];
    }
  } catch (error) {
    console.error('Error cargando estados de potrero:', error);
    estadosPotrero.value = [];
  }
};

export const cargarPersonasUsuario = async () => {
  try {
    const response = await fetch(`${API_BASE}/potreros/personas-usuario`);
    if (response.ok) {
      const data = await response.json();
      personasUsuario.value = data.success ? data.data : [];
    } else {
      personasUsuario.value = [];
    }
  } catch (error) {
    console.error('Error cargando personas usuario:', error);
    personasUsuario.value = [];
  }
};

export const cargarPotreros = async () => {
  try {
    console.log('Cargando potreros desde API...');
    const response = await fetch(`${API_BASE}/potreros/`);
    console.log('Respuesta HTTP:', response.status);

    if (!response.ok) {
      throw new Error(`Error HTTP: ${response.status}`);
    }

    const data = await response.json();
    console.log('Respuesta completa del backend:', data);

    // Validar si la respuesta contiene un array dentro de data.data
    if (data.data && Array.isArray(data.data)) {
      console.log('Procesando array de potreros desde data.data');
      potreros.value = data.data.map(potrero => ({
        id: potrero.id,
        nombre: potrero.nombre,
        estado: potrero.estado,
        capacidad: potrero.capacidad,
        ocupacion: potrero.ocupacion,
        hectareas: potrero.hectareas,
        area: potrero.area,
        fechaUso: potrero.fecha_ultimo_uso ? formatDate(potrero.fecha_ultimo_uso) : '',
        ultimaLimpieza: potrero.ultima_limpieza ? formatDate(potrero.ultima_limpieza) : '',
        proximaLimpieza: potrero.proxima_limpieza ? formatDate(potrero.proxima_limpieza) : null,
        responsable: potrero.responsable_persona_id ? (personasUsuario.value.find(p => p.id == potrero.responsable_persona_id) ? `${personasUsuario.value.find(p => p.id == potrero.responsable_persona_id).primer_nombre} ${personasUsuario.value.find(p => p.id == potrero.responsable_persona_id).primer_apellido}` : `Persona ${potrero.responsable_persona_id}`) : 'No asignado',
        descripcion: potrero.descripcion || '',
        pasto: potrero.tipo_pasto_nombre || 'No definido'
      }));
      console.log('Potreros cargados exitosamente:', potreros.value.length, 'potreros');
    } else if (Array.isArray(data)) {
      // Fallback: si la respuesta es directamente un array
      console.log('Procesando array de potreros directamente desde data');
      potreros.value = data.map(potrero => ({
        id: potrero.id,
        nombre: potrero.nombre,
        estado: potrero.estado,
        capacidad: potrero.capacidad,
        ocupacion: potrero.ocupacion,
        hectareas: potrero.hectareas,
        area: potrero.area,
        fechaUso: potrero.fecha_ultimo_uso ? formatDate(potrero.fecha_ultimo_uso) : '',
        ultimaLimpieza: potrero.ultima_limpieza ? formatDate(potrero.ultima_limpieza) : '',
        proximaLimpieza: potrero.proxima_limpieza ? formatDate(potrero.proxima_limpieza) : null,
        responsable: potrero.responsable || 'No asignado',
        descripcion: potrero.descripcion || '',
        pasto: potrero.tipo_pasto || 'No definido'
      }));
      console.log('Potreros cargados exitosamente (fallback):', potreros.value.length, 'potreros');
    } else {
      console.warn('La respuesta no contiene un array válido de potreros');
      potreros.value = [];
    }
  } catch (error) {
    console.error('Error cargando potreros:', error);
    error.value = error.message;
    potreros.value = [];
  } finally {
    loading.value = false;
  }
};

// Utility functions
export const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  // Ajustar por zona horaria de Colombia (UTC-5)
  date.setHours(date.getHours() + 5);
  return date.toLocaleDateString('es-ES', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  });
};

export const estadoClass = (estado) => {
  if (estado === 'Disponible') return 'bg-success';
  if (estado === 'En uso') return 'bg-warning';
  if (estado === 'Mantenimiento') return 'bg-danger';
  return 'bg-secondary';
};

// CRUD operations
export const crearPotrero = () => {
  // Construir opciones de estado
  let estadoOptions = '';
  estadosPotrero.value.forEach(estado => {
    estadoOptions += `<option value="${estado.estado}">${estado.estado}</option>`;
  });

  // Construir opciones de tipo de pasto
  let pastoOptions = '<option value="">Seleccionar tipo de pasto</option>';
  tiposPasto.value.forEach(tipo => {
    pastoOptions += `<option value="${tipo.id}">${tipo.tipo_pasto || 'Sin nombre'}</option>`;
  });

  // Construir opciones de responsable
  let responsableOptions = '<option value="">Seleccionar responsable</option>';
  personasUsuario.value.forEach(persona => {
    const nombreCompleto = `${persona.primer_nombre} ${persona.primer_apellido}`.trim();
    responsableOptions += `<option value="${persona.id}">${nombreCompleto}</option>`;
  });

  Swal.fire({
    title: '<i class="fas fa-plus"></i> Crear Nuevo Potrero',
    html: `
      <form class="text-start">
        <div class="mb-3">
          <label class="form-label">Estado:</label>
          <select id="estado" class="form-control">
            ${estadoOptions}
          </select>
        </div>
        <div class="mb-3"><label class="form-label">Capacidad:</label><input type="number" id="capacidad" class="form-control" placeholder="Ej: 25" min="0"></div>
        <div class="mb-3"><label class="form-label">Hectáreas:</label><input type="number" id="hectareas" class="form-control" placeholder="Ej: 2.5" step="0.01" min="0"></div>
        <div class="mb-3"><label class="form-label">Ocupación:</label><input type="number" id="ocupacion" class="form-control" placeholder="Ej: 0" min="0" value="0"></div>
        <div class="mb-3">
          <label class="form-label">Tipo de pasto:</label>
          <select id="id_tipo_pasto" class="form-control">
            ${pastoOptions}
          </select>
        </div>
        <div class="mb-3">
          <label class="form-label">Responsable:</label>
          <select id="responsable_persona_id" class="form-control">
            ${responsableOptions}
          </select>
        </div>
        <div class="mb-3"><label class="form-label">Próxima limpieza:</label><input type="date" id="proxima_limpieza" class="form-control"></div>
        <div class="mb-3"><label class="form-label">Área (m²):</label><input type="number" id="area" class="form-control" placeholder="Ej: 2500" step="0.01" min="0"></div>
        <div class="mb-3"><label class="form-label">Descripción:</label><textarea id="descripcion" class="form-control" rows="2" placeholder="Descripción opcional del potrero"></textarea></div>
      </form>
    `,
    width: '600px',
    showCancelButton: true,
    confirmButtonText: 'Agregar',
    confirmButtonColor: '#00d563',
    preConfirm: () => {
      const estado = document.getElementById('estado').value;
      const capacidad = document.getElementById('capacidad').value;
      const hectareas = document.getElementById('hectareas').value;
      const ocupacion = document.getElementById('ocupacion').value;
      const id_tipo_pasto = document.getElementById('id_tipo_pasto').value;
      const responsable_persona_id = document.getElementById('responsable_persona_id').value;
      const proxima_limpieza = document.getElementById('proxima_limpieza').value;
      const area = document.getElementById('area').value;
      const descripcion = document.getElementById('descripcion').value;

      return {
        nombre: null, // El backend generará el nombre automáticamente
        estado,
        capacidad: capacidad ? parseInt(capacidad) : null,
        hectareas: hectareas ? parseFloat(hectareas) : null,
        ocupacion: ocupacion ? parseInt(ocupacion) : 0,
        id_tipo_pasto: id_tipo_pasto ? parseInt(id_tipo_pasto) : null,
        responsable_persona_id: responsable_persona_id ? parseInt(responsable_persona_id) : null,
        proxima_limpieza,
        area: area ? parseFloat(area) : null,
        descripcion
      };
    }
  }).then(async (result) => {
    if (result.isConfirmed) {
      try {
        const response = await fetch(`${API_BASE}/potreros/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(result.value)
        });

        if (response.ok) {
          const data = await response.json();
          if (data.success) {
            Swal.fire('¡Éxito!', 'Potrero creado correctamente', 'success');
            await cargarPotreros();
          } else {
            console.log('Respuesta de potreros:', data);
            throw new Error(data.message || 'Error desconocido');
          }
        } else {
          const errorData = await response.json();
          throw new Error(errorData.message || `Error HTTP: ${response.status}`);
        }
      } catch (error) {
        console.error('Error creando potrero:', error);
        Swal.fire('Error', error.message, 'error');
      }
    }
  });
};

export const editarPotrero = (id) => {
  const potrero = potreros.value.find(p => p.id === id);
  if (!potrero) return;

  // Construir opciones de estado con selección
  let estadoOptions = '';
  estadosPotrero.value.forEach(estado => {
    const selected = estado.estado === potrero.estado ? 'selected' : '';
    estadoOptions += `<option value="${estado.estado}" ${selected}>${estado.estado}</option>`;
  });

  // Construir opciones de tipo de pasto con selección
  let pastoOptions = '<option value="">Seleccionar tipo de pasto</option>';
  tiposPasto.value.forEach(tipo => {
    const selected = tipo.tipo_pasto === potrero.pasto ? 'selected' : '';
    pastoOptions += `<option value="${tipo.id}" ${selected}>${tipo.tipo_pasto || 'Sin nombre'}</option>`;
  });

  // Construir opciones de responsable con selección
  let responsableOptions = '<option value="">Seleccionar responsable</option>';
  personasUsuario.value.forEach(persona => {
    const nombreCompleto = `${persona.primer_nombre} ${persona.primer_apellido}`.trim();
    const selected = nombreCompleto === potrero.responsable ? 'selected' : '';
    responsableOptions += `<option value="${persona.id}" ${selected}>${nombreCompleto}</option>`;
  });

  Swal.fire({
    title: `<i class="fas fa-edit"></i> Editar Potrero: ${potrero.nombre}`,
    html: `
      <form class="text-start">
        <div class="mb-3">
          <label class="form-label">Estado:</label>
          <select id="edit_estado" class="form-control">
            ${estadoOptions}
          </select>
        </div>
        <div class="mb-3"><label class="form-label">Capacidad:</label><input type="number" id="edit_capacidad" class="form-control" value="${potrero.capacidad || ''}" min="0"></div>
        <div class="mb-3"><label class="form-label">Hectáreas:</label><input type="number" id="edit_hectareas" class="form-control" value="${potrero.hectareas || ''}" step="0.01" min="0"></div>
        <div class="mb-3"><label class="form-label">Ocupación:</label><input type="number" id="edit_ocupacion" class="form-control" value="${potrero.ocupacion || 0}" min="0"></div>
        <div class="mb-3">
          <label class="form-label">Tipo de pasto:</label>
          <select id="edit_id_tipo_pasto" class="form-control">
            ${pastoOptions}
          </select>
        </div>
        <div class="mb-3"><label class="form-label">Fecha de último uso:</label><input type="date" id="edit_fecha_ultimo_uso" class="form-control" value="${potrero.fechaUso ? potrero.fechaUso.split('/').reverse().join('-') : ''}"></div>
        <div class="mb-3">
          <label class="form-label">Responsable:</label>
          <select id="edit_responsable_persona_id" class="form-control">
            ${responsableOptions}
          </select>
        </div>
        <div class="mb-3"><label class="form-label">Próxima limpieza:</label><input type="date" id="edit_proxima_limpieza" class="form-control" value="${potrero.proximaLimpieza ? potrero.proximaLimpieza.split('/').reverse().join('-') : ''}"></div>
        <div class="mb-3"><label class="form-label">Área (m²):</label><input type="number" id="edit_area" class="form-control" value="${potrero.area || ''}" step="0.01" min="0"></div>
        <div class="mb-3"><label class="form-label">Última limpieza:</label><input type="date" id="edit_ultima_limpieza" class="form-control" value="${potrero.ultimaLimpieza ? potrero.ultimaLimpieza.split('/').reverse().join('-') : ''}"></div>
        <div class="mb-3"><label class="form-label">Descripción:</label><textarea id="edit_descripcion" class="form-control" rows="2">${potrero.descripcion || ''}</textarea></div>
      </form>
    `,
    width: '600px',
    showCancelButton: true,
    confirmButtonText: 'Actualizar',
    confirmButtonColor: '#00d563',
    preConfirm: () => {
      const estado = document.getElementById('edit_estado').value;
      const capacidad = document.getElementById('edit_capacidad').value;
      const hectareas = document.getElementById('edit_hectareas').value;
      const ocupacion = document.getElementById('edit_ocupacion').value;
      const id_tipo_pasto = document.getElementById('edit_id_tipo_pasto').value;
      const responsable_persona_id = document.getElementById('edit_responsable_persona_id').value;
      const proxima_limpieza = document.getElementById('edit_proxima_limpieza').value;
      const ultima_limpieza = document.getElementById('edit_ultima_limpieza').value;
      const area = document.getElementById('edit_area').value;
      const descripcion = document.getElementById('edit_descripcion').value;

      const data = {
        estado,
        capacidad: capacidad ? parseInt(capacidad) : null,
        hectareas: hectareas ? parseFloat(hectareas) : null,
        ocupacion: ocupacion ? parseInt(ocupacion) : 0,
        id_tipo_pasto: id_tipo_pasto ? parseInt(id_tipo_pasto) : null,
        responsable_persona_id: responsable_persona_id ? parseInt(responsable_persona_id) : null,
        area: area ? parseFloat(area) : null,
        descripcion
      };

      // Solo incluir proxima_limpieza si tiene valor
      if (proxima_limpieza) {
        data.proxima_limpieza = proxima_limpieza;
      }

      // Solo incluir ultima_limpieza si tiene valor
      if (ultima_limpieza) {
        data.ultima_limpieza = ultima_limpieza;
      }

      // Solo incluir fecha_ultimo_uso si tiene valor
      const fecha_ultimo_uso = document.getElementById('edit_fecha_ultimo_uso').value;
      if (fecha_ultimo_uso) {
        data.fecha_ultimo_uso = fecha_ultimo_uso;
      }

      return data;
    }
  }).then(async (result) => {
    if (result.isConfirmed) {
      try {
        const response = await fetch(`${API_BASE}/potreros/${id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(result.value)
        });

        if (response.ok) {
          const data = await response.json();
          if (data.success) {
            Swal.fire('¡Éxito!', 'Potrero actualizado correctamente', 'success');
            await cargarPotreros();
          } else {
            throw new Error(data.message || 'Error desconocido');
          }
        } else {
          const errorData = await response.json();
          throw new Error(errorData.message || `Error HTTP: ${response.status}`);
        }
      } catch (error) {
        console.error('Error actualizando potrero:', error);
        Swal.fire('Error', error.message, 'error');
      }
    }
  });
};

// Navigation
export const prevPotrero = () => {
  if (potreros.value.length > 1) {
    currentIndex.value = (currentIndex.value - 1 + potreros.value.length) % potreros.value.length;
    accordionOpen.value = true;
  }
};

export const nextPotrero = () => {
  if (potreros.value.length > 1) {
    currentIndex.value = (currentIndex.value + 1) % potreros.value.length;
    accordionOpen.value = true;
  }
};

export const toggleAccordion = () => {
  accordionOpen.value = !accordionOpen.value;
};