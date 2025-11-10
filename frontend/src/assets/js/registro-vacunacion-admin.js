import Swal from 'sweetalert2';
import { vacunacionAPI, ganadoAPI, userAPI } from '../../services/api.js';

export default {
  name: "RegistroVacunacion",
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
  async mounted() {
    await this.cargarDatos();
  },
  methods: {
    async cargarDatos() {
      this.loading = true;
      try {
        const [vacunacionesRes, animalesRes, tiposVacunaRes, personasRes] = await Promise.all([
          vacunacionAPI.getAll(),
          ganadoAPI.getAll(),
          vacunacionAPI.getAll().then(() => this.obtenerTiposVacuna()),
          userAPI.getAll()
        ]);

        this.vacunaciones = vacunacionesRes.data?.data || [];
        this.animales = animalesRes.data?.data || [];
        this.personas = personasRes.data?.data || [];
      } catch (error) {
        console.error('Error cargando datos:', error);
        Swal.fire('Error', 'No se pudieron cargar los datos', 'error');
      } finally {
        this.loading = false;
      }
    },

    async obtenerTiposVacuna() {
      try {
        const response = await fetch('http://localhost:5000/api/vacunaciones/tipos-vacuna');
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

    formatDate(dateString) {
      if (!dateString) return 'No definida';
      // Remove the time part (everything after 'T') and return just the date
      return dateString.split('T')[0];
    },

    async registrarVacunacion() {
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
        preConfirm: () => {
          const animal = document.getElementById('animal').value;
          const tipoVacuna = document.getElementById('tipoVacuna').value;
          const fechaAplicacion = document.getElementById('fechaAplicacion').value;
          const responsable = document.getElementById('responsable').value;
          const estado = document.getElementById('estado').value;

          if (!animal || !tipoVacuna || !fechaAplicacion || !responsable ) {
            Swal.showValidationMessage('Por favor complete todos los campos ');
            return false;
          }

          return {
            id_animal: parseInt(animal),
            id_tipo_vacuna: parseInt(tipoVacuna),
            fecha_aplicacion: fechaAplicacion,
            responsable: parseInt(responsable),
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
              <p><strong>Estado:</strong> <span class="badge ${this.estadoClass(v.estado)}">${v.estado === 'aplicado' ? 'Aplicado' : v.estado === 'pendiente' ? 'Pendiente' : v.estado}</span></p>
            </div>
          `,
          confirmButtonColor: '#00d563'
        });
      }
    },

    async editarVacunacion(id) {
      const v = this.vacunaciones.find(x => x.id === id);
      if (!v) return;

      const { value: formValues } = await Swal.fire({
        title: 'Editar Vacunación',
        html: `
          <div class="row g-3">
            <div class="col-12">
              <label class="form-label">Animal</label>
              <select id="animal" class="form-select">
                ${this.animales.map(a => `<option value="${a.id}" ${v.idAnimal == a.id ? 'selected' : ''}>${a.nombre} (ID: ${a.id})</option>`).join('')}
              </select>
            </div>
            <div class="col-12">
              <label class="form-label">Tipo de Vacuna</label>
              <select id="tipoVacuna" class="form-select">
                <option value="">Sin especificar</option>
                ${this.tiposVacuna.map(t => `<option value="${t.id}" ${v.idTipoVacuna == t.id ? 'selected' : ''}>${t.nombre}</option>`).join('')}
              </select>
            </div>
            <div class="col-6">
              <label class="form-label">Fecha Aplicación</label>
              <input id="fechaAplicacion" type="date" class="form-control" value="${v.fechaAplicacion ? v.fechaAplicacion.split('T')[0] : ''}">
            </div>
            <div class="col-6">
              <label class="form-label">Próxima Dosis</label>
              <input id="proximaDosis" type="date" class="form-control" value="${v.proximaDosis ? v.proximaDosis.split('T')[0] : ''}">
            </div>
            <div class="col-12">
              <label class="form-label">Responsable</label>
              <select id="responsable" class="form-select">
                ${this.personas.map(p => `<option value="${p.id}" ${v.responsableId == p.id ? 'selected' : ''}>${p.nombre}</option>`).join('')}
              </select>
            </div>
            <div class="col-12">
              <label class="form-label">Estado</label>
              <select id="estado" class="form-select">
                <option value="pendiente" ${v.estado === 'pendiente' ? 'selected' : ''}>Pendiente</option>
                <option value="aplicado" ${v.estado === 'aplicado' ? 'selected' : ''}>Aplicado</option>
              </select>
            </div>
          </div>
        `,
        focusConfirm: false,
        showCancelButton: true,
        confirmButtonText: 'Actualizar',
        cancelButtonText: 'Cancelar',
        preConfirm: () => {
          const animal = document.getElementById('animal').value;
          const tipoVacuna = document.getElementById('tipoVacuna').value;
          const fechaAplicacion = document.getElementById('fechaAplicacion').value;
          const proximaDosis = document.getElementById('proximaDosis').value;
          const responsable = document.getElementById('responsable').value;
          const estado = document.getElementById('estado').value;

          if (!animal || !fechaAplicacion || !responsable) {
            Swal.showValidationMessage('Por favor complete los campos requeridos: Animal, Fecha Aplicación y Responsable');
            return false;
          }

          return {
            id_animal: parseInt(animal),
            id_tipo_vacuna: tipoVacuna ? parseInt(tipoVacuna) : null,
            fecha_aplicacion: fechaAplicacion,
            proxima_dosis: proximaDosis || null,
            responsable: parseInt(responsable),
            estado: estado
          };
        }
      });

      if (formValues) {
        try {
          await vacunacionAPI.update(id, formValues);
          await this.cargarDatos();
          Swal.fire('Éxito', 'Vacunación actualizada correctamente', 'success');
        } catch (error) {
          console.error('Error actualizando vacunación:', error);
          Swal.fire('Error', 'No se pudo actualizar la vacunación', 'error');
        }
      }
    },

    async eliminarVacunacion(id) {
      console.log('Frontend: Intentando eliminar vacunación con ID:', id);
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
          console.log('Frontend: Llamando a vacunacionAPI.delete con ID:', id);
          const response = await vacunacionAPI.delete(id);
          console.log('Frontend: Respuesta de delete:', response);
          await this.cargarDatos();
          Swal.fire('Eliminado', 'La vacunación ha sido eliminada correctamente', 'success');
        } catch (error) {
          console.error('Frontend: Error eliminando vacunación:', error);
          console.error('Frontend: Detalles del error:', error.response);
          Swal.fire('Error', 'No se pudo eliminar la vacunación', 'error');
        }
      }
    }
  }
};