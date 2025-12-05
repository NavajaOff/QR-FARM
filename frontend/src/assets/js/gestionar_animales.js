import { ref } from 'vue';
import Swal from 'sweetalert2';
import axios from 'axios';
import io from 'socket.io-client';
import api from '../../services/api.js';

// Variables reactivas
export const currentIndex = ref(0);
export const accordionOpen = ref(true);
export const animales = ref([]);
export const estadosGanado = ref([]);
export const personasUsuario = ref([]);
export const loading = ref(true);
export const error = ref(null);

const findPotreroById = (potreroId) => potreros.value.find(p => p.id == potreroId);

const buildPersonaNombre = (persona) => {
  if (!persona) return null;
  if (persona.nombre_completo) return persona.nombre_completo;
  const partes = [
    persona.primer_nombre,
    persona.segundo_nombre,
    persona.primer_apellido,
    persona.segundo_apellido
  ].filter(Boolean);
  const nombreCompuesto = partes.join(' ').trim();
  return nombreCompuesto || null;
};

const obtenerNombrePersonaPorId = (personaId, fallback = 'Sin asignar') => {
  if (!personaId) return fallback;
  const persona = personasUsuario.value.find(p => p.id == personaId);
  const nombre = buildPersonaNombre(persona);
  if (nombre) return nombre;
  return `Persona ${personaId}`;
};

const obtenerNombrePersonaDesdeEntidad = (entidad, fallback = 'Sin asignar') => {
  if (!entidad) return fallback;
  if (entidad.persona_nombre) return entidad.persona_nombre;
  if (entidad.propietario) return entidad.propietario;
  return obtenerNombrePersonaPorId(entidad.id_persona, fallback);
};

const obtenerNombrePotreroPorId = (potreroId, fallback = 'Sin asignar') => {
  if (!potreroId) return fallback;
  const potrero = findPotreroById(potreroId);
  if (potrero?.nombre) return potrero.nombre;
  return `Potrero ${potreroId}`;
};

const obtenerNombrePotreroDesdeEntidad = (entidad, fallback = 'Sin asignar') => {
  if (!entidad) return fallback;
  if (entidad.potrero_nombre) return entidad.potrero_nombre;
  if (entidad.potreroActual) return entidad.potreroActual;
  return obtenerNombrePotreroPorId(entidad.id_potrero, fallback);
};

// Control de cancelación con Axios
let cancelTokenSource = null;

// Importar potreros para el select
import { potreros, cargarDatosIniciales as cargarDatosInicialesPotreros, cargarPotreros } from './gestionar-potreros.js';
import { getApiBaseUrl, getBackendUrl } from '../../utils/config.js';

// API configuration
const API_BASE = getApiBaseUrl();

// WebSocket configuration
const socket = io(getBackendUrl());

// Función para actualizar la lista en el componente Vue
let updateCallback = null;

export const setUpdateCallback = (callback) => {
   updateCallback = callback;

   // Configurar listeners de WebSocket para actualizaciones en tiempo real
   socket.on('animal_created', (data) => {
       console.log('Nuevo animal creado:', data);
       if (updateCallback) {
           updateCallback();
       }
   });

   socket.on('animal_updated', (data) => {
       console.log('Animal actualizado:', data);
       if (updateCallback) {
           updateCallback();
       }
   });

   socket.on('potrero_created', (data) => {
       console.log('Nuevo potrero creado:', data);
       if (updateCallback) {
           updateCallback();
       }
   });

   socket.on('potrero_updated', (data) => {
       console.log('Potrero actualizado:', data);
       if (updateCallback) {
           updateCallback();
       }
   });

   socket.on('potrero_deleted', (data) => {
       console.log('Potrero eliminado:', data);
       if (updateCallback) {
           updateCallback();
       }
   });

   socket.on('usuario_updated', (data) => {
       console.log('Usuario actualizado:', data);
       if (updateCallback) {
           updateCallback();
       }
   });

   socket.on('usuario_deleted', (data) => {
       console.log('Usuario eliminado:', data);
       if (updateCallback) {
           updateCallback();
       }
   });
};

// Función para cancelar peticiones pendientes
export const cancelPendingRequests = () => {
  if (cancelTokenSource) {
    cancelTokenSource.cancel('Navegación cancelada por el usuario');
    cancelTokenSource = null;
  }
};

// API calls
export const cargarDatosIniciales = async () => {
  try {
    // Cancelar peticiones anteriores si existen
    cancelPendingRequests();

    // Crear nuevo cancel token para esta carga
    cancelTokenSource = axios.CancelToken.source();

    loading.value = true;
    error.value = null;

    // Cargar datos iniciales de potreros para que estén disponibles
    await cargarDatosInicialesPotreros();

    // Verificar si fue cancelado
    if (cancelTokenSource?.token?.reason) {
      return;
    }

    await Promise.all([
      cargarEstadosGanado(true, false), // Solo cargar estados activos inicialmente
      cargarPersonasUsuario()
    ]);

    // Verificar si fue cancelado
    if (cancelTokenSource?.token?.reason) {
      return;
    }

    await cargarAnimales();
  } catch (error) {
    if (axios.isCancel(error)) {
    return;
    }
    error.value = error.message;
    loading.value = false;
  }
};

export const cargarEstadosGanado = async (soloActivos = false, soloBajas = false) => {
  try {
    let url = '/animales/estados-ganado';
    const params = [];
    if (soloActivos) params.push('solo_activos=true');
    if (soloBajas) params.push('solo_bajas=true');
    if (params.length > 0) url += '?' + params.join('&');

    const response = await api.get(url, {
      cancelToken: cancelTokenSource?.token,
      timeout: 10000
    });
    estadosGanado.value = response.data.success ? response.data.data : [];
  } catch (error) {
    if (axios.isCancel(error)) {
      return;
    }
    console.error(`Error cargando estados de ganado: ${error.message}`);
    estadosGanado.value = [];
  }
};

export const cargarPersonasUsuario = async () => {
  try {
    const response = await api.get('/potreros/personas-usuario', {
      cancelToken: cancelTokenSource?.token,
      timeout: 10000
    });
    // Usar el mismo array que en potreros
    personasUsuario.value = response.data.success ? response.data.data : [];
  } catch (error) {
    if (axios.isCancel(error)) {
      return;
    }
    personasUsuario.value = [];
  }
};


export const cargarAnimales = async (incluirBajas = false) => {
  try {
    console.log('[DEBUG] cargarAnimales - incluirBajas:', incluirBajas);
    const url = '/animales/';
    console.log('[DEBUG] URL de la petición:', url);
    const response = await api.get(url, {
      cancelToken: cancelTokenSource?.token,
      timeout: 15000  // Timeout más largo para listas grandes
    });
    console.log('[DEBUG] Respuesta HTTP ganado:', response.status);
    console.log('Cantidad de animales recibidos:', response.data?.data?.length || 0);

    if (response.data.success && response.data.data) {
      // Filtrar animales según el parámetro incluirBajas
      let animalesFiltrados;
      if (incluirBajas) {
        // Solo mostrar dados de baja (id_estado >= 4)
        animalesFiltrados = response.data.data.filter(animal => {
          const idEstado = Number.parseInt(animal.id_estado, 10);
          return idEstado >= 4;
        });
      } else {
        // Solo mostrar activos (id_estado < 4 o null)
        animalesFiltrados = response.data.data.filter(animal => {
          const idEstado = Number.parseInt(animal.id_estado, 10);
          return !idEstado || idEstado < 4;
        });
      }

      animales.value = animalesFiltrados.map(animal => {
        const estadoFinal = animal.estado_tipo || animal.estado || 'No definido';
        console.log(`[DEBUG] Mapeando animal id=${animal.id}: estado_tipo=${animal.estado_tipo}, estado=${animal.estado}, id_estado=${animal.id_estado}, estadoFinal=${estadoFinal}`);
        return {
          id: animal.id,
          nombre: animal.nombre,
          peso: animal.peso,
          raza: animal.raza,
          fecha_nacimiento: animal.fecha_nacimiento,
          sexo: animal.sexo,
          id_estado: animal.id_estado,
          id_potrero: animal.id_potrero,
          id_persona: animal.id_persona,
          // Determinar si está dado de baja:
          // - Sistema nuevo: por id_estado (>= 4)
          es_dado_de_baja: (animal.id_estado && animal.id_estado >= 4),
          // Campos calculados
          estado: estadoFinal,
          potreroActual: obtenerNombrePotreroDesdeEntidad(animal),
          propietario: obtenerNombrePersonaDesdeEntidad(animal),
          edad: animal.fecha_nacimiento ? calcularEdad(animal.fecha_nacimiento) : 'No definida',
          codigo_qr: animal.codigo_qr
        };
      });
      console.log('Animales cargados exitosamente:', animales.value.length, 'animales');
    } else {
      // Si no hay datos, mostrar lista vacía (modo sin BD)
      animales.value = [];
      console.log('No hay animales en la base de datos (modo sin BD)');
    }
  } catch (error) {
    if (axios.isCancel(error)) {
      return;
    }
    error.value = error.message;
  } finally {
    loading.value = false;
  }
};

// Utility functions
export const calcularEdad = (fechaNacimiento) => {
  if (!fechaNacimiento) return Number.NaN;
  const nacimiento = new Date(fechaNacimiento);
  const hoy = new Date();
  let edad = hoy.getFullYear() - nacimiento.getFullYear();
  const mes = hoy.getMonth() - nacimiento.getMonth();
  if (mes < 0 || (mes === 0 && hoy.getDate() < nacimiento.getDate())) {
    edad--;
  }
  return edad;
};

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
  if (estado === 'saludable') return 'bg-success';
  if (estado === 'revision') return 'bg-warning';
  if (estado === 'enfermo') return 'bg-danger';
  return 'bg-secondary';
};

export const iconClass = (animal) => {
  if (animal.estado === 'activo') return 'text-success';
  if (animal.estado === 'en_tratamiento') return 'text-warning';
  return 'text-danger';
};

// CRUD operations
export const verPerfilAnimal = async (id) => {
  const animal = animales.value.find(a => a.id === id);
  if (!animal) return;

  // Obtener datos actualizados del animal desde el backend
  try {
    const response = await api.get(`/animales/${animal.id}`);
    const data = response.data;
    if (data.success) {
      const animalActualizado = data.data;
      
      // Debug: verificar qué datos de vacunas recibimos
      console.log('[PERFIL_ANIMAL] Datos recibidos:', {
        id: animalActualizado.id,
        nombre: animalActualizado.nombre,
        vacunas: animalActualizado.vacunas,
        vacunas_tipo: typeof animalActualizado.vacunas,
        vacunas_length: animalActualizado.vacunas?.length
      });

      const encargado = obtenerNombrePersonaDesdeEntidad(animalActualizado, 'Sin encargado');
      const potreroNombre = obtenerNombrePotreroDesdeEntidad(animalActualizado, 'Sin dato');
      
      // Formatear información de vacunas
      let vacunasInfo = 'Sin vacunas registradas';
      if (animalActualizado.vacunas && Array.isArray(animalActualizado.vacunas) && animalActualizado.vacunas.length > 0) {
        console.log('[PERFIL_ANIMAL] Procesando vacunas:', animalActualizado.vacunas);
        const vacunasCount = animalActualizado.vacunas.length;
        const ultimaVacuna = animalActualizado.vacunas[0]; // La más reciente (ordenadas por fecha DESC)
        const nombreVacuna = ultimaVacuna.nombre_vacuna || ultimaVacuna.nombre || 'Vacuna';
        const fechaAplicacion = ultimaVacuna.fecha_aplicacion ? formatDate(ultimaVacuna.fecha_aplicacion) : null;
        const estadoVacuna = ultimaVacuna.estado || 'pendiente';
        const proximaDosis = ultimaVacuna.proxima_dosis ? formatDate(ultimaVacuna.proxima_dosis) : null;
        
        // Contar vacunas pendientes
        const vacunasPendientes = animalActualizado.vacunas.filter(v => 
          v.estado === 'pendiente' || !v.fecha_aplicacion
        ).length;
        
        let infoDetalle = '';
        if (fechaAplicacion) {
          infoDetalle = `Última: ${nombreVacuna} aplicada el ${fechaAplicacion}`;
        } else {
          infoDetalle = `Pendiente: ${nombreVacuna}`;
        }
        
        if (proximaDosis) {
          infoDetalle += `. Próxima dosis: ${proximaDosis}`;
        }
        
        if (vacunasPendientes > 0) {
          vacunasInfo = `${vacunasCount} vacuna(s) registrada(s) (${vacunasPendientes} pendiente(s)). ${infoDetalle}`;
        } else {
          vacunasInfo = `${vacunasCount} vacuna(s) registrada(s). ${infoDetalle}`;
        }
      }

      Swal.fire({
        title: `Perfil de ${animalActualizado.nombre}`,
        html: `
          <div class="text-start">
            <p><strong>Código QR:</strong> ${animalActualizado.codigo_qr || 'Sin código'}</p>
            <p><strong>Sexo:</strong> ${animalActualizado.sexo || 'Sin dato'}</p>
            <p><strong>Raza:</strong> ${animalActualizado.raza || 'Sin dato'}</p>
            <p><strong>Encargado:</strong> ${encargado}</p>
            <p><strong>Fecha de nacimiento:</strong> ${animalActualizado.fecha_nacimiento ? formatDate(animalActualizado.fecha_nacimiento) : 'Sin dato'}</p>
            <p><strong>Peso actual:</strong> ${animalActualizado.peso || 'Sin dato'} kg</p>
            <p><strong>Estado:</strong> ${animalActualizado.estado_tipo || animalActualizado.estado || 'Sin dato'}</p>
            <p><strong>Potrero actual:</strong> ${potreroNombre}</p>
            <p><strong>Vacunas:</strong> ${vacunasInfo}</p>
            ${animalActualizado.codigo_qr ? `<div class="mt-3"><img src="${API_BASE}/animales/qr/${animalActualizado.codigo_qr}.png" alt="Código QR" class="img-fluid" style="max-width: 300px;"></div>` : ''}
          </div>
        `,
        confirmButtonColor: '#00d563',
        width: '600px',
        didOpen: () => {
          // Detener cualquier reproducción de audio/video que pueda estar causando el error
          const mediaElements = document.querySelectorAll('audio, video');
          for (const element of mediaElements) {
            element.pause();
          }
        }
      });
    } else {
      throw new Error(data.message || 'Error desconocido');
    }
  } catch (error) {
    console.error('Error obteniendo perfil del animal:', error);
    // Mostrar perfil con datos locales si falla la petición
    const encargadoLocal = obtenerNombrePersonaDesdeEntidad(animal, 'Sin encargado');
    const potreroLocal = obtenerNombrePotreroDesdeEntidad(animal, 'Sin dato');
    
    // Formatear información de vacunas (datos locales)
    let vacunasInfoLocal = 'Sin vacunas registradas';
    if (animal.vacunas && Array.isArray(animal.vacunas) && animal.vacunas.length > 0) {
      const vacunasCount = animal.vacunas.length;
      const ultimaVacuna = animal.vacunas[0];
      const nombreVacuna = ultimaVacuna.nombre_vacuna || ultimaVacuna.nombre || 'Vacuna';
      const fechaAplicacion = ultimaVacuna.fecha_aplicacion ? formatDate(ultimaVacuna.fecha_aplicacion) : null;
      const estadoVacuna = ultimaVacuna.estado || 'pendiente';
      const proximaDosis = ultimaVacuna.proxima_dosis ? formatDate(ultimaVacuna.proxima_dosis) : null;
      
      // Contar vacunas pendientes
      const vacunasPendientes = animal.vacunas.filter(v => 
        v.estado === 'pendiente' || !v.fecha_aplicacion
      ).length;
      
      let infoDetalle = '';
      if (fechaAplicacion) {
        infoDetalle = `Última: ${nombreVacuna} aplicada el ${fechaAplicacion}`;
      } else {
        infoDetalle = `Pendiente: ${nombreVacuna}`;
      }
      
      if (proximaDosis) {
        infoDetalle += `. Próxima dosis: ${proximaDosis}`;
      }
      
      if (vacunasPendientes > 0) {
        vacunasInfoLocal = `${vacunasCount} vacuna(s) registrada(s) (${vacunasPendientes} pendiente(s)). ${infoDetalle}`;
      } else {
        vacunasInfoLocal = `${vacunasCount} vacuna(s) registrada(s). ${infoDetalle}`;
      }
    }

    Swal.fire({
      title: `Perfil de ${animal.nombre}`,
      html: `
        <div class="text-start">
          <p><strong>Código QR:</strong> ${animal.codigo_qr || 'Sin código'}</p>
          <p><strong>Sexo:</strong> ${animal.sexo || 'Sin dato'}</p>
          <p><strong>Raza:</strong> ${animal.raza || 'Sin dato'}</p>
          <p><strong>Encargado:</strong> ${encargadoLocal}</p>
          <p><strong>Fecha de nacimiento:</strong> ${animal.fecha_nacimiento || 'Sin dato'}</p>
          <p><strong>Peso actual:</strong> ${animal.peso || 'Sin dato'} kg</p>
          <p><strong>Estado:</strong> ${animal.estado || 'Sin dato'}</p>
          <p><strong>Potrero actual:</strong> ${potreroLocal}</p>
          <p><strong>Vacunas:</strong> ${vacunasInfoLocal}</p>
          ${animal.codigo_qr ? `<div class="mt-3"><img src="${API_BASE}/animales/qr/${animal.codigo_qr}.png" alt="Código QR" class="img-fluid" style="max-width: 300px;"></div>` : ''}
        </div>
      `,
      confirmButtonColor: '#00d563',
      width: '600px'
    });
  }
};

// Helper functions for editarAnimal
async function asegurarDatosFormulario(soloEstadosActivos = true) {
  if (estadosGanado.value.length && personasUsuario.value.length) return;

  try {
    await Promise.all([
      cargarEstadosGanado(soloEstadosActivos, false),
      cargarPersonasUsuario()
    ]);
  } catch (error) {
    console.error('Error cargando datos para formulario:', error);
    Swal.fire('Error', 'No se pudieron cargar los datos necesarios', 'error');
    throw new Error('DATOS_INCOMPLETOS');
  }
}

function construirOpcionesEstado(animal) {
  return [
    `<option value="">Seleccionar estado</option>`,
    ...estadosGanado.value.map(e =>
      `<option value="${e.estado}" ${e.estado === animal.estado ? 'selected' : ''}>${e.estado}</option>`
    )
  ].join('');
}

function construirOpcionesSexo(animal) {
  return `
    <option value="">Seleccionar sexo</option>
    <option value="macho" ${animal.sexo === 'macho' ? 'selected' : ''}>Macho</option>
    <option value="hembra" ${animal.sexo === 'hembra' ? 'selected' : ''}>Hembra</option>
  `;
}

function construirOpcionesPotrero(animal) {
  return [
    `<option value="">Seleccionar potrero</option>`,
    ...potreros.value.map(p =>
      `<option value="${p.id}" ${p.id === animal.id_potrero ? 'selected' : ''}>${p.nombre}</option>`
    )
  ].join('');
}

function construirOpcionesPropietario(animal) {
  return [
    `<option value="">Seleccionar propietario</option>`,
    ...personasUsuario.value.map(p => {
      const nombre = `${p.primer_nombre} ${p.primer_apellido}`.trim();
      return `<option value="${p.id}" ${p.id === animal.id_persona ? 'selected' : ''}>${nombre}</option>`;
    })
  ].join('');
}

function generarFormularioEdicion(a, opts) {
  return `
    <form class="text-start">
      <div class="mb-3"><label>Nombre:</label>
        <input id="edit_nombre" class="form-control" value="${a.nombre}">
      </div>

      <div class="mb-3"><label>Peso (kg):</label>
        <input id="edit_peso" type="number" class="form-control" value="${a.peso || ''}">
      </div>

      <div class="mb-3"><label>Raza:</label>
        <input id="edit_raza" class="form-control" value="${a.raza || ''}">
      </div>

      <div class="mb-3"><label>Estado:</label>
        <select id="edit_estado" class="form-control">${opts.estadoOptions}</select>
      </div>

      <div class="mb-3"><label>Sexo:</label>
        <select id="edit_sexo" class="form-control">${opts.sexoOptions}</select>
      </div>

      <div class="mb-3"><label>Potrero:</label>
        <select id="edit_id_potrero" class="form-control">${opts.potreroOptions}</select>
      </div>

      <div class="mb-3"><label>Propietario:</label>
        <select id="edit_id_persona" class="form-control">${opts.propietarioOptions}</select>
      </div>
    </form>`;
}

function validarYConstruirUpdate(animal) {
  const nombre = document.getElementById('edit_nombre').value.trim();
  if (!nombre) {
    Swal.showValidationMessage('El nombre es obligatorio');
    return;
  }

  const id_potrero = document.getElementById('edit_id_potrero').value;
  if (id_potrero && !validarCapacidadPotrero(id_potrero, animal)) {
    return;
  }

  const data = construirUpdateData();
  return data;
}

function validarCapacidadPotrero(id_potrero, animal = null) {
  const potrero = potreros.value.find(p => p.id === Number(id_potrero));
  if (potrero?.capacidad == null) return true;

  const capacidad = Number(potrero.capacidad);
  const ocup = Number(potrero.ocupacion || 0);
  const esMismo = animal && potrero.id === animal.id_potrero;
  const nuevaOcupacion = esMismo ? ocup : ocup + 1;

  if (capacidad > 0 && nuevaOcupacion > capacidad) {
    Swal.showValidationMessage(
      `El potrero ${potrero.nombre} no tiene cupo (${ocup}/${capacidad}).`
    );
    return false;
  }

  return true;
}

function construirUpdateData() {
  const nombre = document.getElementById('edit_nombre').value.trim();
  const peso = document.getElementById('edit_peso').value;
  const raza = document.getElementById('edit_raza').value.trim();
  const estado = document.getElementById('edit_estado').value;
  const sexo = document.getElementById('edit_sexo').value;
  const id_potrero = document.getElementById('edit_id_potrero').value;
  const id_persona = document.getElementById('edit_id_persona').value;

  const data = {
    nombre,
    peso: peso ? Number.parseFloat(peso) : null,
    raza: raza || null,
    estado: estado || null,
    sexo: sexo || null,
    id_potrero: id_potrero ? Number.parseInt(id_potrero, 10) : null,
    id_persona: id_persona ? Number.parseInt(id_persona, 10) : null
  };

  console.log('[DEBUG] construirUpdateData - estado seleccionado:', estado);
  console.log('[DEBUG] construirUpdateData - data completa:', data);
  return limpiarCampos(data);
}

function limpiarCampos(data) {
  const cleaned = Object.fromEntries(
    Object.entries(data).filter(([_, value]) => value !== null && value !== undefined && value !== '')
  );
  console.log('[DEBUG] limpiarCampos - data original:', data);
  console.log('[DEBUG] limpiarCampos - data limpiada:', cleaned);
  return cleaned;
}

function mostrarModalEditarAnimal(animal, opts, onConfirm) {
  Swal.fire({
    title: `<i class="fas fa-edit"></i> Editar Animal: ${animal.nombre}`,
    html: generarFormularioEdicion(animal, opts),
    focusConfirm: false,
    showCancelButton: true,
    confirmButtonText: 'Actualizar',
    preConfirm: () => validarYConstruirUpdate(animal)
  }).then(res => {
    if (res.isConfirmed) onConfirm(res.value);
  });
}

async function actualizarAnimal(id, data) {
  try {
    const res = await api.put(`/animales/${id}`, data);
    const json = res.data;
    console.log('[DEBUG] Respuesta de actualizarAnimal:', json);
    if (json.data) {
      console.log('[DEBUG] Animal actualizado recibido:', json.data);
      console.log('[DEBUG] Estado del animal actualizado: estado_tipo=', json.data.estado_tipo, ', estado=', json.data.estado, ', id_estado=', json.data.id_estado);
    }
    if (!json.success) throw new Error(json.message || 'Error desconocido');

    Swal.fire('Éxito', 'Animal actualizado correctamente', 'success');
    await cargarPotreros();
    await cargarAnimales();

    if (updateCallback) updateCallback();

  } catch (err) {
    console.error(err);
    Swal.fire('Error', err.message, 'error');
  }
}

export const editarAnimal = async (id) => {
  const animal = animales.value.find(a => a.id === id);
  if (!animal) return;

  try {
    await asegurarDatosFormulario();
  } catch {
    return; // datos no listos
  }

  const estadoOptions = construirOpcionesEstado(animal);
  const sexoOptions = construirOpcionesSexo(animal);
  const potreroOptions = construirOpcionesPotrero(animal);
  const propietarioOptions = construirOpcionesPropietario(animal);

  mostrarModalEditarAnimal(animal, {
    estadoOptions,
    sexoOptions,
    potreroOptions,
    propietarioOptions
  }, async (updateData) => {
    await actualizarAnimal(id, updateData);
  });
};

export const agregarNuevoAnimal = async () => {
  try {
    await asegurarDatosFormulario();
  } catch {
    return; // datos no listos
  }

  Swal.fire({
    title: 'Agregar Animal',
    html: `
      <form class="text-start">
        <div class="mb-3"><label class="form-label">Nombre:</label><input type="text" id="nombre" class="form-control" placeholder="Ej: Holstein-001" required></div>
        <div class="mb-3"><label class="form-label">Peso (kg):</label><input type="number" id="peso" class="form-control" placeholder="Ej: 450" min="0" step="0.1"></div>
        <div class="mb-3"><label class="form-label">Raza:</label><input type="text" id="raza" class="form-control" placeholder="Ej: Holstein" required></div>
        <div class="mb-3"><label class="form-label">Fecha de nacimiento:</label><input type="date" id="fecha_nacimiento" class="form-control" required></div>
        <div class="mb-3">
          <label class="form-label">Estado:</label>
          <select id="estado" class="form-control" required>
            <option value="">Seleccionar estado</option>
            ${estadosGanado.value.map(e => `<option value="${e.estado}">${e.estado}</option>`).join('')}
          </select>
        </div>
        <div class="mb-3">
          <label class="form-label">Sexo:</label>
          <select id="sexo" class="form-control" required>
            <option value="">Seleccionar sexo</option>
            <option value="macho">Macho</option>
            <option value="hembra">Hembra</option>
          </select>
        </div>
        <div class="mb-3">
          <label class="form-label">Potrero actual:</label>
          <select id="id_potrero" class="form-control">
            <option value="">Seleccionar potrero</option>
            ${potreros.value.map(p => `<option value="${p.id}">${p.nombre}</option>`).join('')}
          </select>
        </div>
        <div class="mb-3">
          <label class="form-label">Propietario:</label>
          <select id="id_persona" class="form-control">
            <option value="">Seleccionar propietario</option>
            ${personasUsuario.value.map(p => {
              const nombre = `${p.primer_nombre} ${p.primer_apellido}`.trim();
              return `<option value="${p.id}">${nombre}</option>`;
            }).join('')}
          </select>
        </div>
      </form>
    `,
    width: '600px',
    showCancelButton: true,
    confirmButtonText: 'Agregar',
    confirmButtonColor: '#00d563',
    preConfirm: () => {
      const nombre = document.getElementById('nombre').value;
      const raza = document.getElementById('raza').value;
      const fecha_nacimiento = document.getElementById('fecha_nacimiento').value;
      const estado = document.getElementById('estado').value;
      const sexo = document.getElementById('sexo').value;
      const id_potrero = document.getElementById('id_potrero').value;
      const id_persona = document.getElementById('id_persona').value;
      const peso = document.getElementById('peso').value;

      if (!nombre || !raza || !fecha_nacimiento || !estado || !sexo) {
        Swal.showValidationMessage('Complete todos los campos requeridos');
        throw new Error('VALIDATION_ERROR');
      }

      validarCapacidadPotrero(id_potrero);

      const data = {
        nombre,
        peso: peso ? Number.parseFloat(peso) : null,
        raza,
        fecha_nacimiento,
        estado,
        sexo,
        id_potrero: id_potrero ? Number.parseInt(id_potrero, 10) : null,
        id_persona: id_persona ? Number.parseInt(id_persona, 10) : null
      };

      return limpiarCampos(data);
    }
  }).then(async result => {
    if (!result.isConfirmed) return;

    try {
      const response = await api.post('/animales/', result.value);
      const data = response.data;

      if (data.success === true || data.status === 'success') {
        Swal.fire('Éxito', 'Animal agregado', 'success');
        await cargarPotreros();
        await cargarAnimales();
        if (updateCallback) updateCallback();
      } else {
        throw new Error(data.message || 'Error desconocido');
      }
    } catch (error) {
      console.error('Error creando animal:', error);
      const errorMessage = error.response?.data?.message || error.message || 'No se pudo crear el animal';
      Swal.fire('Error', errorMessage, 'error');
    }
  });
};

export const darBajaAnimal = async (id, incluirBajas = false) => {
  // Cargar estados de baja
  try {
    await cargarEstadosGanado(false, true);
  } catch (error) {
    console.error('Error cargando estados de baja:', error);
    Swal.fire('Error', 'No se pudieron cargar los estados de baja', 'error');
    return { success: false, message: 'Error cargando estados' };
  }

  const causaOptions = estadosGanado.value.map(e =>
    `<option value="${e.estado}">${e.estado}</option>`
  ).join('');
  
  const result = await Swal.fire({
    title: 'Dar de baja animal',
    html: `
      <form class="text-start">
        <div class="mb-3">
          <label class="form-label">Causa de baja *</label>
          <select id="causa_baja" class="form-control" required>
            <option value="">Seleccionar causa</option>
            ${causaOptions}
          </select>
        </div>
        <div class="mb-3">
          <label class="form-label">Observaciones</label>
          <textarea id="observaciones_baja" class="form-control" rows="3" 
                    placeholder="Detalles adicionales sobre la baja (opcional)"></textarea>
        </div>
      </form>
    `,
    showCancelButton: true,
    confirmButtonText: 'Dar de baja',
    cancelButtonText: 'Cancelar',
    confirmButtonColor: '#d33',
    cancelButtonColor: '#3085d6',
    allowOutsideClick: true,
    allowEscapeKey: true,
    preConfirm: () => {
      const causa = document.getElementById('causa_baja').value;
      const observaciones = document.getElementById('observaciones_baja').value;

      if (!causa) {
        Swal.showValidationMessage('Debe seleccionar una causa de baja');
        return { valid: false };
      }

      return { valid: true, data: { causa_baja: causa, observaciones: observaciones || null } };
    }
  });
  
  if (result.isConfirmed && result.value.valid) {
    try {
      const response = await api.put(`/animales/${id}/baja`, result.value.data);
      const data = response.data;
      
      if (data.success) {
        Swal.fire('Éxito', 'Animal dado de baja correctamente', 'success');
        await cargarPotreros();
        await cargarAnimales();
        if (updateCallback) updateCallback();
        return { success: true };
      } else {
        throw new Error(data.message || 'Error al dar de baja');
      }
    } catch (error) {
      console.error('Error dando de baja animal:', error);
      const errorMessage = error.response?.data?.message || error.message || 'Baja failed';
      Swal.fire('Error', errorMessage, 'error');
      return { success: false, message: errorMessage };
    }
  }
  
  return { success: false, message: 'Operación cancelada' };
};

export const reactivarAnimal = async (id, incluirBajas = false) => {
  // Cargar estados activos
  try {
    const estadosResponse = await api.get('/animales/estados-ganado?solo_activos=true');
    const estadosActivos = estadosResponse.data.data || estadosResponse.data || [];
    
    const estadoOptions = estadosActivos.map(e => 
      `<option value="${e.estado || e.nombre_estado}">${e.estado || e.nombre_estado}</option>`
    ).join('');
    
    const result = await Swal.fire({
      title: 'Reactivar animal',
      html: `
        <form class="text-start">
          <p>¿Está seguro de que desea reactivar este animal?</p>
          <div class="mb-3">
            <label class="form-label">Nuevo estado *</label>
            <select id="nuevo_estado" class="form-control" required>
              <option value="">Seleccionar estado</option>
              ${estadoOptions}
            </select>
          </div>
        </form>
      `,
      icon: 'question',
      showCancelButton: true,
      confirmButtonText: 'Sí, reactivar',
      cancelButtonText: 'Cancelar',
      confirmButtonColor: '#28a745',
      cancelButtonColor: '#6c757d',
      allowOutsideClick: true,
      allowEscapeKey: true,
      preConfirm: () => {
        const nuevoEstado = document.getElementById('nuevo_estado').value;
        if (!nuevoEstado) {
          Swal.showValidationMessage('Debe seleccionar un estado');
          return { valid: false };
        }
        return { valid: true, data: { nuevo_estado: nuevoEstado } };
      }
    });
    
    if (result.isConfirmed && result.value.valid) {
      try {
        const response = await api.put(`/animales/${id}/reactivar`, result.value.data);
        const data = response.data;
        
        if (data.success) {
          Swal.fire('Éxito', 'Animal reactivado correctamente', 'success');
          await cargarPotreros();
          await cargarAnimales();
          if (updateCallback) updateCallback();
          return { success: true };
        } else {
          throw new Error(data.message || 'Error al reactivar');
        }
      } catch (error) {
        console.error('Error reactivando animal:', error);
        const errorMessage = error.response?.data?.message || error.message || 'Reactivar failed';
        Swal.fire('Error', errorMessage, 'error');
        return { success: false, message: errorMessage };
      }
    }
    
    return { success: false, message: 'Operación cancelada' };
  } catch (error) {
    console.error('Error cargando estados activos:', error);
    Swal.fire('Error', 'No se pudieron cargar los estados activos', 'error');
    return { success: false, message: error.message };
  }
};

// Mantener función legacy para compatibilidad
export const eliminarAnimal = async (id) => {
  return await darBajaAnimal(id);
};

// Función para limpiar estado al cambiar de ruta
export const resetEstado = () => {
  cancelPendingRequests();
  loading.value = true;
  error.value = null;
  // Limpiamos arrays para forzar recarga fresca
  animales.value = [];
  estadosGanado.value = [];
  personasUsuario.value = [];
};

// Navigation
export const prevAnimal = () => {
  if (animales.value.length > 1) {
    currentIndex.value = (currentIndex.value - 1 + animales.value.length) % animales.value.length;
    accordionOpen.value = true;
  }
};

export const nextAnimal = () => {
  if (animales.value.length > 1) {
    currentIndex.value = (currentIndex.value + 1) % animales.value.length;
    accordionOpen.value = true;
  }
};

export const toggleAccordion = () => {
  accordionOpen.value = !accordionOpen.value;
};
