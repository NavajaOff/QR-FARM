<template>
  <div class="container-fluid py-4">
    <div class="row">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h2 class="mb-0">
            <i class="fas fa-boxes me-2 text-success"></i>Mi Inventario
          </h2>
        </div>

        <!-- Resumen -->
        <div class="card border-0 shadow-lg mb-4">
          <div class="card-body p-3 p-sm-4 p-lg-5">
            <div class="row g-4 align-items-center">
              <div class="col-12 col-lg-8">
                <div style="max-width: 500px; margin: 0 auto;">
                  <canvas id="inventarioPie"></canvas>
                </div>
              </div>
              <div class="col-12 col-lg-4">
                <div class="d-flex align-items-center mb-3">
                  <i class="fas fa-cow fa-2x text-success me-2"></i>
                  <span class="fw-bold">Mis Animales: {{ totalAnimales }}</span>
                </div>
                <div class="d-flex align-items-center mb-3">
                  <i class="fas fa-check-circle fa-2x text-success me-2"></i>
                  <span class="fw-bold">Saludables: {{ countSaludable }}</span>
                </div>
                <div class="d-flex align-items-center mb-3">
                  <i class="fas fa-exclamation-triangle fa-2x text-warning me-2"></i>
                  <span class="fw-bold">En Tratamiento: {{ countTratamiento }}</span>
                </div>
                <div class="d-flex align-items-center mb-3">
                  <i class="fas fa-baby fa-2x text-info me-2"></i>
                  <span class="fw-bold">Recién Nacidos: {{ countRecienNacidos }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Tabla -->
        <div class="card border-0 shadow-lg">
          <div class="card-header bg-light p-3">
            <div class="row align-items-center">
              <div class="col">
                <h5 class="mb-0">Lista de Mis Animales</h5>
              </div>
            </div>
          </div>
          <div class="card-body p-3 p-sm-4">
            <div class="table-responsive">
              <table class="table table-hover">
                <caption class="visually-hidden">Lista de animales del usuario, mostrando ID, nombre/código, raza, edad, estado, ubicación y acciones disponibles</caption>
                <thead class="table-light">
                  <tr>
                    <th>ID</th>
                    <th>Nombre/Código</th>
                    <th>Raza</th>
                    <th>Edad</th>
                    <th>Estado</th>
                    <th>Ubicación</th>
                    <th>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="a in animales" :key="a.id">
                    <td>{{ a.id }}</td>
                    <td>{{ a.nombre }}</td>
                    <td>{{ a.raza }}</td>
                    <td>{{ a.edad }} años</td>
                    <td><span :class="['badge', estadoClass(a.estado)]">{{ a.estado }}</span></td>
                    <td>{{ a.potrero }}</td>
                    <td>
                      <button class="btn btn-sm btn-outline-success me-1" @click="verPerfilAnimal(a.id)">
                        <i class="fas fa-eye"></i>
                      </button>
                      <button class="btn btn-sm btn-outline-warning" @click="editarAnimal(a.id)">
                        <i class="fas fa-edit"></i>
                      </button>
                    </td>
                  </tr>
                  <tr v-if="animales.length === 0">
                    <td colspan="7" class="text-center">No hay animales registrados.</td>
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
import inventarioUsuario from '../../assets/js/inventario-usuario.js';

export default inventarioUsuario;
</script>

<style scoped>
@import '../../assets/css/inventario-usuario.css';
</style>