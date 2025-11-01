import { ref } from 'vue';
import Swal from 'sweetalert2';

// Variables reactivas
export const currentIndex = ref(0);
export const accordionOpen = ref(true);
export const animales = ref([]);
export const estadosGanado = ref([]);
export const personasUsuario = ref([]);
export const loading = ref(true);
export const error = ref(null);

// Importar potreros para el select
import { potreros, cargarPotreros, cargarDatosIniciales as cargarDatosInicialesPotreros } from './gestionar-potreros.js';

// API configuration
const API_BASE = 'http://localhost:5000/api';

// Función para actualizar la lista en el componente Vue
let updateCallback = null;

export const setUpdateCallback = (callback) => {
  updateCallback = callback;
};

// API calls
export const cargarDatosIniciales = async () => {
  try {
    loading.value = true;
    error.value = null;

    // Cargar datos iniciales de potreros para que estén disponibles
    await cargarDatosInicialesPotreros();

    await Promise.all([
      cargarEstadosGanado(),
      cargarPersonasUsuario()
    ]);

    await cargarAnimales();
  } catch (error) {
    error.value = error.message;
    console.error('Error cargando datos iniciales:', error);
    loading.value = false;
  }
};

export const cargarEstadosGanado = async () => {
  try {
    console.log('Cargando estados de ganado...');
    const response = await fetch(`${API_BASE}/animales/estados`);
    console.log('Respuesta estados ganado:', response.status);
    if (response.ok) {
      const data = await response.json();
      console.log('Datos estados ganado:', data);
      estadosGanado.value = data.success ? data.data : [];
      console.log('Estados ganado cargados:', estadosGanado.value);
    } else {
      console.error('Error HTTP estados ganado:', response.status);
      estadosGanado.value = [];
    }
  } catch (error) {
    console.error('Error cargando estados de ganado:', error);
    estadosGanado.value = [];
  }
};

export const cargarPersonasUsuario = async () => {
  try {
    const response = await fetch(`${API_BASE}/potreros/personas-usuario`);
    if (response.ok) {
      const data = await response.json();
      // Usar el mismo array que en potreros
      personasUsuario.value = data.success ? data.data : [];
    } else {
      personasUsuario.value = [];
    }
  } catch (error) {
    console.error('Error cargando personas usuario:', error);
    personasUsuario.value = [];
  }
};

export const cargarAnimales = async () => {
  try {
    const response = await fetch(`${API_BASE}/animales/`);
    if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);

    const data = await response.json();
    if (data.success) {
      animales.value = data.data.map(animal => ({
        id: animal.id,
        nombre: animal.nombre,
        peso: animal.peso,
        raza: animal.raza,
        fecha_nacimiento: animal.fecha_nacimiento,
        sexo: animal.sexo,
        id_estado: animal.id_estado,
        id_potrero: animal.id_potrero,
        id_persona: animal.id_persona,
        // Campos calculados
        estado: animal.estado_tipo || animal.estado || 'No definido',
        potreroActual: animal.id_potrero ? (potreros.value.find(p => p.id == animal.id_potrero)?.nombre || `Potrero ${animal.id_potrero}`) : 'Sin asignar',
        propietario: animal.id_persona ? (personasUsuario.value.find(p => p.id == animal.id_persona) ? `${personasUsuario.value.find(p => p.id == animal.id_persona).primer_nombre} ${personasUsuario.value.find(p => p.id == animal.id_persona).primer_apellido}` : `Persona ${animal.id_persona}`) : 'Sin asignar',
        edad: animal.fecha_nacimiento ? calcularEdad(animal.fecha_nacimiento) : 'No definida',
        codigo_qr: animal.codigo_qr
      }));
    } else {
      throw new Error(data.message || 'Error desconocido');
    }
  } catch (error) {
    error.value = error.message;
    console.error('Error cargando animales:', error);
  } finally {
    loading.value = false;
  }
};

// Utility functions
export const calcularEdad = (fechaNacimiento) => {
  if (!fechaNacimiento) return 'No definida';
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
  return animal.estado === 'activo' ? 'text-success' : (animal.estado === 'en_tratamiento' ? 'text-warning' : 'text-danger');
};

// CRUD operations
export const verPerfilAnimal = async (id) => {
  const animal = animales.value.find(a => a.id === id);
  if (!animal) return;

  // Obtener datos actualizados del animal desde el backend
  try {
    const response = await fetch(`${API_BASE}/animales/${animal.id}`);
    if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);

    const data = await response.json();
    if (data.success) {
      const animalActualizado = data.data;

      Swal.fire({
        title: `Perfil de ${animalActualizado.nombre}`,
        html: `
          <div class="text-start">
            <p><strong>Código QR:</strong> ${animalActualizado.codigo_qr || 'Sin código'}</p>
            <p><strong>Sexo:</strong> ${animalActualizado.sexo || 'Sin dato'}</p>
            <p><strong>Raza:</strong> ${animalActualizado.raza || 'Sin dato'}</p>
            <p><strong>Encargado:</strong> ${animalActualizado.id_persona ? (personasUsuario.value.find(p => p.id == animalActualizado.id_persona) ? `${personasUsuario.value.find(p => p.id == animalActualizado.id_persona).primer_nombre} ${personasUsuario.value.find(p => p.id == animalActualizado.id_persona).primer_apellido}` : `Persona ${animalActualizado.id_persona}`) : 'Sin encargado'}</p>
            <p><strong>Fecha de nacimiento:</strong> ${animalActualizado.fecha_nacimiento ? formatDate(animalActualizado.fecha_nacimiento) : 'Sin dato'}</p>
            <p><strong>Peso actual:</strong> ${animalActualizado.peso || 'Sin dato'} kg</p>
            <p><strong>Estado:</strong> ${animalActualizado.estado_tipo || animalActualizado.estado || 'Sin dato'}</p>
            <p><strong>Potrero actual:</strong> ${animalActualizado.id_potrero ? (potreros.value.find(p => p.id == animalActualizado.id_potrero)?.nombre || `Potrero ${animalActualizado.id_potrero}`) : 'Sin dato'}</p>
            <p><strong>Historial médico:</strong> Sin incidencias</p>
            ${animalActualizado.codigo_qr ? `<div class="mt-3"><img src="http://localhost:5000/api/animales/qr/${animalActualizado.codigo_qr}.png" alt="Código QR" class="img-fluid" style="max-width: 300px;"></div>` : ''}
          </div>
        `,
        confirmButtonColor: '#00d563',
        width: '600px',
        didOpen: () => {
          // Detener cualquier reproducción de audio/video que pueda estar causando el error
          const mediaElements = document.querySelectorAll('audio, video');
          mediaElements.forEach(element => {
            element.pause();
          });
        }
      });
    } else {
      throw new Error(data.message || 'Error desconocido');
    }
  } catch (error) {
    console.error('Error obteniendo perfil del animal:', error);
    // Mostrar perfil con datos locales si falla la petición
    Swal.fire({
      title: `Perfil de ${animal.nombre}`,
      html: `
        <div class="text-start">
          <p><strong>Código QR:</strong> ${animal.codigo_qr || 'Sin código'}</p>
          <p><strong>Sexo:</strong> ${animal.sexo || 'Sin dato'}</p>
          <p><strong>Raza:</strong> ${animal.raza || 'Sin dato'}</p>
          <p><strong>Encargado:</strong> ${animal.propietario || 'Sin encargado'}</p>
          <p><strong>Fecha de nacimiento:</strong> ${animal.fecha_nacimiento || 'Sin dato'}</p>
          <p><strong>Peso actual:</strong> ${animal.peso || 'Sin dato'} kg</p>
          <p><strong>Estado:</strong> ${animal.estado || 'Sin dato'}</p>
          <p><strong>Potrero actual:</strong> ${animal.potreroActual || 'Sin dato'}</p>
          <p><strong>Historial médico:</strong> Sin incidencias</p>
          ${animal.codigo_qr ? `<div class="mt-3"><img src="http://localhost:5000/api/animales/qr/${animal.codigo_qr}.png" alt="Código QR" class="img-fluid" style="max-width: 300px;"></div>` : ''}
        </div>
      `,
      confirmButtonColor: '#00d563',
      width: '600px'
    });
  }
};

export const editarAnimal = (id) => {
  const animal = animales.value.find(a => a.id === id);
  if (!animal) return;

  // Construir opciones de estado
  let estadoOptions = '<option value="">Seleccionar estado</option>';
  estadosGanado.value.forEach(estado => {
    const selected = estado.estado === animal.estado ? 'selected' : '';
    estadoOptions += `<option value="${estado.estado}" ${selected}>${estado.estado}</option>`;
  });

  // Construir opciones de sexo
  let sexoOptions = '<option value="">Seleccionar sexo</option>';
  sexoOptions += `<option value="macho" ${animal.sexo === 'macho' ? 'selected' : ''}>Macho</option>`;
  sexoOptions += `<option value="hembra" ${animal.sexo === 'hembra' ? 'selected' : ''}>Hembra</option>`;

  // Construir opciones de potrero
  let potreroOptions = '<option value="">Seleccionar potrero</option>';
  console.log('Potreros disponibles para select:', potreros.value);
  console.log('Animal id_potrero:', animal.id_potrero);
  potreros.value.forEach(potrero => {
    const selected = potrero.id === animal.id_potrero ? 'selected' : '';
    console.log(`Comparando potrero ${potrero.id} (${potrero.nombre}) con animal.id_potrero ${animal.id_potrero}: ${selected}`);
    potreroOptions += `<option value="${potrero.id}" ${selected}>${potrero.nombre}</option>`;
  });
  console.log('Opciones potrero generadas:', potreroOptions);

  // Construir opciones de propietario
  let propietarioOptions = '<option value="">Seleccionar propietario</option>';
  personasUsuario.value.forEach(persona => {
    const nombreCompleto = `${persona.primer_nombre} ${persona.primer_apellido}`.trim();
    const selected = persona.id === animal.id_persona ? 'selected' : '';
    propietarioOptions += `<option value="${persona.id}" ${selected}>${nombreCompleto}</option>`;
  });

  Swal.fire({
    title: `<i class="fas fa-edit"></i> Editar Animal: ${animal.nombre}`,
    html: `
      <form class="text-start">
        <div class="mb-3"><label class="form-label">Nombre:</label><input type="text" id="edit_nombre" class="form-control" value="${animal.nombre}" required></div>
        <div class="mb-3"><label class="form-label">Peso (kg):</label><input type="number" id="edit_peso" class="form-control" value="${animal.peso || ''}" min="0" step="0.1"></div>
        <div class="mb-3"><label class="form-label">Raza:</label><input type="text" id="edit_raza" class="form-control" value="${animal.raza || ''}" required></div>
        <div class="mb-3">
          <label class="form-label">Estado:</label>
          <select id="edit_estado" class="form-control" required>
            ${estadoOptions}
          </select>
        </div>
        <div class="mb-3">
          <label class="form-label">Sexo:</label>
          <select id="edit_sexo" class="form-control" required>
            ${sexoOptions}
          </select>
        </div>
        <div class="mb-3">
          <label class="form-label">Potrero actual:</label>
          <select id="edit_id_potrero" class="form-control">
            ${potreroOptions}
          </select>
        </div>
        <div class="mb-3">
          <label class="form-label">Propietario:</label>
          <select id="edit_id_persona" class="form-control">
            ${propietarioOptions}
          </select>
        </div>
      </form>
    `,
    width: '600px',
    showCancelButton: true,
    confirmButtonText: 'Actualizar',
    confirmButtonColor: '#00d563',
    preConfirm: () => {
      const nombre = document.getElementById('edit_nombre').value;
      const peso = document.getElementById('edit_peso').value;
      const raza = document.getElementById('edit_raza').value;
      const estado = document.getElementById('edit_estado').value;
      const sexo = document.getElementById('edit_sexo').value;
      const id_potrero = document.getElementById('edit_id_potrero').value;
      const id_persona = document.getElementById('edit_id_persona').value;

      // Solo validar campos obligatorios
      if (!nombre) {
        Swal.showValidationMessage('El nombre es obligatorio');
        return false;
      }

      const updateData = {
        nombre,
        peso: peso ? parseFloat(peso) : null,
        raza: raza || null,
        estado: estado || null,
        sexo: sexo || null,
        id_potrero: id_potrero ? parseInt(id_potrero) : null,
        id_persona: id_persona ? parseInt(id_persona) : null
      };

      // Remover campos null/undefined para enviar solo los campos que se van a actualizar
      Object.keys(updateData).forEach(key => {
        if (updateData[key] === null || updateData[key] === undefined) {
          delete updateData[key];
        }
      });

      return updateData;
    }
  }).then(async (result) => {
    if (result.isConfirmed) {
      try {
        const response = await fetch(`${API_BASE}/animales/${id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(result.value)
        });

        if (response.ok) {
          const data = await response.json();
          if (data.success) {
            Swal.fire('¡Éxito!', 'Animal actualizado correctamente', 'success');
            await cargarAnimales();
            // Notificar al componente Vue que actualice la lista
            if (updateCallback) {
              updateCallback();
            }
          } else {
            throw new Error(data.message || 'Error desconocido');
          }
        } else {
          const errorData = await response.json();
          throw new Error(errorData.message || `Error HTTP: ${response.status}`);
        }
      } catch (error) {
        console.error('Error actualizando animal:', error);
        Swal.fire('Error', error.message, 'error');
      }
    }
  });
};

export const agregarNuevoAnimal = () => {
  // Construir opciones de estado
  let estadoOptions = '<option value="">Seleccionar estado</option>';
  estadosGanado.value.forEach(estado => {
    estadoOptions += `<option value="${estado.estado}">${estado.estado}</option>`;
  });

  // Construir opciones de sexo
  let sexoOptions = '<option value="">Seleccionar sexo</option>';
  sexoOptions += '<option value="macho">Macho</option>';
  sexoOptions += '<option value="hembra">Hembra</option>';

  // Construir opciones de potrero
  let potreroOptions = '<option value="">Seleccionar potrero</option>';
  console.log('Potreros disponibles para agregar:', potreros.value);
  potreros.value.forEach(potrero => {
    potreroOptions += `<option value="${potrero.id}">${potrero.nombre}</option>`;
  });
  console.log('Opciones potrero agregar generadas:', potreroOptions);

  // Construir opciones de propietario
  let propietarioOptions = '<option value="">Seleccionar propietario</option>';
  personasUsuario.value.forEach(persona => {
    const nombreCompleto = `${persona.primer_nombre} ${persona.primer_apellido}`.trim();
    propietarioOptions += `<option value="${persona.id}">${nombreCompleto}</option>`;
  });

  Swal.fire({
    title: '<i class="fas fa-plus"></i> Agregar Nuevo Animal',
    html: `
      <form class="text-start">
        <div class="mb-3"><label class="form-label">Nombre:</label><input type="text" id="nombre" class="form-control" placeholder="Ej: Holstein-001" required></div>
        <div class="mb-3"><label class="form-label">Peso (kg):</label><input type="number" id="peso" class="form-control" placeholder="Ej: 450" min="0" step="0.1"></div>
        <div class="mb-3"><label class="form-label">Raza:</label><input type="text" id="raza" class="form-control" placeholder="Ej: Holstein" required></div>
        <div class="mb-3"><label class="form-label">Fecha de nacimiento:</label><input type="date" id="fecha_nacimiento" class="form-control" required></div>
        <div class="mb-3">
          <label class="form-label">Estado:</label>
          <select id="estado" class="form-control" required>
            ${estadoOptions}
          </select>
        </div>
        <div class="mb-3">
          <label class="form-label">Sexo:</label>
          <select id="sexo" class="form-control" required>
            ${sexoOptions}
          </select>
        </div>
        <div class="mb-3">
          <label class="form-label">Potrero actual:</label>
          <select id="id_potrero" class="form-control">
            ${potreroOptions}
          </select>
        </div>
        <div class="mb-3">
          <label class="form-label">Propietario:</label>
          <select id="id_persona" class="form-control">
            ${propietarioOptions}
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
      const peso = document.getElementById('peso').value;
      const raza = document.getElementById('raza').value;
      const fecha_nacimiento = document.getElementById('fecha_nacimiento').value;
      const estado = document.getElementById('estado').value;
      const sexo = document.getElementById('sexo').value;
      const id_potrero = document.getElementById('id_potrero').value;
      const id_persona = document.getElementById('id_persona').value;

      if (!nombre || !raza || !fecha_nacimiento || !estado || !sexo) {
        Swal.showValidationMessage('Por favor complete todos los campos requeridos');
        return false;
      }

      return {
        nombre,
        peso: peso ? parseFloat(peso) : null,
        raza,
        fecha_nacimiento,
        estado,
        sexo,
        id_potrero: id_potrero ? parseInt(id_potrero) : null,
        id_persona: id_persona ? parseInt(id_persona) : null
      };
    }
  }).then(async (result) => {
    if (result.isConfirmed) {
      try {
        const response = await fetch(`${API_BASE}/animales/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(result.value)
        });

        if (response.ok) {
          const data = await response.json();
          if (data.success) {
            Swal.fire('¡Éxito!', 'Animal agregado correctamente', 'success');
            await cargarAnimales();
            // Notificar al componente Vue que actualice la lista
            if (updateCallback) {
              updateCallback();
            }
          } else {
            throw new Error(data.message || 'Error desconocido');
          }
        } else {
          const errorData = await response.json();
          throw new Error(errorData.message || `Error HTTP: ${response.status}`);
        }
      } catch (error) {
        console.error('Error creando animal:', error);
        Swal.fire('Error', error.message, 'error');
      }
    }
  });
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
