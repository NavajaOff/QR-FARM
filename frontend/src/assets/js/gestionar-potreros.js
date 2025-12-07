import { ref } from 'vue';
import Swal from 'sweetalert2';
import io from 'socket.io-client';

// Variables reactivas
export const currentIndex = ref(0);
export const accordionOpen = ref(true);
export const potreros = ref([]);
export const tiposPasto = ref([]);
export const estadosPotrero = ref([]);
export const personasUsuario = ref([]);
export const loading = ref(true);
export const error = ref(null);

const buildPersonaNombre = (persona) => {
  if (!persona) return '';
  if (persona.nombre_completo) return persona.nombre_completo;
  const partes = [
    persona.primer_nombre,
    persona.segundo_nombre,
    persona.primer_apellido,
    persona.segundo_apellido
  ].filter(Boolean);
  return partes.join(' ').trim();
};

const obtenerResponsableNombre = (personaId) => {
  if (!personaId) return 'No asignado';
  const persona = personasUsuario.value.find(p => p.id == personaId);
  const etiqueta = buildPersonaNombre(persona);
  if (etiqueta) return etiqueta;
  return `Persona ${personaId}`;
};

const mapPotreroFromApi = (potrero) => {
  const mapped = {
    id: potrero.id,
    nombre: potrero.nombre,
    estado: potrero.estado || potrero.estado_nombre, // Usar estado o estado_nombre
    capacidad: potrero.capacidad,
    ocupacion: potrero.ocupacion,
    hectareas: potrero.hectareas,
    area: potrero.area,
    fechaUso: '',
    ultimaLimpieza: '',
    proximaLimpieza: null,
    responsable: obtenerResponsableNombre(potrero.responsable_persona_id),
    descripcion: potrero.descripcion || '',
    pasto: 'No definido',
    id_tipo_pasto: potrero.id_tipo_pasto,
    responsable_persona_id: potrero.responsable_persona_id,
    id_estado_potrero: potrero.id_estado_potrero
  };

  if (potrero.fecha_ultimo_uso) {
    mapped.fechaUso = formatDate(potrero.fecha_ultimo_uso);
  }

  if (potrero.ultima_limpieza) {
    mapped.ultimaLimpieza = formatDate(potrero.ultima_limpieza);
  }

  if (potrero.proxima_limpieza) {
    mapped.proximaLimpieza = formatDate(potrero.proxima_limpieza);
  }

  if (potrero.tipo_pasto_nombre) {
    mapped.pasto = potrero.tipo_pasto_nombre;
  }

  return mapped;
};

import { getApiBaseUrl, getBackendUrl } from '../../utils/config.js';
import api from '../../services/api.js';

// API configuration
const API_BASE = getApiBaseUrl();

// WebSocket configuration
const socket = io(getBackendUrl());

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
    const response = await api.get('/potreros/tipos-pasto');
    const data = response.data;
    if (data.success) {
      tiposPasto.value = data.data;
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
    const response = await api.get('/potreros/estados');
    const data = response.data;
    if (data.success) {
      estadosPotrero.value = data.data;
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
    const response = await api.get('/potreros/personas-usuario');
    const data = response.data;
    if (data.success) {
      personasUsuario.value = data.data;
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
    const response = await api.get('/potreros/');
    console.log('Respuesta HTTP:', response.status);

    const data = response.data;
    console.log('Respuesta completa del backend:', data);

    // Validar si la respuesta contiene un array dentro de data.data
    if (data.success && data.data && Array.isArray(data.data)) {
      console.log('Procesando array de potreros desde data.data');
      potreros.value = data.data.map(mapPotreroFromApi);
      console.log('Potreros cargados exitosamente:', potreros.value.length, 'potreros');
    } else {
      // Si no hay datos, mostrar lista vacía (modo sin BD)
      potreros.value = [];
      console.log('No hay potreros en la base de datos (modo sin BD)');
    }
  } catch (error) {
    console.error('Error cargando potreros:', error);
    error.value = error.response?.data?.message || error.message || 'Error desconocido';
    potreros.value = [];
  } finally {
    loading.value = false;
  }
};

// Utility functions
export const formatDate = (dateString) => {
  if (!dateString) return '';
  try {
    const date = new Date(dateString);
    // Ajustar por zona horaria de Colombia (UTC-5)
    date.setHours(date.getHours() + 5);
    return date.toLocaleDateString('es-ES', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  } catch (error) {
    console.error('Error formateando fecha:', error);
    return '';
  }
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
  for (const estado of estadosPotrero.value) {
    estadoOptions += `<option value="${estado.estado}">${estado.estado}</option>`;
  }

  // Construir opciones de tipo de pasto
  let pastoOptions = '<option value="">Seleccionar tipo de pasto</option>';
  for (const tipo of tiposPasto.value) {
    pastoOptions += `<option value="${tipo.id}">${tipo.tipo_pasto || 'Sin nombre'}</option>`;
  }

  // Construir opciones de responsable
  let responsableOptions = '<option value="">Seleccionar responsable</option>';
  for (const persona of personasUsuario.value) {
    const nombreCompleto = `${persona.primer_nombre} ${persona.primer_apellido}`.trim();
    responsableOptions += `<option value="${persona.id}">${nombreCompleto}</option>`;
  }

  Swal.fire({
    title: '<i class="fas fa-plus"></i> Crear Nuevo Potrero',
    html: `
      <form class="text-start">
        <div class="mb-3"><label class="form-label">Capacidad:</label><input type="number" id="capacidad" class="form-control" placeholder="Ej: 25" min="0"></div>
        <div class="mb-3"><label class="form-label">Hectáreas:</label><input type="number" id="hectareas" class="form-control" placeholder="Ej: 2.5" step="0.01" min="0"></div>
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
        <div class="mb-3"><label class="form-label">Última limpieza:</label><input type="date" id="ultima_limpieza" class="form-control"></div>
        <div class="mb-3"><label class="form-label">Área (m²):</label><input type="number" id="area" class="form-control" placeholder="Ej: 2500" step="0.01" min="0"></div>
        <div class="mb-3"><label class="form-label">Descripción:</label><textarea id="descripcion" class="form-control" rows="2" placeholder="Descripción opcional del potrero"></textarea></div>
      </form>
    `,
    width: '600px',
    showCancelButton: true,
    confirmButtonText: 'Agregar',
    confirmButtonColor: '#00d563',
    preConfirm: () => {
      const capacidad = document.getElementById('capacidad').value;
      const hectareas = document.getElementById('hectareas').value;
      const id_tipo_pasto = document.getElementById('id_tipo_pasto').value;
      const responsable_persona_id = document.getElementById('responsable_persona_id').value;
      const ultima_limpieza = document.getElementById('ultima_limpieza').value;
      const area = document.getElementById('area').value;
      const descripcion = document.getElementById('descripcion').value;

      // Obtener tenant_id seleccionado para super_admin
      const selectedTenantId = localStorage.getItem('qr_farm_selected_tenant_id');
      const tenant_id = selectedTenantId ? Number.parseInt(selectedTenantId, 10) : null;

      return {
        nombre: null, // El backend generará el nombre automáticamente
        tenant_id: tenant_id, // Incluir tenant_id para super_admin
        id_estado_potrero: 1, // Estado por defecto al crear (disponible = 1)
        capacidad: capacidad ? Number.parseInt(capacidad, 10) : null,
        hectareas: hectareas ? Number.parseFloat(hectareas) : null,
        id_tipo_pasto: id_tipo_pasto ? Number.parseInt(id_tipo_pasto, 10) : null,
        responsable_persona_id: responsable_persona_id ? Number.parseInt(responsable_persona_id, 10) : null,
        ultima_limpieza,
        area: area ? Number.parseFloat(area) : null,
        descripcion
      };
    }
  }).then(async (result) => {
    if (result.isConfirmed) {
      try {
        const response = await api.post('/potreros/', result.value);
        const data = response.data;
        if (data.success) {
          Swal.fire('¡Éxito!', 'Potrero creado correctamente', 'success');
          await cargarPotreros();
        } else {
          console.log('Respuesta de potreros:', data);
          throw new Error(data.message || 'Error desconocido');
        }
      } catch (error) {
        console.error('Error creando potrero:', error);
        const errorMessage = error.response?.data?.message || error.message || 'Error desconocido';
        Swal.fire('Error', errorMessage, 'error');
      }
    }
  });
};

// Funciones auxiliares para construir opciones
const construirOpcionesEstado = (potrero) => {
  let estadoOptions = '';
  for (const estado of estadosPotrero.value) {
    const estadoValue = estado.estado || estado.nombre_estado || estado.nombre || '';
    const selected = estadoValue === potrero.estado ? 'selected' : '';
    estadoOptions += `<option value="${estadoValue}" ${selected}>${estadoValue}</option>`;
  }
  return estadoOptions;
};

const construirOpcionesTipoPasto = (potrero) => {
  let pastoOptions = '<option value="">Seleccionar tipo de pasto</option>';
  for (const tipo of tiposPasto.value) {
    const tipoNombre = tipo.tipo_pasto || tipo.nombre || 'Sin nombre';
    const selected = tipo.id === potrero.id_tipo_pasto || tipoNombre === potrero.pasto ? 'selected' : '';
    pastoOptions += `<option value="${tipo.id}" ${selected}>${tipoNombre}</option>`;
  }
  return pastoOptions;
};

const construirOpcionesResponsable = (potrero) => {
  let responsableOptions = '<option value="">Seleccionar responsable</option>';
  for (const persona of personasUsuario.value) {
    const nombreCompleto = persona.nombre_completo || `${persona.primer_nombre} ${persona.primer_apellido}`.trim();
    const selected = persona.id === potrero.responsable_persona_id || nombreCompleto === potrero.responsable ? 'selected' : '';
    responsableOptions += `<option value="${persona.id}" ${selected}>${nombreCompleto}</option>`;
  }
  return responsableOptions;
};

const getEstadoIdFromNombre = (estadoNombre) => {
  if (!estadoNombre) return 1; // Default a Disponible si no hay estado
  const estadoMap = {
    'Disponible': 1,
    'Ocupado': 2,
    'En limpieza': 3
  };
  return estadoMap[estadoNombre] || 1; // Default a Disponible
};

const obtenerDatosFormularioEdicion = () => {
  const estado = document.getElementById('edit_estado').value;
  const capacidad = document.getElementById('edit_capacidad').value;
  const hectareas = document.getElementById('edit_hectareas').value;
  const id_tipo_pasto = document.getElementById('edit_id_tipo_pasto').value;
  const responsable_persona_id = document.getElementById('edit_responsable_persona_id').value;
  const proxima_limpieza = document.getElementById('edit_proxima_limpieza').value;
  const ultima_limpieza = document.getElementById('edit_ultima_limpieza').value;
  const area = document.getElementById('edit_area').value;
  const descripcion = document.getElementById('edit_descripcion').value;

  const data = {
    id_estado_potrero: estado ? getEstadoIdFromNombre(estado) : null,
    capacidad: capacidad ? Number.parseInt(capacidad, 10) : null,
    hectareas: hectareas ? Number.parseFloat(hectareas) : null,
    id_tipo_pasto: id_tipo_pasto ? Number.parseInt(id_tipo_pasto, 10) : null,
    responsable_persona_id: responsable_persona_id ? Number.parseInt(responsable_persona_id, 10) : null,
    area: area ? Number.parseFloat(area) : null,
    descripcion
  };

  // Solo incluir campos opcionales si tienen valor
  if (proxima_limpieza) {
    data.proxima_limpieza = proxima_limpieza;
  }
  if (ultima_limpieza) {
    data.ultima_limpieza = ultima_limpieza;
  }
  const fecha_ultimo_uso = document.getElementById('edit_fecha_ultimo_uso').value;
  if (fecha_ultimo_uso) {
    data.fecha_ultimo_uso = fecha_ultimo_uso;
  }

  return data;
};

const asegurarDatosCargados = async () => {
  if (estadosPotrero.value.length === 0) {
    await cargarEstadosPotrero();
  }
  if (tiposPasto.value.length === 0) {
    await cargarTiposPasto();
  }
  if (personasUsuario.value.length === 0) {
    await cargarPersonasUsuario();
  }
};

export const editarPotrero = async (id) => {
  const potrero = potreros.value.find(p => p.id === id);
  if (!potrero) return;

  await asegurarDatosCargados();

  const estadoOptions = construirOpcionesEstado(potrero);
  const pastoOptions = construirOpcionesTipoPasto(potrero);
  const responsableOptions = construirOpcionesResponsable(potrero);

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
      return obtenerDatosFormularioEdicion();
    }
  }).then(async (result) => {
    if (result.isConfirmed) {
      try {
        const response = await api.put(`/potreros/${id}`, result.value);
        const data = response.data;
        if (data.success) {
          Swal.fire('¡Éxito!', 'Potrero actualizado correctamente', 'success');
          await cargarPotreros();
        } else {
          throw new Error(data.message || 'Error desconocido');
        }
      } catch (error) {
        console.error('Error actualizando potrero:', error);
        const errorMessage = error.response?.data?.message || error.message || 'Error desconocido';
        Swal.fire('Error', errorMessage, 'error');
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

// Función para configurar WebSocket listeners para potreros
export const configurarWebSocketPotreros = (callback) => {
   socket.on('potrero_created', (data) => {
       console.log('Nuevo potrero creado:', data);
       if (callback) callback();
   });

   socket.on('potrero_updated', (data) => {
       console.log('Potrero actualizado:', data);
       if (callback) callback();
   });

   socket.on('potrero_deleted', (data) => {
       console.log('Potrero eliminado:', data);
       if (callback) callback();
   });

   socket.on('animal_created', (data) => {
       console.log('Nuevo animal creado:', data);
       if (callback) callback();
   });

   socket.on('animal_updated', (data) => {
       console.log('Animal actualizado:', data);
       if (callback) callback();
   });

   socket.on('usuario_updated', (data) => {
       console.log('Usuario actualizado:', data);
       if (callback) callback();
   });

   socket.on('usuario_deleted', (data) => {
       console.log('Usuario eliminado:', data);
       if (callback) callback();
   });
};

export const toggleAccordion = () => {
   accordionOpen.value = !accordionOpen.value;
};

export const actualizarProximaLimpieza = async (id, fecha) => {
  try {
    const response = await api.put(`/potreros/${id}`, { proxima_limpieza: fecha });
    const data = response.data;
    if (!data.success) {
      console.error('Error actualizando próxima limpieza:', data.message);
    }
  } catch (error) {
    console.error('Error actualizando próxima limpieza:', error);
  }
};