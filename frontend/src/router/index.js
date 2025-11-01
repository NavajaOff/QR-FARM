import { createRouter, createWebHistory } from 'vue-router';

const routes = [
  // Ruta raíz redirige a login
  { path: '/', redirect: '/login' },

  // Rutas públicas
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/public/Login.vue')
  },
  {
    path: '/crear_cuenta',
    name: 'CrearCuenta',
    component: () => import('../views/public/CrearCuenta.vue')
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import('../views/public/Home.vue')
  },
  {
    path: '/contacto',
    name: 'Contacto',
    component: () => import('../views/public/Contacto.vue')
  },

  // Rutas de administrador con layout anidado
  {
    path: '/admin',
    component: () => import('../layouts/AdminLayout.vue'),
    meta: { requiresAuth: true, role: 'admin' },
    children: [
      {
        path: 'dashboard',
        name: 'DashboardAdmin',
        component: () => import('../views/admin/DashboardContent.vue')
      },
      {
        path: 'gestionar-usuarios',
        name: 'GestionarUsuarios',
        component: () => import('../views/admin/GestionarUsuarios.vue')
      },
      {
        path: 'gestionar-animales',
        name: 'GestionarAnimalesAdmin',
        component: () => import('../views/admin/GestionarAnimalesAdmin.vue')
      },
      {
        path: 'gestionar-ganado',
        name: 'GestionarGanadoAdmin',
        component: () => import('../views/admin/GestionarAnimalesAdmin.vue')
      },
      {
        path: 'gestionar-ganados',
        name: 'GestionarGanadosAdmin',
        component: () => import('../views/admin/GestionarAnimalesAdmin.vue')
      },
      {
        path: 'gestionar-potreros',
        name: 'GestionarPotrerosAdmin',
        component: () => import('../views/admin/GestionarPotrerosAdmin.vue')
      },
      {
        path: 'inventario',
        name: 'InventarioAdmin',
        component: () => import('../views/admin/InventarioAdmin.vue')
      },
      {
        path: 'vacunacion',
        name: 'RegistroVacunacionAdmin',
        component: () => import('../views/admin/RegistroVacunacionAdmin.vue')
      },
      {
        path: 'perfil',
        name: 'PerfilAdmin',
        component: () => import('../views/admin/PerfilAdmin.vue')
      },
      {
        path: 'escanear-qr',
        name: 'EscanearQRAdmin',
        component: () => import('../views/admin/EscanearQRAdmin.vue')
      }
    ]
  },

  // Rutas de usuario con layout anidado
  {
    path: '/user',
    component: () => import('../layouts/UserLayout.vue'),
    meta: { requiresAuth: true, role: 'usuario' },
    children: [
      {
        path: 'dashboard',
        name: 'DashboardUsuario',
        component: () => import('../views/user/DashboardContent.vue')
      },
      {
        path: 'gestionar-animales',
        name: 'GestionarAnimalesUsuario',
        component: () => import('../views/user/GestionarAnimalesUsuario.vue')
      },
      {
        path: 'mi-ganado',
        redirect: { name: 'GestionarAnimalesUsuario' }
      },
      {
        path: 'inventario',
        name: 'InventarioUsuario',
        component: () => import('../views/user/InventarioUsuario.vue')
      },
      {
        path: 'registro-vacunacion',
        name: 'RegistroVacunacionUsuario',
        component: () => import('../views/user/RegistroVacunacionUsuario.vue')
      },
      {
        path: 'vacunacion',
        redirect: { name: 'RegistroVacunacionUsuario' }
      },
      {
        path: 'perfil',
        name: 'PerfilUsuario',
        component: () => import('../views/user/PerfilUsuario.vue')
      },
      {
        path: 'qr',
        name: 'EscanearQRUsuario',
        component: () => import('../views/user/EscanearQRUsuario.vue')
      }
    ]
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

// Guard de navegación
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token');
  const userRole = localStorage.getItem('userRole');

  console.log(`[ROUTER GUARD] Navegando de ${from.path} a ${to.path}`);
  console.log(`[ROUTER GUARD] Token: ${token ? 'presente' : 'ausente'}`);
  console.log(`[ROUTER GUARD] UserRole: ${userRole}`);
  console.log(`[ROUTER GUARD] Meta requiresAuth: ${to.meta.requiresAuth}`);
  console.log(`[ROUTER GUARD] Meta role: ${to.meta.role}`);

  // Si la ruta requiere autenticación y no hay token
  if (to.meta.requiresAuth && !token) {
    console.log('[ROUTER GUARD] Redirigiendo a /login - no hay token');
    return next('/login');
  }

  // Si la ruta requiere un rol específico y el usuario no lo tiene
  if (to.meta.role && to.meta.role !== userRole) {
    console.log(`[ROUTER GUARD] Redirigiendo a /login - rol requerido: ${to.meta.role}, rol actual: ${userRole}`);

    // Si el usuario está intentando acceder a una ruta raíz sin especificar, redirigir según su rol
    if (to.path === '/' || to.path === '/login') {
      if (userRole === 'admin' || userRole === 'administrador') {
        console.log('[ROUTER GUARD] Redirigiendo admin a /admin/dashboard');
        return next('/admin/dashboard');
      } else if (userRole === 'usuario' || userRole === 'user') {
        console.log('[ROUTER GUARD] Redirigiendo usuario a /user/dashboard');
        return next('/user/dashboard');
      }
    }

    return next('/login');
  }

  // Si el usuario está autenticado y va a login, redirigir según su rol
  if (token && (to.path === '/' || to.path === '/login')) {
    if (userRole === 'admin' || userRole === 'administrador') {
      console.log('[ROUTER GUARD] Usuario admin autenticado, redirigiendo a /admin/dashboard');
      return next('/admin/dashboard');
    } else if (userRole === 'usuario' || userRole === 'user') {
      console.log('[ROUTER GUARD] Usuario normal autenticado, redirigiendo a /user/dashboard');
      return next('/user/dashboard');
    }
  }

  console.log('[ROUTER GUARD] Navegación permitida');
  next();
});

export default router;
