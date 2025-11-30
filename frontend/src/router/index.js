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
        path: 'gestionar-tenants',
        name: 'GestionarTenants',
        component: () => import('../views/admin/GestionarTenants.vue'),
        meta: { requiresAuth: true, role: 'super_admin' }
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

function isRootOrLogin(path) {
  return path === '/' || path === '/login';
}

// Guard de navegación
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token');
  const userRole = localStorage.getItem('userRole');

  const isAdmin = userRole === 'admin' || userRole === 'administrador' || userRole === 'super_admin';
  const isSuperAdmin = userRole === 'super_admin';
  const isUser = userRole === 'usuario' || userRole === 'user';

  function redirectByRole() {
    // Super admin y admin van al dashboard de admin
    if (isSuperAdmin || isAdmin) return '/admin/dashboard';
    if (isUser) return '/user/dashboard';
    return '/login';
  }

  function lacksAuth() {
    return to.meta.requiresAuth && !token;
  }

  function invalidRole() {
    // Si no hay rol requerido, permitir
    if (!to.meta.role) return false;

    // Super admin puede acceder a todas las rutas protegidas (excepto usuario si no es usuario)
    if (isSuperAdmin) {
      // Super admin puede acceder a cualquier ruta excepto las específicas de usuario
      return to.meta.role === 'usuario' && !isUser;
    }

    // Si la ruta requiere super_admin y el usuario NO es super_admin, bloquear
    if (to.meta.role === 'super_admin' && !isSuperAdmin) return true;

    // Si la ruta requiere admin y el usuario es admin o super_admin, permitir
    if (to.meta.role === 'admin' && isAdmin) return false;

    // Si la ruta requiere usuario y el usuario es usuario, permitir
    if (to.meta.role === 'usuario' && isUser) return false;

    // Si el rol requerido no coincide con el rol del usuario, bloquear
    if (to.meta.role !== userRole) return true;

    return false;
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
