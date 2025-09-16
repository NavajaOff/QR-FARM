import { createRouter, createWebHistory } from 'vue-router';

import Menu from '../views/Menu.vue';
import Login from '../views/Login.vue';
import CrearCuenta from '../views/CrearCuenta.vue';
import Contacto from '../views/Contacto.vue';
import Inventario from '../views/Inventario.vue';
import GestionarAnimales from '../views/GestionarAnimales.vue';
import GestionarPotreros from '../views/GestionarPotreros.vue';
import EscanearQR from '../views/EscanearQR.vue';
import RegistroVacunacion from '../views/RegistroVacunacion.vue';

const routes = [
  { path: '/', name: 'Menu', component: Menu },
  { path: '/login', name: 'Login', component: Login },
  { path: '/crear_cuenta', name: 'CrearCuenta', component: CrearCuenta },
  { path: '/contacto', name: 'Contacto', component: Contacto },
  { path: '/inventario', name: 'Inventario', component: Inventario },
  { path: '/gestionar_animales', name: 'GestionarAnimales', component: GestionarAnimales },
  { path: '/gestionar_potreros', name: 'GestionarPotreros', component: GestionarPotreros },
  { path: '/escanear_qr', name: 'EscanearQR', component: EscanearQR },
  { path: '/registro_vacunacion', name: 'RegistroVacunacion', component: RegistroVacunacion },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
