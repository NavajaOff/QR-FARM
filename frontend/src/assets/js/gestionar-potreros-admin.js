import { onMounted } from 'vue';
import {
  currentIndex,
  accordionOpen,
  potreros,
  tiposPasto,
  estadosPotrero,
  personasUsuario,
  loading,
  error,
  cargarDatosIniciales,
  cargarPotreros,
  crearPotrero,
  editarPotrero,
  prevPotrero,
  nextPotrero,
  toggleAccordion,
  estadoClass,
  actualizarProximaLimpieza,
  abrirGestionPastos
} from './gestionar-potreros.js';

export default {
  name: 'GestionarPotreros',
  setup() {
    onMounted(cargarDatosIniciales);

    return {
      currentIndex,
      accordionOpen,
      potreros,
      tiposPasto,
      estadosPotrero,
      personasUsuario,
      loading,
      error,
      crearPotrero,
      editarPotrero,
      prevPotrero,
      nextPotrero,
      toggleAccordion,
      estadoClass,
      cargarPotreros,
      actualizarProximaLimpieza,
      abrirGestionPastos
    };
  }
};

