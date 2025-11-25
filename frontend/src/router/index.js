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
        path: 'reportes',
        name: 'ReportesAdmin',
        component: () => import('../views/admin/ReportesAdmin.vue')
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
        path: 'scan-qr',
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
        path: '',
        redirect: { name: 'InicioUsuario' }
      },
      {
        path: 'inicio',
        name: 'InicioUsuario',
        component: () => import('../views/user/DashboardContent.vue')
      },
      {
        path: 'dashboard',
        redirect: { name: 'InicioUsuario' }
      },
      {
        path: 'ganado',
        name: 'GanadoUsuario',
        component: () => import('../views/user/GestionarAnimalesUsuario.vue')
      },
      {
        path: 'gestionar-animales',
        redirect: { name: 'GanadoUsuario' }
      },
      {
        path: 'potreros',
        name: 'PotrerosUsuario',
        component: () => import('../views/user/GestionarPotrerosUsuario.vue')
      },
      {
        path: 'reportes',
        name: 'ReportesUsuario',
        component: () => import('../views/user/ReportesUsuario.vue')
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
        path: 'scan-qr',
        name: 'EscanearQRUsuario',
        component: () => import('../views/user/EscanearQRUsuario.vue')
      },
      {
        path: 'qr',
        redirect: { name: 'EscanearQRUsuario' }
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

  const isAdmin = userRole === 'admin' || userRole === 'administrador';
  const isUser = userRole === 'usuario' || userRole === 'user';

  function redirectByRole() {
    if (isAdmin) return '/admin/dashboard';
    if (isUser) return '/user/dashboard';
    return '/login';
  }

  function lacksAuth() {
    return to.meta.requiresAuth && !token;
  }

  function invalidRole() {
    return to.meta.role && to.meta.role !== userRole;
  }

  function isRootOrLogin(path) {
    return path === '/' || path === '/login';
  }

  console.log(`[ROUTER GUARD] Navegando de ${from.path} a ${to.path}`);
  console.log(`[ROUTER GUARD] Token: ${token ? 'presente' : 'ausente'}`);
  console.log(`[ROUTER GUARD] UserRole: ${userRole}`);

  // 1️⃣ Si requiere auth y NO hay token → LOGIN
  if (lacksAuth()) {
    return next('/login');
  }

  // 2️⃣ Si requiere rol y no coincide → LOGIN o dashboard según caso
  if (invalidRole()) {
    if (isRootOrLogin(to.path)) {
      return next(redirectByRole());
    }
    return next('/login');
  }

  // 3️⃣ Si ya está autenticado y va a login → mandarlo a su dashboard
  if (token && isRootOrLogin(to.path)) {
    return next(redirectByRole());
  }

  // 4️⃣ Permitir navegación normal
  next();
});

export default router;
