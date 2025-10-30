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
import { potreros } from './gestionar-potreros.js';

// API configuration
const API_BASE = 'http://localhost:5000/api';

// API calls
export const cargarDatosIniciales = async () => {
  try {
    loading.value = true;
    error.value = null;

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
    const response = await fetch(`${API_BASE}/animales/estados`);
    if (response.ok) {
      const data = await response.json();
      estadosGanado.value = data.success ? data.data : [];
    } else {
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
        id_estado: animal.id_estado,
        id_potrero: animal.id_potrero,
        id_persona: animal.id_persona,
        // Campos calculados
        estado: animal.estado_tipo || 'No definido',
        potreroActual: animal.potrero_nombre || 'Sin asignar',
        propietario: animal.persona_nombre ? `${animal.persona_primer_nombre} ${animal.persona_primer_apellido}` : 'Sin asignar',
        edad: animal.fecha_nacimiento ? calcularEdad(animal.fecha_nacimiento) : 'No definida'
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
export const verPerfilAnimal = (id) => {
  const animal = animales.value.find(a => a.id === id);
  if (!animal) return;

  Swal.fire({
    title: `Perfil de ${animal.nombre}`,
    html: `
      <div class="text-start">
        <p><strong>Código QR:</strong> ${animal.codigo_qr || 'Sin código'}</p>
        <p><strong>Encargado:</strong> ${animal.propietario || 'Sin encargado'}</p>
        <p><strong>Fecha de nacimiento:</strong> ${animal.fecha_nacimiento || 'Sin dato'}</p>
        <p><strong>Peso actual:</strong> ${animal.peso_actual || 'Sin dato'} kg</p>
        <p><strong>Última vacunación:</strong> ${animal.ultima_vacunacion || 'Sin dato'}</p>
        <p><strong>Próxima vacunación:</strong> ${animal.proxima_vacunacion || 'Sin dato'}</p>
        <p><strong>Potrero actual:</strong> ${animal.potreroActual || 'Sin dato'}</p>
        <p><strong>Historial médico:</strong> Sin incidencias</p>
      </div>
    `,
    confirmButtonColor: '#00d563'
  });
};

export const editarAnimal = (id) => {
  const animal = animales.value.find(a => a.id === id);
  if (!animal) return;

  Swal.fire('Editar', `Aquí editarías al animal ${animal.nombre}`, 'info');
};

export const agregarNuevoAnimal = () => {
  // Construir opciones de estado
  let estadoOptions = '<option value="">Seleccionar estado</option>';
  estadosGanado.value.forEach(estado => {
    estadoOptions += `<option value="${estado.id}">${estado.estado}</option>`;
  });

  // Construir opciones de potrero
  let potreroOptions = '<option value="">Seleccionar potrero</option>';
  potreros.value.forEach(potrero => {
    potreroOptions += `<option value="${potrero.id}">${potrero.nombre}</option>`;
  });

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
          <select id="id_estado" class="form-control" required>
            ${estadoOptions}
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
      const id_estado = document.getElementById('id_estado').value;
      const id_potrero = document.getElementById('id_potrero').value;
      const id_persona = document.getElementById('id_persona').value;

      if (!nombre || !raza || !fecha_nacimiento || !id_estado) {
        Swal.showValidationMessage('Por favor complete todos los campos requeridos');
        return false;
      }

      return {
        nombre,
        peso: peso ? parseFloat(peso) : null,
        raza,
        fecha_nacimiento,
        id_estado: parseInt(id_estado),
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
