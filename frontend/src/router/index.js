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
    meta: { requiresAuth: true, allowedRoles: ['admin', 'super_admin'] },
    children: [
      {
        path: 'dashboard',
        name: 'DashboardAdmin',
        component: () => import('../views/admin/DashboardContent.vue'),
        meta: { requiresAuth: true, allowedRoles: ['admin', 'super_admin'] }
      },
      {
        path: 'gestionar-usuarios',
        name: 'GestionarUsuarios',
        component: () => import('../views/admin/GestionarUsuarios.vue'),
        meta: { requiresAuth: true, allowedRoles: ['admin', 'super_admin'] }
      },
      {
        path: 'gestionar-tenants',
        name: 'GestionarTenants',
        component: () => import('../views/admin/GestionarTenants.vue'),
        meta: { requiresAuth: true, allowedRoles: ['super_admin'] }
      },
      {
        path: 'gestionar-animales',
        name: 'GestionarAnimalesAdmin',
        component: () => import('../views/admin/GestionarAnimalesAdmin.vue'),
        meta: { requiresAuth: true, allowedRoles: ['admin'], requiresTenant: true }
      },
      {
        path: 'gestionar-ganado',
        name: 'GestionarGanadoAdmin',
        component: () => import('../views/admin/GestionarAnimalesAdmin.vue'),
        meta: { requiresAuth: true, allowedRoles: ['admin'], requiresTenant: true }
      },
      {
        path: 'gestionar-ganados',
        name: 'GestionarGanadosAdmin',
        component: () => import('../views/admin/GestionarAnimalesAdmin.vue'),
        meta: { requiresAuth: true, allowedRoles: ['admin'], requiresTenant: true }
      },
      {
        path: 'gestionar-potreros',
        name: 'GestionarPotrerosAdmin',
        component: () => import('../views/admin/GestionarPotrerosAdmin.vue'),
        meta: { requiresAuth: true, allowedRoles: ['admin'], requiresTenant: true }
      },
      {
        path: 'reportes',
        name: 'ReportesAdmin',
        component: () => import('../views/admin/ReportesAdmin.vue'),
        meta: { requiresAuth: true, allowedRoles: ['admin'], requiresTenant: true }
      },
      {
        path: 'vacunacion',
        name: 'RegistroVacunacionAdmin',
        component: () => import('../views/admin/RegistroVacunacionAdmin.vue'),
        meta: { requiresAuth: true, allowedRoles: ['admin'], requiresTenant: true }
      },
      {
        path: 'perfil',
        name: 'PerfilAdmin',
        component: () => import('../views/admin/PerfilAdmin.vue'),
        meta: { requiresAuth: true, allowedRoles: ['admin', 'super_admin'] }
      },
      {
        path: 'scan-qr',
        name: 'EscanearQRAdmin',
        component: () => import('../views/admin/EscanearQRAdmin.vue'),
        meta: { requiresAuth: true, allowedRoles: ['admin'], requiresTenant: true }
      }
    ]
  },

  // Rutas de usuario con layout anidado
  {
    path: '/user',
    component: () => import('../layouts/UserLayout.vue'),
    meta: { requiresAuth: true, allowedRoles: ['usuario'] },
    children: [
      {
        path: '',
        redirect: { name: 'InicioUsuario' }
      },
      {
        path: 'inicio',
        name: 'InicioUsuario',
        component: () => import('../views/user/DashboardContent.vue'),
        meta: { requiresAuth: true, allowedRoles: ['usuario'] }
      },
      {
        path: 'dashboard',
        redirect: { name: 'InicioUsuario' }
      },
      {
        path: 'ganado',
        name: 'GanadoUsuario',
        component: () => import('../views/user/GestionarAnimalesUsuario.vue'),
        meta: { requiresAuth: true, allowedRoles: ['usuario'], requiresTenant: true }
      },
      {
        path: 'gestionar-animales',
        redirect: { name: 'GanadoUsuario' }
      },
      {
        path: 'potreros',
        name: 'PotrerosUsuario',
        component: () => import('../views/user/GestionarPotrerosUsuario.vue'),
        meta: { requiresAuth: true, allowedRoles: ['usuario'], requiresTenant: true }
      },
      {
        path: 'registro-vacunacion',
        name: 'RegistroVacunacionUsuario',
        component: () => import('../views/user/RegistroVacunacionUsuario.vue'),
        meta: { requiresAuth: true, allowedRoles: ['usuario'], requiresTenant: true }
      },
      {
        path: 'vacunacion',
        redirect: { name: 'RegistroVacunacionUsuario' }
      },
      {
        path: 'perfil',
        name: 'PerfilUsuario',
        component: () => import('../views/user/PerfilUsuario.vue'),
        meta: { requiresAuth: true, allowedRoles: ['usuario'] }
      },
      {
        path: 'scan-qr',
        name: 'EscanearQRUsuario',
        component: () => import('../views/user/EscanearQRUsuario.vue'),
        meta: { requiresAuth: true, allowedRoles: ['usuario'], requiresTenant: true }
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

  const isSuperAdmin = userRole === 'super_admin';
  const isAdmin = userRole === 'admin' || userRole === 'administrador';
  const isUser = userRole === 'usuario' || userRole === 'user';

  function redirectByRole() {
    if (isSuperAdmin) return '/admin/dashboard';
    if (isAdmin) return '/admin/dashboard';
    if (isUser) return '/user/inicio';
    return '/login';
  }

  function lacksAuth() {
    return to.meta.requiresAuth && !token;
  }

  function invalidRole() {
    // Si no hay roles permitidos definidos, permitir
    if (!to.meta.allowedRoles || !Array.isArray(to.meta.allowedRoles)) {
      return false;
    }

    // Verificar si el rol del usuario está en los roles permitidos
    // Manejar alias: 'user' es equivalente a 'usuario', 'administrador' es equivalente a 'admin'
    let roleAllowed = to.meta.allowedRoles.includes(userRole);
    
    // Si no está permitido directamente, verificar alias
    if (!roleAllowed) {
      if (userRole === 'user' && to.meta.allowedRoles.includes('usuario')) {
        roleAllowed = true;
      } else if (userRole === 'administrador' && to.meta.allowedRoles.includes('admin')) {
        roleAllowed = true;
      }
    }
    
    if (!roleAllowed) {
      return true;
    }

    // Validar si la ruta requiere tenant (super_admin no tiene tenant)
    if (to.meta.requiresTenant && isSuperAdmin) {
      return true;
    }

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
    
    // Redirecciones específicas según el rol
    if (isSuperAdmin) {
      // Super admin intentando acceder a rutas de tenant (ganado, potreros, QR, etc.)
      if (to.meta.requiresTenant || to.path.includes('/scan-qr') || 
          to.path.includes('/ganado') || to.path.includes('/potreros') ||
          to.path.includes('/vacunacion') || to.path.includes('/reportes')) {
        return next('/admin/dashboard');
      }
    }
    
    if (isUser) {
      // Usuario intentando acceder a rutas de admin
      if (to.path.includes('/admin/') && !to.path.includes('/admin/dashboard')) {
        return next('/user/inicio');
      }
      // Usuario intentando acceder a reportes
      if (to.path.includes('/reportes')) {
        return next('/user/inicio');
      }
    }
    
    if (isAdmin) {
      // Admin intentando acceder a rutas de super_admin
      if (to.meta.allowedRoles && to.meta.allowedRoles.includes('super_admin') && 
          !to.meta.allowedRoles.includes('admin')) {
        return next('/admin/dashboard');
      }
    }
    
    return next(redirectByRole());
  }

  // 3️⃣ Si ya está autenticado y va a login → mandarlo a su dashboard
  if (token && isRootOrLogin(to.path)) {
    return next(redirectByRole());
  }

  // 4️⃣ Permitir navegación normal
  next();
});

export default router;
