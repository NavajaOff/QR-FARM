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

// Funciones auxiliares para el guard de navegación
function getRoleInfo(userRole) {
  return {
    isSuperAdmin: userRole === 'super_admin',
    isAdmin: userRole === 'admin' || userRole === 'administrador',
    isUser: userRole === 'usuario' || userRole === 'user'
  };
}

function redirectByRole(roleInfo) {
  if (roleInfo.isSuperAdmin || roleInfo.isAdmin) return '/admin/dashboard';
  if (roleInfo.isUser) return '/user/inicio';
  return '/login';
}

function lacksAuth(to, token) {
  return to.meta.requiresAuth && !token;
}

function checkRoleAlias(userRole, allowedRoles) {
  if (userRole === 'user' && allowedRoles.includes('usuario')) {
    return true;
  }
  if (userRole === 'administrador' && allowedRoles.includes('admin')) {
    return true;
  }
  return false;
}

function invalidRole(to, userRole, roleInfo) {
  if (!to.meta.allowedRoles || !Array.isArray(to.meta.allowedRoles)) {
    return false;
  }

  const roleAllowed = to.meta.allowedRoles.includes(userRole) || 
                     checkRoleAlias(userRole, to.meta.allowedRoles);
  
  if (!roleAllowed) {
    return true;
  }

  if (to.meta.requiresTenant && roleInfo.isSuperAdmin) {
    return true;
  }

  return false;
}

function handleSuperAdminRedirect(to) {
  const tenantRoutes = ['/scan-qr', '/ganado', '/potreros', '/vacunacion', '/reportes'];
  if (to.meta.requiresTenant || tenantRoutes.some(route => to.path.includes(route))) {
    return '/admin/dashboard';
  }
  return null;
}

function handleUserRedirect(to) {
  if (to.path.includes('/admin/') && !to.path.includes('/admin/dashboard')) {
    return '/user/inicio';
  }
  if (to.path.includes('/reportes')) {
    return '/user/inicio';
  }
  return null;
}

function handleAdminRedirect(to) {
  if (to.meta.allowedRoles && to.meta.allowedRoles.includes('super_admin') && 
      !to.meta.allowedRoles.includes('admin')) {
    return '/admin/dashboard';
  }
  return null;
}

function handleInvalidRoleRedirect(to, roleInfo) {
  if (isRootOrLogin(to.path)) {
    return redirectByRole(roleInfo);
  }
  
  const redirect = roleInfo.isSuperAdmin ? handleSuperAdminRedirect(to) :
                   roleInfo.isUser ? handleUserRedirect(to) :
                   roleInfo.isAdmin ? handleAdminRedirect(to) : null;
  
  return redirect || redirectByRole(roleInfo);
}

// Guard de navegación
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token');
  const userRole = localStorage.getItem('userRole');
  const roleInfo = getRoleInfo(userRole);

  if (lacksAuth(to, token)) {
    return next('/login');
  }

  if (invalidRole(to, userRole, roleInfo)) {
    return next(handleInvalidRoleRedirect(to, roleInfo));
  }

  if (token && isRootOrLogin(to.path)) {
    return next(redirectByRole(roleInfo));
  }

  next();
});

export default router;
