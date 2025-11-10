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
                <caption class="visually-hidden">Tabla administrativa de registros de vacunación mostrando ID animal, nombre, tipo de vacuna, fechas, responsable, estado y acciones disponibles</caption>
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
import registroVacunacionAdmin from '../../assets/js/registro-vacunacion-admin.js';

export default registroVacunacionAdmin;
</script>

<style scoped>
/* Estilos específicos para RegistroVacunacionAdmin se añadirán aquí cuando sean necesarios */
</style>
