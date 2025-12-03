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
        component: () => import('../views/admin/DashboardContent.vue'),
        meta: { requiresAuth: true, role: 'admin', allowSuperAdmin: true }
      },
      {
        path: 'gestionar-usuarios',
        name: 'GestionarUsuarios',
        component: () => import('../views/admin/GestionarUsuarios.vue'),
        meta: { requiresAuth: true, role: 'admin', allowSuperAdmin: true }
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
        component: () => import('../views/admin/GestionarAnimalesAdmin.vue'),
        meta: { requiresAuth: true, role: 'admin', requiresTenant: true, blockSuperAdmin: true }
      },
      {
        path: 'gestionar-ganado',
        name: 'GestionarGanadoAdmin',
        component: () => import('../views/admin/GestionarAnimalesAdmin.vue'),
        meta: { requiresAuth: true, role: 'admin', requiresTenant: true, blockSuperAdmin: true }
      },
      {
        path: 'gestionar-ganados',
        name: 'GestionarGanadosAdmin',
        component: () => import('../views/admin/GestionarAnimalesAdmin.vue'),
        meta: { requiresAuth: true, role: 'admin', requiresTenant: true, blockSuperAdmin: true }
      },
      {
        path: 'gestionar-potreros',
        name: 'GestionarPotrerosAdmin',
        component: () => import('../views/admin/GestionarPotrerosAdmin.vue'),
        meta: { requiresAuth: true, role: 'admin', requiresTenant: true, blockSuperAdmin: true }
      },
      {
        path: 'reportes',
        name: 'ReportesAdmin',
        component: () => import('../views/admin/ReportesAdmin.vue'),
        meta: { requiresAuth: true, role: 'admin', requiresTenant: true, blockSuperAdmin: true }
      },
      {
        path: 'vacunacion',
        name: 'RegistroVacunacionAdmin',
        component: () => import('../views/admin/RegistroVacunacionAdmin.vue'),
        meta: { requiresAuth: true, role: 'admin', requiresTenant: true, blockSuperAdmin: true }
      },
      {
        path: 'perfil',
        name: 'PerfilAdmin',
        component: () => import('../views/admin/PerfilAdmin.vue'),
        meta: { requiresAuth: true, role: 'admin' }
      },
      {
        path: 'scan-qr',
        name: 'EscanearQRAdmin',
        component: () => import('../views/admin/EscanearQRAdmin.vue'),
        meta: { requiresAuth: true, role: 'admin', requiresTenant: true, blockSuperAdmin: true }
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
        component: () => import('../views/user/ReportesUsuario.vue'),
        meta: { requiresAuth: true, role: 'admin', requiresAdmin: true }
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
        component: () => import('../views/user/EscanearQRUsuario.vue'),
        meta: { requiresAuth: true, role: 'usuario', requiresTenant: true, allowAdmin: true }
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

    // Bloquear super_admin de rutas que explícitamente lo bloquean
    if (to.meta.blockSuperAdmin && isSuperAdmin) {
      return true;
    }

    // Validar si la ruta requiere tenant (no super admin)
    if (to.meta.requiresTenant && isSuperAdmin) {
      return true;
    }

    // Validar si la ruta requiere admin (para reportes de usuario)
    if (to.meta.requiresAdmin) {
      // Solo admin puede acceder (no super_admin)
      if (!isAdmin || isSuperAdmin) {
        return true;
      }
    }

    // Super admin solo puede acceder a rutas de organización (tenants, usuarios, dashboard)
    if (isSuperAdmin) {
      // Super admin puede acceder a rutas de super_admin
      if (to.meta.role === 'super_admin') return false;
      // Super admin puede acceder a rutas admin si allowSuperAdmin está habilitado (usuarios, dashboard)
      if (to.meta.role === 'admin' && to.meta.allowSuperAdmin) return false;
      // Bloquear todas las demás rutas para super_admin
      return true;
    }

    // Si la ruta requiere super_admin y el usuario NO es super_admin, bloquear
    if (to.meta.role === 'super_admin' && !isSuperAdmin) return true;

    // Si la ruta requiere admin, permitir solo si es admin (no super_admin)
    if (to.meta.role === 'admin') {
      return !isAdmin || isSuperAdmin;
    }

    // Si la ruta requiere usuario, permitir si es usuario O admin (admin puede acceder a rutas de usuario con allowAdmin)
    if (to.meta.role === 'usuario') {
      if (isUser) return false;
      // Admin también puede acceder a rutas de usuario si allowAdmin está habilitado (para scan-qr, etc.)
      if (to.meta.allowAdmin && isAdmin && !isSuperAdmin) return false;
      return true;
    }

    // Si el rol requerido no coincide con el rol del usuario, bloquear
    if (to.meta.role !== userRole) return true;

    return false;
  }

  // 1️⃣ Si requiere auth y NO hay token → LOGIN
  if (lacksAuth()) {
    return next('/login');
  }

  // 2️⃣ Si requiere rol y no coincide → redirigir según caso
  if (invalidRole()) {
    if (isRootOrLogin(to.path)) {
      return next(redirectByRole());
    }
    // Si un usuario normal intenta acceder a reportes, redirigir al inicio
    if (to.path === '/user/reportes' && isUser && !isAdmin && !isSuperAdmin) {
      return next('/user/inicio');
    }
    // Si super_admin intenta acceder a rutas bloqueadas, redirigir al dashboard
    if (isSuperAdmin && (to.meta.blockSuperAdmin || to.meta.requiresTenant || to.path.includes('/scan-qr'))) {
      return next('/admin/dashboard');
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
