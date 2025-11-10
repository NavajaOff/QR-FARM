import { registroVacunacionBase } from './registro-vacunacion-base.js';

const { methods, ...baseOptions } = registroVacunacionBase;

export default {
  ...baseOptions,
  name: 'RegistroVacunacionUsuario',
  registroVacunacionConfig: {
    registroValidacionMsg: 'Por favor complete todos los campos requeridos',
    eliminarLogPrefix: 'Frontend Usuario'
  },
  methods: {
    ...methods
  }
};