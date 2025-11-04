<template>
  <div class="container-fluid py-4 py-md-5">
    <div class="row justify-content-center g-4">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h2 class="fw-bold text-dark mb-0">
            <i class="fas fa-syringe me-2 text-success"></i>Registro de Vacunación
          </h2>
          <div class="d-flex gap-2">
            <button class="btn btn-success" @click="registrarVacunacion">
              <i class="fas fa-plus me-2"></i>Nueva Vacunación
            </button>
            <button class="btn btn-primary" @click="generarReporte">
              <i class="fas fa-file-pdf me-2"></i>Generar Reporte
            </button>
          </div>
        </div>

        <!-- Filtros -->
        <div class="card border-0 shadow-lg mb-4">
          <div class="card-body p-3 p-sm-4">
            <div class="row g-3">
              <div class="col-md-3">
                <label class="form-label">Buscar animal:</label>
                <input type="text" class="form-control" v-model="filtros.animal" placeholder="ID o Nombre">
              </div>
              <div class="col-md-3">
                <label class="form-label">Tipo de vacuna:</label>
                <select class="form-select" v-model="filtros.vacuna">
                  <option value="">Todas</option>
                  <option v-for="tipo in tiposVacuna" :key="tipo.id" :value="tipo.nombre">{{ tipo.nombre }}</option>
                </select>
              </div>
              <div class="col-md-3">
                <label class="form-label">Fecha desde:</label>
                <input type="date" class="form-control" v-model="filtros.fechaDesde">
              </div>
              <div class="col-md-3">
                <label class="form-label">Fecha hasta:</label>
                <input type="date" class="form-control" v-model="filtros.fechaHasta">
              </div>
            </div>
          </div>
        </div>

        <!-- Tabla de Registros -->
        <div class="card border-0 shadow-lg">
          <div class="card-body p-0">
            <div class="table-responsive">
              <table class="table table-hover mb-0">
                <thead class="bg-light">
                  <tr>
                    <th>ID Animal</th>
                    <th>Nombre/Código</th>
                    <th>Tipo de Vacuna</th>
                    <th>Fecha Aplicación</th>
                    <th>Próxima Dosis</th>
                    <th>Responsable</th>
                    <th>Estado</th>
                    <th>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="v in vacunaciones" :key="v.id">
                    <td>{{ v.idAnimal }}</td>
                    <td>{{ v.nombre }}</td>
                    <td>{{ v.tipoVacuna }}</td>
                    <td>{{ formatDate(v.fechaAplicacion) }}</td>
                    <td>{{ formatDate(v.proximaDosis) }}</td>
                    <td>{{ v.responsable }}</td>
                    <td><span :class="['badge', estadoClass(v.estado)]">{{ v.estado }}</span></td>
                    <td>
                      <button class="btn btn-sm btn-outline-primary me-1" @click="verVacunacion(v.id)"><i class="fas fa-eye"></i></button>
                      <button class="btn btn-sm btn-outline-warning me-1" @click="editarVacunacion(v.id)"><i class="fas fa-edit"></i></button>
                      <button class="btn btn-sm btn-outline-danger" @click="eliminarVacunacion(v.id)"><i class="fas fa-trash"></i></button>
                    </td>
                  </tr>
                  <tr v-if="loading">
                    <td colspan="9" class="text-center">
                      <div class="spinner-border spinner-border-sm" role="status">
                        <span class="visually-hidden">Cargando...</span>
                      </div>
                      Cargando vacunaciones...
                    </td>
                  </tr>
                  <tr v-else-if="vacunaciones.length === 0">
                    <td colspan="9" class="text-center">No hay registros de vacunación.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
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
      if (estado === 'aplicada') return 'bg-success';
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
                ${this.animales.map(a => `<option value="${a.id}">${a.nombre} (ID: ${a.id})</option>`).join('')}
              </select>
            </div>
            <div class="col-12">
              <label class="form-label">Tipo de Vacuna</label>
              <select id="tipoVacuna" class="form-select">
                <option value="">Seleccionar tipo...</option>
                ${this.tiposVacuna.map(t => `<option value="${t.id}">${t.nombre}</option>`).join('')}
              </select>
            </div>
            <div class="col-6">
              <label class="form-label">Fecha Aplicación</label>
              <input id="fechaAplicacion" type="date" class="form-control">
            </div>
            <div class="col-6">
              <label class="form-label">Próxima Dosis</label>
              <input id="proximaDosis" type="date" class="form-control">
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
                <option value="aplicada">Aplicada</option>
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
          const proximaDosis = document.getElementById('proximaDosis').value;
          const responsable = document.getElementById('responsable').value;
          const estado = document.getElementById('estado').value;

          if (!animal || !tipoVacuna || !responsable) {
            Swal.showValidationMessage('Por favor complete todos los campos requeridos');
            return false;
          }

          return {
            id_animal: parseInt(animal),
            id_tipo_vacuna: parseInt(tipoVacuna),
            fecha_aplicacion: fechaAplicacion || null,
            proxima_dosis: proximaDosis || null,
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
              <p><strong>Estado:</strong> <span class="badge ${this.estadoClass(v.estado)}">${v.estado}</span></p>
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
                <option value="aplicada" ${v.estado === 'aplicada' ? 'selected' : ''}>Aplicada</option>
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

          if (!animal || !responsable) {
            Swal.showValidationMessage('Por favor complete los campos requeridos: Animal y Responsable');
            return false;
          }

          return {
            id_animal: parseInt(animal),
            id_tipo_vacuna: tipoVacuna ? parseInt(tipoVacuna) : null,
            fecha_aplicacion: fechaAplicacion || null,
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
</script>

<style scoped>
</style>
