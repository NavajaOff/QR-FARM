<template>
  <div class="container-fluid py-4 py-md-5">
    <div class="row justify-content-center g-4">
      <div class="col-12">
        <div class="mb-4 text-center">
          <h2 class="fw-bold text-dark">
            <i class="fas fa-map-marked-alt me-2 text-success"></i>Gestionar Potreros
          </h2>
          <p class="lead text-muted">Administra y controla tus potreros de manera eficiente</p>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-success" role="status">
            <span class="visually-hidden">Cargando...</span>
          </div>
          <p class="mt-2 text-muted">Cargando potreros...</p>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="alert alert-danger text-center">
          <i class="fas fa-exclamation-triangle me-2"></i>
          {{ error }}
          <button class="btn btn-sm btn-outline-danger ms-3" @click="cargarPotreros">
            <i class="fas fa-redo me-1"></i>Reintentar
          </button>
        </div>

        <!-- Empty State -->
        <div v-else-if="potreros.length === 0" class="text-center py-5">
          <i class="fas fa-map-marked-alt fa-4x text-muted mb-3"></i>
          <h4 class="text-muted">No hay potreros registrados</h4>
          <p class="text-muted">Aún no se han creado potreros en el sistema.</p>
          <button class="btn btn-success" @click="crearPotrero()">
            <i class="fas fa-plus me-1"></i>Crear Primer Potrero
          </button>
        </div>

        <!-- Card Potrero -->
        <div v-else class="d-flex justify-content-center align-items-start gap-2">
          <button class="btn btn-outline-secondary" @click="prevPotrero" :disabled="potreros.length <= 1"><i class="fas fa-chevron-left"></i></button>

          <div class="card border-0 shadow-lg" style="min-width: 450px; max-width: 700px;">
            <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
              <h5 class="mb-0"><i class="fas fa-leaf me-2"></i>{{ potreros[currentIndex].nombre }}</h5>
              <button class="btn btn-light btn-sm" @click="toggleAccordion">
                <i :class="accordionOpen ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
              </button>
            </div>
            <div class="card-body p-4 p-sm-5" v-show="accordionOpen">
              <div class="row g-3 mb-3">
                <div class="col-6"><strong>Estado:</strong> <span class="badge" :class="estadoClass(potreros[currentIndex].estado)">{{ potreros[currentIndex].estado }}</span></div>
                <div class="col-6"><strong>Capacidad:</strong> {{ potreros[currentIndex].capacidad || 'No definida' }} Animales</div>
              </div>
              <div class="row g-3 mb-3">
                <div class="col-6"><strong>Ocupación:</strong> {{ potreros[currentIndex].ocupacion || 0 }} Animales</div>
                <div class="col-6"><strong>Hectáreas:</strong> {{ potreros[currentIndex].hectareas || 'No definida' }} ha</div>
              </div>
              <div class="row g-3 mb-3">
                <div class="col-6"><strong>Fecha de último uso:</strong> {{ potreros[currentIndex].fechaUso || 'No registrada' }}</div>
                <div class="col-6"><strong>Responsable:</strong> {{ potreros[currentIndex].responsable }}</div>
              </div>
              <div class="row g-3 mb-3">
                <div class="col-12"><strong>Próxima limpieza:</strong> {{ potreros[currentIndex].proximaLimpieza || 'No programada' }}</div>
              </div>
              <div class="row g-3 mb-3">
                <div class="col-6"><strong>Área:</strong> {{ potreros[currentIndex].area || 'No definida' }} m²</div>
                <div class="col-6"><strong>Última limpieza:</strong> {{ potreros[currentIndex].ultimaLimpieza || 'No registrada' }}</div>
              </div>
              <div class="row g-3 mb-3" v-if="potreros[currentIndex].descripcion">
                <div class="col-12"><strong>Descripción:</strong> {{ potreros[currentIndex].descripcion }}</div>
              </div>
              <div class="d-flex gap-2 justify-content-center">
                <button class="btn btn-primary" @click="editarPotrero(potreros[currentIndex].id)"><i class="fas fa-edit me-1"></i>Editar</button>
                <button class="btn btn-success" @click="crearPotrero()"><i class="fas fa-plus me-1"></i>Crear Potrero</button>
              </div>
            </div>
          </div>

          <button class="btn btn-outline-secondary" @click="nextPotrero" :disabled="potreros.length <= 1"><i class="fas fa-chevron-right"></i></button>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
import Swal from 'sweetalert2';

export default {
  name: "GestionarPotreros",
  data() {
    return {
      currentIndex: 0,
      accordionOpen: true,
      potreros: [],
      tiposPasto: [],
      estadosPotrero: [],
      personasUsuario: [],
      loading: true,
      error: null
    };
  },
  async mounted() {
    await this.cargarDatosIniciales();
  },
  methods: {
    async cargarDatosIniciales() {
      try {
        this.loading = true;
        this.error = null;

        // Cargar tipos de pasto, estados y personas primero
        await Promise.all([
          this.cargarTiposPasto(),
          this.cargarEstadosPotrero(),
          this.cargarPersonasUsuario()
        ]);

        // Luego cargar potreros
        await this.cargarPotreros();
      } catch (error) {
        this.error = error.message;
        console.error('Error cargando datos iniciales:', error);
        this.loading = false;
      }
    },

    async cargarTiposPasto() {
      try {
        const response = await fetch('http://localhost:5000/api/potreros/tipos-pasto');
        if (response.ok) {
          const data = await response.json();
          if (data.success && data.data.length > 0) {
            this.tiposPasto = data.data;
          } else {
            // Fallback a hardcodeados si no hay datos
            this.tiposPasto = [
              { id: 1, nombre: 'Kikuyo' },
              { id: 2, nombre: 'Braquiaria' },
              { id: 3, nombre: 'Festuca' },
              { id: 4, nombre: 'Ray Grass' },
              { id: 5, nombre: 'Pastura Mixta' }
            ];
          }
        } else {
          // Fallback a hardcodeados si falla la API
          this.tiposPasto = [
            { id: 1, nombre: 'Kikuyo' },
            { id: 2, nombre: 'Braquiaria' },
            { id: 3, nombre: 'Festuca' },
            { id: 4, nombre: 'Ray Grass' },
            { id: 5, nombre: 'Pastura Mixta' }
          ];
        }
      } catch (error) {
        console.error('Error cargando tipos de pasto:', error);
        // Fallback a hardcodeados si hay error
        this.tiposPasto = [
          { id: 1, nombre: 'Kikuyo' },
          { id: 2, nombre: 'Braquiaria' },
          { id: 3, nombre: 'Festuca' },
          { id: 4, nombre: 'Ray Grass' },
          { id: 5, nombre: 'Pastura Mixta' }
        ];
      }
    },

    async cargarEstadosPotrero() {
      try {
        const response = await fetch('http://localhost:5000/api/potreros/estados');
        if (response.ok) {
          const data = await response.json();
          if (data.success) {
            this.estadosPotrero = data.data;
          }
        }
      } catch (error) {
        console.error('Error cargando estados de potrero:', error);
        // Fallback a valores hardcodeados
        this.estadosPotrero = [
          { id: 1, nombre: 'disponible' },
          { id: 2, nombre: 'ocupado' },
          { id: 3, nombre: 'limpieza' }
        ];
      }
    },

    async cargarPersonasUsuario() {
      try {
        const response = await fetch('http://localhost:5000/api/potreros/personas-usuario');
        if (response.ok) {
          const data = await response.json();
          if (data.success) {
            this.personasUsuario = data.data;
          }
        }
      } catch (error) {
        console.error('Error cargando personas usuario:', error);
        this.personasUsuario = [];
      }
    },

    async cargarPotreros() {
      try {
        const response = await fetch('http://localhost:5000/api/potreros/');
        if (!response.ok) {
          throw new Error(`Error HTTP: ${response.status}`);
        }
        const data = await response.json();
        if (data.status === "success") {
          this.potreros = data.data.map(potrero => ({
            id: potrero.id,
            nombre: potrero.nombre,
            estado: potrero.estado,
            capacidad: potrero.capacidad,
            ocupacion: potrero.ocupacion,
            hectareas: potrero.hectareas,
            area: potrero.area,
            fechaUso: potrero.fecha_ultimo_uso ? this.formatDate(potrero.fecha_ultimo_uso) : 'No registrada',
            ultimaLimpieza: potrero.ultima_limpieza ? this.formatDate(potrero.ultima_limpieza) : 'No registrada',
            proximaLimpieza: potrero.proxima_limpieza ? this.formatDate(potrero.proxima_limpieza) : 'No programada',
            responsable: potrero.responsable || 'No asignado',
            descripcion: potrero.descripcion || ''
          }));
        } else {
          throw new Error(data.message || 'Error desconocido');
        }
      } catch (error) {
        this.error = error.message;
        console.error('Error cargando potreros:', error);
      } finally {
        this.loading = false;
      }
    },

    mapEstado(estado) {
      const estados = {
        'disponible': 'Disponible',
        'en_uso': 'En uso',
        'mantenimiento': 'Mantenimiento',
        'inactivo': 'Inactivo'
      };
      return estados[estado] || estado;
    },

    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString('es-ES', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      });
    },

    estadoClass(estado) {
      if (estado === 'Disponible') return 'bg-success';
      if (estado === 'En uso') return 'bg-warning';
      if (estado === 'Mantenimiento') return 'bg-danger';
      return 'bg-secondary';
    },

    crearPotrero() {
      Swal.fire({
        title: '<i class="fas fa-plus"></i> Crear Nuevo Potrero',
        html: `
          <form class="text-start">
            <div class="mb-3">
              <label class="form-label">Estado:</label>
              <select id="estado" class="form-control">
                <option v-for="estado in estadosPotrero" :key="estado.id" :value="estado.nombre">{{ estado.nombre }}</option>
              </select>
            </div>
            <div class="mb-3"><label class="form-label">Capacidad:</label><input type="number" id="capacidad" class="form-control" placeholder="Ej: 25" min="0"></div>
            <div class="mb-3"><label class="form-label">Hectáreas:</label><input type="number" id="hectareas" class="form-control" placeholder="Ej: 2.5" step="0.01" min="0"></div>
            <div class="mb-3"><label class="form-label">Ocupación:</label><input type="number" id="ocupacion" class="form-control" placeholder="Ej: 0" min="0" value="0"></div>
            <div class="mb-3">
              <label class="form-label">Tipo de pasto:</label>
              <select id="id_tipo_pasto" class="form-control">
                <option value="">Seleccionar tipo de pasto</option>
                <option v-for="tipo in tiposPasto" :key="tipo.id" :value="tipo.id">{{ tipo.nombre }}</option>
              </select>
            </div>
            <div class="mb-3"><label class="form-label">Fecha de último uso:</label><input type="date" id="fecha_ultimo_uso" class="form-control"></div>
            <div class="mb-3">
              <label class="form-label">Responsable:</label>
              <select id="responsable_persona_id" class="form-control">
                <option value="">Seleccionar responsable</option>
                <option v-for="persona in personasUsuario" :key="persona.id" :value="persona.id">{{ persona.nombre_completo }}</option>
              </select>
            </div>
            <div class="mb-3"><label class="form-label">Próxima limpieza:</label><input type="date" id="proxima_limpieza" class="form-control"></div>
            <div class="mb-3"><label class="form-label">Área (m²):</label><input type="number" id="area" class="form-control" placeholder="Ej: 2500" step="0.01" min="0"></div>
            <div class="mb-3"><label class="form-label">Última limpieza:</label><input type="date" id="ultima_limpieza" class="form-control"></div>
            <div class="mb-3"><label class="form-label">Descripción:</label><textarea id="descripcion" class="form-control" rows="2" placeholder="Descripción opcional del potrero"></textarea></div>
          </form>
        `,
        showCancelButton: true,
        confirmButtonText: 'Agregar',
        confirmButtonColor: '#00d563',
        preConfirm: () => {
          const estado = document.getElementById('estado').value;
          const capacidad = document.getElementById('capacidad').value;
          const hectareas = document.getElementById('hectareas').value;
          const ocupacion = document.getElementById('ocupacion').value;
          const id_tipo_pasto = document.getElementById('id_tipo_pasto').value;
          const fecha_ultimo_uso = document.getElementById('fecha_ultimo_uso').value;
          const responsable_persona_id = document.getElementById('responsable_persona_id').value;
          const proxima_limpieza = document.getElementById('proxima_limpieza').value;
          const area = document.getElementById('area').value;
          const ultima_limpieza = document.getElementById('ultima_limpieza').value;
          const descripcion = document.getElementById('descripcion').value;

          return {
            estado,
            capacidad: capacidad ? parseInt(capacidad) : null,
            hectareas: hectareas ? parseFloat(hectareas) : null,
            ocupacion: ocupacion ? parseInt(ocupacion) : 0,
            id_tipo_pasto: id_tipo_pasto ? parseInt(id_tipo_pasto) : null,
            fecha_ultimo_uso,
            responsable_persona_id: responsable_persona_id ? parseInt(responsable_persona_id) : null,
            proxima_limpieza,
            area: area ? parseFloat(area) : null,
            ultima_limpieza,
            descripcion
          };
        }
      }).then(async (result) => {
        if (result.isConfirmed) {
          try {
            const response = await fetch('http://localhost:5000/api/potreros/', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify(result.value)
            });

            if (response.ok) {
              const data = await response.json();
              if (data.success) {
                Swal.fire('¡Éxito!', 'Potrero creado correctamente', 'success');
                await this.cargarPotreros(); // Recargar la lista
              } else {
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
    },

    editarPotrero(id) {
      const potrero = this.potreros.find(p => p.id === id);
      if (!potrero) return;

      Swal.fire({
        title: `<i class="fas fa-edit"></i> Editar Potrero: ${potrero.nombre}`,
        html: `
          <form class="text-start">
            <div class="mb-3">
              <label class="form-label">Estado:</label>
              <select id="edit_estado" class="form-control">
                <option v-for="estado in estadosPotrero" :key="estado.id" :value="estado.nombre" :selected="estado.nombre === potrero.estado">{{ estado.nombre }}</option>
              </select>
            </div>
            <div class="mb-3"><label class="form-label">Capacidad:</label><input type="number" id="edit_capacidad" class="form-control" value="${potrero.capacidad || ''}" min="0"></div>
            <div class="mb-3"><label class="form-label">Hectáreas:</label><input type="number" id="edit_hectareas" class="form-control" value="${potrero.hectareas || ''}" step="0.01" min="0"></div>
            <div class="mb-3"><label class="form-label">Ocupación:</label><input type="number" id="edit_ocupacion" class="form-control" value="${potrero.ocupacion || 0}" min="0"></div>
            <div class="mb-3">
              <label class="form-label">Tipo de pasto:</label>
              <select id="edit_id_tipo_pasto" class="form-control">
                <option value="">Seleccionar tipo de pasto</option>
                <option v-for="tipo in tiposPasto" :key="tipo.id" :value="tipo.id" :selected="tipo.nombre === potrero.pasto">{{ tipo.nombre }}</option>
              </select>
            </div>
            <div class="mb-3"><label class="form-label">Fecha de último uso:</label><input type="date" id="edit_fecha_ultimo_uso" class="form-control" value="${potrero.fechaUso ? potrero.fechaUso.split('/').reverse().join('-') : ''}"></div>
            <div class="mb-3">
              <label class="form-label">Responsable:</label>
              <select id="edit_responsable_persona_id" class="form-control">
                <option value="">Seleccionar responsable</option>
                <option v-for="persona in personasUsuario" :key="persona.id" :value="persona.id" :selected="persona.nombre_completo === potrero.responsable">{{ persona.nombre_completo }}</option>
              </select>
            </div>
            <div class="mb-3"><label class="form-label">Próxima limpieza:</label><input type="date" id="edit_proxima_limpieza" class="form-control"></div>
            <div class="mb-3"><label class="form-label">Área (m²):</label><input type="number" id="edit_area" class="form-control" value="${potrero.area || ''}" step="0.01" min="0"></div>
            <div class="mb-3"><label class="form-label">Última limpieza:</label><input type="date" id="edit_ultima_limpieza" class="form-control" value="${potrero.ultimaLimpieza ? potrero.ultimaLimpieza.split('/').reverse().join('-') : ''}"></div>
            <div class="mb-3"><label class="form-label">Descripción:</label><textarea id="edit_descripcion" class="form-control" rows="2">${potrero.descripcion || ''}</textarea></div>
          </form>
        `,
        showCancelButton: true,
        confirmButtonText: 'Actualizar',
        confirmButtonColor: '#00d563',
        preConfirm: () => {
          const estado = document.getElementById('edit_estado').value;
          const capacidad = document.getElementById('edit_capacidad').value;
          const hectareas = document.getElementById('edit_hectareas').value;
          const ocupacion = document.getElementById('edit_ocupacion').value;
          const id_tipo_pasto = document.getElementById('edit_id_tipo_pasto').value;
          const fecha_ultimo_uso = document.getElementById('edit_fecha_ultimo_uso').value;
          const responsable_persona_id = document.getElementById('edit_responsable_persona_id').value;
          const proxima_limpieza = document.getElementById('edit_proxima_limpieza').value;
          const area = document.getElementById('edit_area').value;
          const ultima_limpieza = document.getElementById('edit_ultima_limpieza').value;
          const descripcion = document.getElementById('edit_descripcion').value;

          return {
            estado,
            capacidad: capacidad ? parseInt(capacidad) : null,
            hectareas: hectareas ? parseFloat(hectareas) : null,
            ocupacion: ocupacion ? parseInt(ocupacion) : 0,
            id_tipo_pasto: id_tipo_pasto ? parseInt(id_tipo_pasto) : null,
            fecha_ultimo_uso,
            responsable_persona_id: responsable_persona_id ? parseInt(responsable_persona_id) : null,
            proxima_limpieza,
            area: area ? parseFloat(area) : null,
            ultima_limpieza,
            descripcion
          };
        }
      }).then(async (result) => {
        if (result.isConfirmed) {
          try {
            const response = await fetch(`http://localhost:5000/api/potreros/${id}`, {
              method: 'PUT',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify(result.value)
            });

            if (response.ok) {
              const data = await response.json();
              if (data.success) {
                Swal.fire('¡Éxito!', 'Potrero actualizado correctamente', 'success');
                await this.cargarPotreros(); // Recargar la lista
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
    },

    prevPotrero() {
      if (this.potreros.length > 1) {
        this.currentIndex = (this.currentIndex - 1 + this.potreros.length) % this.potreros.length;
        this.accordionOpen = true;
      }
    },

    nextPotrero() {
      if (this.potreros.length > 1) {
        this.currentIndex = (this.currentIndex + 1) % this.potreros.length;
        this.accordionOpen = true;
      }
    },

    toggleAccordion() {
      this.accordionOpen = !this.accordionOpen;
    },

    async actualizarProximaLimpieza(id, fecha) {
      try {
        const response = await fetch(`http://localhost:5000/api/potreros/${id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            proxima_limpieza: fecha
          })
        });

        if (response.ok) {
          const data = await response.json();
          if (data.success) {
            console.log('Próxima limpieza actualizada correctamente');
          } else {
            console.error('Error actualizando próxima limpieza:', data.message);
          }
        } else {
          console.error('Error HTTP actualizando próxima limpieza:', response.status);
        }
      } catch (error) {
        console.error('Error actualizando próxima limpieza:', error);
      }
    }
  }
};
</script>

<style scoped>
.sidebar {
  min-width: 250px;
  max-width: 250px;
  position: fixed;
  top: 80px;
  left: 0;
  height: calc(100vh - 80px);
  background-color: #6c757d;
  z-index: 1020;
  padding: 1rem;
  overflow-y: auto;
}
@media (max-width: 767px) {
  .sidebar {
    display: none !important;
  }
}
.main-content {
  margin-left: 250px;
  margin-top: 0;
}
@media (max-width: 767px) {
  .main-content {
    margin-left: 0 !important;
  }
}
</style>
