import Swal from 'sweetalert2';
import { vacunacionAPI, ganadoAPI, userAPI } from '../../services/api.js';

const defaultConfig = {
  registroValidacionMsg: 'Por favor complete todos los campos requeridos',
  eliminarLogPrefix: 'Frontend'
};

const buildDefaultEditForm = (vacunacion) => `
  <div class="row g-3">
    <div class="col-12">
      <label class="form-label">Estado</label>
      <select id="estado" class="form-select">
        <option value="pendiente" ${vacunacion.estado === 'pendiente' ? 'selected' : ''}>Pendiente</option>
        <option value="aplicado" ${vacunacion.estado === 'aplicado' ? 'selected' : ''}>Aplicado</option>
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
  </div>
`;

export const collectDefaultEditPayload = () => {
  const estado = document.getElementById('estado').value;
  const fechaAplicacion = document.getElementById('fechaAplicacion').value;
  const proximaDosis = document.getElementById('proximaDosis').value;

  return {
    valid: true,
    payload: {
      estado,
      fecha_aplicacion: fechaAplicacion || null,
      proxima_dosis: proximaDosis || null
    },
    message: ''
  };
};

export const registroVacunacionBase = {
  data() {
    return {
      filtros: { animal: '', vacuna: '', fechaDesde: '', fechaHasta: '' },
      vacunaciones: [],
      animales: [],
      tiposVacuna: [],
      personas: [],
      loading: false
    };
  },
  computed: {
    filteredVacunaciones() {
      return this.vacunaciones.filter(v => {
        // Filtro por animal (ID o nombre)
        if (this.filtros.animal) {
          const searchTerm = this.filtros.animal.toLowerCase();
          const matchesId = v.idAnimal.toString().includes(searchTerm);
          const matchesName = v.nombre?.toLowerCase().includes(searchTerm);
          if (!matchesId && !matchesName) return false;
        }

        // Filtro por tipo de vacuna
        if (this.filtros.vacuna && v.tipoVacuna !== this.filtros.vacuna) return false;

        // Filtro por fecha desde
        if (this.filtros.fechaDesde && v.fechaAplicacion) {
          const fechaAplicacion = new Date(v.fechaAplicacion.split('T')[0]);
          const fechaDesde = new Date(this.filtros.fechaDesde);
          if (fechaAplicacion < fechaDesde) return false;
        }

        // Filtro por fecha hasta
        if (this.filtros.fechaHasta && v.fechaAplicacion) {
          const fechaAplicacion = new Date(v.fechaAplicacion.split('T')[0]);
          const fechaHasta = new Date(this.filtros.fechaHasta);
          if (fechaAplicacion > fechaHasta) return false;
        }

        return true;
      });
    }
  },
  async mounted() {
    await this.cargarDatos();
  },
  methods: {
    async cargarDatos() {
      this.loading = true;
      try {
        const [vacunacionesRes, animalesRes, personasRes] = await Promise.all([
          vacunacionAPI.getAll(),
          ganadoAPI.getAll(),
          userAPI.getAll()
        ]);

        this.vacunaciones = vacunacionesRes.data?.data || [];
        this.animales = animalesRes.data?.data || [];
        this.personas = personasRes.data?.data || [];

        await this.obtenerTiposVacuna();
      } catch (error) {
        console.error('Error cargando datos:', error);
        Swal.fire('Error', 'No se pudieron cargar los datos', 'error');
      } finally {
        this.loading = false;
      }
    },

    async obtenerTiposVacuna() {
      try {
        const { getApiUrl } = await import('../../utils/config.js');
        const response = await fetch(getApiUrl('/vacunaciones/tipos-vacuna'));
        const data = await response.json();
        this.tiposVacuna = data.data || [];
      } catch (error) {
        console.error('Error obteniendo tipos de vacuna:', error);
      }
    },

    estadoClass(estado) {
      if (estado === 'aplicado') return 'bg-success';
      if (estado === 'pendiente') return 'bg-warning';
      return 'bg-secondary';
    },

    estadoLabel(estado) {
      if (estado === 'aplicado') return 'Aplicado';
      if (estado === 'pendiente') return 'Pendiente';
      return estado || 'Sin estado';
    },

    formatDate(dateString) {
      if (!dateString) return 'No definida';
      return dateString.split('T')[0];
    },

    async registrarVacunacion() {
      const config = { ...defaultConfig, ...this.$options.registroVacunacionConfig };

      const { value: formValues } = await Swal.fire({
        title: 'Nueva Vacunación',
        html: `
          <div class="row g-3">
            <div class="col-12">
              <label class="form-label">Animal</label>
              <select id="animal" class="form-select">
                <option value="">Seleccionar animal...</option>
                ${this.animales.map(a => `<option value="${a.id}">${a.nombre}</option>`).join('')}
              </select>
            </div>
            <div class="col-12">
              <label class="form-label">Tipo de Vacuna</label>
              <select id="tipoVacuna" class="form-select">
                <option value="">Seleccionar tipo...</option>
                ${this.tiposVacuna.map(t => `<option value="${t.id}">${t.nombre}</option>`).join('')}
              </select>
            </div>
            <div class="col-12">
              <label class="form-label">Fecha Aplicación</label>
              <input id="fechaAplicacion" type="date" class="form-control">
            </div>
            <div class="col-12">
              <label class="form-label">Responsable</label>
              <select id="responsable" class="form-select">
                <option value="">Seleccionar responsable...</option>
                ${this.personas.map(p => `<option value="${p.id}">${p.nombre}</option>`).join('')}
              </select>
            </div>
            <div class="col-12">
              <label class="form-label">Estado</label>
              <select id="estado" class="form-select">
                <option value="pendiente">Pendiente</option>
                <option value="aplicado">Aplicado</option>
              </select>
            </div>
          </div>
        `,
        focusConfirm: false,
        showCancelButton: true,
        confirmButtonText: 'Guardar',
        cancelButtonText: 'Cancelar',
        preConfirm: async () => {
          const animal = document.getElementById('animal').value;
          const tipoVacuna = document.getElementById('tipoVacuna').value;
          const fechaAplicacion = document.getElementById('fechaAplicacion').value;
          const responsable = document.getElementById('responsable').value;
          const estado = document.getElementById('estado').value;

          if (!animal || !tipoVacuna || !fechaAplicacion || !responsable) {
            Swal.showValidationMessage(config.registroValidacionMsg);
            throw new Error('VALIDATION_ERROR');
          }

          return {
            id_animal: Number.parseInt(animal, 10),
            id_tipo_vacuna: Number.parseInt(tipoVacuna, 10),
            fecha_aplicacion: fechaAplicacion,
            responsable: Number.parseInt(responsable, 10),
            estado: estado
          };
        }
      });

      if (formValues) {
        try {
          await vacunacionAPI.create(formValues);
          await this.cargarDatos();
          Swal.fire('Éxito', 'Vacunación registrada correctamente', 'success');
        } catch (error) {
          console.error('Error creando vacunación:', error);
          Swal.fire('Error', 'No se pudo registrar la vacunación', 'error');
        }
      }
    },

    generarReporte() {
      Swal.fire('Reporte PDF', 'Funcionalidad de reporte próximamente', 'info');
    },

    verVacunacion(id) {
      const v = this.vacunaciones.find(x => x.id === id);
      if (v) {
        Swal.fire({
          title: `Vacunación ${id}`,
          html: `
            <div class="text-start">
              <p><strong>Animal:</strong> ${v.nombre}</p>
              <p><strong>Tipo de Vacuna:</strong> ${v.tipoVacuna}</p>
              <p><strong>Fecha Aplicación:</strong> ${v.fechaAplicacion || 'No definida'}</p>
              <p><strong>Próxima Dosis:</strong> ${v.proximaDosis || 'No definida'}</p>
              <p><strong>Responsable:</strong> ${v.responsable}</p>
              <p><strong>Estado:</strong> <span class="badge ${this.estadoClass(v.estado)}">${this.estadoLabel(v.estado)}</span></p>
            </div>
          `,
          confirmButtonColor: '#00d563'
        });
      }
    },

    async editarVacunacion(id) {
      const v = this.vacunaciones.find(x => x.id === id);
      if (!v) return;

      const editarConfig = this.$options.registroVacunacionConfig?.editar || {};
      const buildForm = editarConfig.buildForm || buildDefaultEditForm;
      const collectPayload = editarConfig.collectPayload || collectDefaultEditPayload;

      const result = await Swal.fire({
        title: 'Editar Vacunación',
        html: buildForm(v, this),
        focusConfirm: false,
        showCancelButton: true,
        confirmButtonText: 'Actualizar',
        cancelButtonText: 'Cancelar',
        preConfirm: async () => {
          const payloadResult = await collectPayload(this, v);
          if (!payloadResult) {
            throw new Error('VALIDATION_ERROR');
          }
          if (!payloadResult.valid) {
            if (payloadResult.message) {
              Swal.showValidationMessage(payloadResult.message);
            }
            throw new Error('VALIDATION_ERROR');
          }
          return payloadResult.payload;
        }
      });

      if (result.isConfirmed && result.value) {
        try {
          await vacunacionAPI.update(id, result.value);
          await this.cargarDatos();
          Swal.fire('Éxito', 'Vacunación actualizada correctamente', 'success');
        } catch (error) {
          console.error('Error actualizando vacunación:', error);
          Swal.fire('Error', 'No se pudo actualizar la vacunación', 'error');
        }
      }
    },

    async eliminarVacunacion(id) {
      const config = { ...defaultConfig, ...this.$options.registroVacunacionConfig };
      console.log(`${config.eliminarLogPrefix}: Intentando eliminar vacunación con ID:`, id);
      const result = await Swal.fire({
        title: '¿Estás seguro?',
        text: 'Esta acción no se puede deshacer',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar'
      });

      if (result.isConfirmed) {
        try {
          console.log(`${config.eliminarLogPrefix}: Llamando a vacunacionAPI.delete con ID:`, id);
          const response = await vacunacionAPI.delete(id);
          console.log(`${config.eliminarLogPrefix}: Respuesta de delete:`, response);
          await this.cargarDatos();
          Swal.fire('Eliminado', 'La vacunación ha sido eliminada correctamente', 'success');
        } catch (error) {
          console.error(`${config.eliminarLogPrefix}: Error eliminando vacunación:`, error);
          console.error(`${config.eliminarLogPrefix}: Detalles del error:`, error.response);
          Swal.fire('Error', 'No se pudo eliminar la vacunación', 'error');
        }
      }
    }
  }
};

