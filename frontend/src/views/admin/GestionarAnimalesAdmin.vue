<template>
  <div>
    <div class="row">
      <div class="col-12">
        <!-- Selector de Tenant para Super Admin -->
        <TenantSelector v-if="isSuperAdmin" @tenant-changed="onTenantChanged" />

        <div class="d-flex justify-content-between align-items-center mb-4">
          <h2 class="mb-0">Gestión de Ganado</h2>
          <div class="d-flex gap-3 align-items-center">
            <div class="form-check">
              <input class="form-check-input" type="checkbox" v-model="mostrarBajas" @change="cargarGanado" id="mostrarBajas">
              <label class="form-check-label" for="mostrarBajas">
                Mostrar animales dados de baja
              </label>
            </div>
            <button class="btn btn-success" @click="addAnimal">
              <i class="fas fa-plus me-2"></i>Agregar Animal
            </button>
          </div>
        </div>

        <!-- Loader mientras carga -->
        <div v-if="isLoading" class="text-center py-5">
          <div class="spinner-border text-primary" aria-live="polite" aria-label="Cargando">
            <span class="visually-hidden">Cargando...</span>
          </div>
          <p class="mt-2 text-muted">Cargando ganado...</p>
        </div>

        <!-- Tabla de ganado -->
        <div v-else class="card">
          <div class="card-body">
            <div class="table-responsive">
              <table class="table table-striped">
                <caption class="visually-hidden">Tabla de gestión de ganado mostrando ID, nombre, raza, edad, peso, potrero, estado y acciones disponibles</caption>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Nombre</th>
                    <th>Raza</th>
                    <th>Edad</th>
                    <th>Peso (kg)</th>
                    <th>Potrero</th>
                    <th>Estado</th>
                    <th>Estado Baja</th>
                    <th>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="animal in ganado" :key="animal.id">
                    <td>{{ animal.id }}</td>
                    <td>{{ animal.nombre }}</td>
                    <td>{{ animal.raza }}</td>
                    <td>{{ animal.edad }} años</td>
                    <td>{{ animal.peso }}</td>
                    <td>{{ animal.potreroActual }}</td>
                    <td>
                      <span class="badge" :class="animal.estado === 'saludable' ? 'bg-success' : animal.estado === 'revision' ? 'bg-warning' : animal.estado === 'enfermo' ? 'bg-danger' : 'bg-secondary'">
                        {{ animal.estado }}
                      </span>
                    </td>
                    <td>
                      <span v-if="animal.es_dado_de_baja" class="badge bg-danger">
                        Dado de baja ({{ animal.estado }})
                      </span>
                      <span v-else class="badge bg-success">Activo</span>
                    </td>
                    <td>
                      <button class="btn btn-sm btn-outline-info me-2" @click="viewQR(animal)" title="Ver QR">
                        <i class="fas fa-qrcode"></i>
                      </button>
                      <button v-if="!animal.es_dado_de_baja" class="btn btn-sm btn-outline-primary me-2" @click="editAnimal(animal)">
                        <i class="fas fa-edit"></i>
                      </button>
                      <button v-if="!animal.es_dado_de_baja" class="btn btn-sm btn-outline-danger me-2" @click="darBajaAnimal(animal)">
                        <i class="fas fa-ban"></i>
                      </button>
                      <button v-if="animal.es_dado_de_baja" class="btn btn-sm btn-outline-success" @click="reactivarAnimal(animal)" title="Reactivar animal">
                        <i class="fas fa-undo"></i>
                      </button>
                    </td>
                  </tr>
                  <tr v-if="ganado.length === 0 && !isLoading">
                    <td colspan="9" class="text-center py-4">
                      <div class="text-muted">
                        <i class="fas fa-info-circle fa-2x mb-3"></i>
                        <h5>No hay animales registrados</h5>
                        <p class="mb-0">Aún no se han registrado animales en el sistema. Haz clic en "Agregar Animal" para comenzar.</p>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal para ver QR -->
    <div class="modal fade" id="qrModal" tabindex="-1" aria-labelledby="qrModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="qrModalLabel">Código QR - {{ selectedAnimal?.nombre }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body text-center">
            <div v-if="qrImageUrl" class="qr-container">
              <img :src="qrImageUrl" alt="Código QR" class="img-fluid qr-image" />
            </div>
            <div v-else class="text-muted">
              <i class="fas fa-spinner fa-spin fa-2x"></i>
              <p class="mt-2">Cargando código QR...</p>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import TenantSelector from '../../components/TenantSelector.vue';
import authService from '../../services/authService.js';
import {
  cargarDatosIniciales,
  animales,
  estadosGanado,
  personasUsuario,
  editarAnimal,
  agregarNuevoAnimal,
  verPerfilAnimal,
  darBajaAnimal,
  reactivarAnimal,
  cargarAnimales,
  setUpdateCallback,
  cancelPendingRequests,
  resetEstado
} from '../../assets/js/gestionar_animales.js';

export default {
  name: 'GestionarAnimalesAdmin',
  components: {
    TenantSelector
  },
  data() {
    return {
      ganado: [],
      showAddAnimalModal: false,
      showEditAnimalModal: false,
      selectedAnimal: null,
      qrImageUrl: null,
      editingAnimal: null,
      isLoading: true,
      mostrarBajas: false
    };
  },
  mounted() {
    this.cargarGanado();
    // Configurar callback para actualizar la lista desde el JS
    setUpdateCallback(this.actualizarLista);
  },
  beforeUnmount() {
    // Cancelar peticiones pendientes cuando el componente se desmonte
    cancelPendingRequests();
  },
  beforeRouteLeave(to, from, next) {
    // Cancelar peticiones y resetear estado antes de cambiar de ruta
    console.log('Saliendo de vista animales, cancelando peticiones y reseteando estado...');
    cancelPendingRequests();
    resetEstado();
    next();
  },
  computed: {
    isSuperAdmin() {
      return authService.getRole() === 'super_admin';
    }
  },
  methods: {
    async cargarGanado() {
      try {
        this.isLoading = true;
        // Cargar datos iniciales si no están cargados
        if (estadosGanado.value.length === 0 || personasUsuario.value.length === 0) {
          await cargarDatosIniciales();
        }
        // Cargar animales con o sin bajas según el filtro
        await cargarAnimales(this.mostrarBajas);
        // Copiar los datos a la variable local para compatibilidad
        this.ganado = [...animales.value];
      } catch (error) {
        console.error('Error cargando ganado:', error);
        // Mostrar mensaje de error al usuario
        this.$nextTick(() => {
          // Pequeño delay para asegurar que el DOM esté listo
          setTimeout(() => {
            if (this.ganado.length === 0) {
              console.warn('No se pudieron cargar los datos del ganado');
            }
          }, 100);
        });
      } finally {
        this.isLoading = false;
      }
    },

    // Método para actualizar la lista después de cambios
    actualizarLista() {
      this.ganado = [...animales.value];
    },

    viewQR(animal) {
      // Usar la función del archivo JS existente para ver perfil con QR
      verPerfilAnimal(animal.id);
    },

    editAnimal(animal) {
      // Usar la función del archivo JS existente
      editarAnimal(animal.id);
    },

    async darBajaAnimal(animal) {
      const resultado = await darBajaAnimal(animal.id, this.mostrarBajas);
      if (resultado && resultado.success) {
        this.ganado = [...animales.value];
      }
    },

    async reactivarAnimal(animal) {
      const resultado = await reactivarAnimal(animal.id, this.mostrarBajas);
      if (resultado && resultado.success) {
        this.ganado = [...animales.value];
      }
    },

    addAnimal() {
      // Usar la función del archivo JS existente
      agregarNuevoAnimal();
    },
    onTenantChanged() {
      // Recargar animales cuando cambia el tenant
      this.cargarGanado();
    }
  }
};
</script>

<style scoped>
@import '../../assets/css/gestionar-animales-admin.css';
</style>
