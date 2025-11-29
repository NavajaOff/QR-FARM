import { ganadoAPI, potreroAPI, userAPI, tenantAPI } from '../../services/api.js';
import authService from '../../services/authService.js';

const secureRandomInt = (min, max) => {
  const lower = Number(min);
  const upper = Number(max);
  if (!Number.isFinite(lower) || !Number.isFinite(upper) || lower > upper) {
    return lower;
  }

  if (typeof window !== 'undefined' && window.crypto?.getRandomValues) {
    const range = upper - lower + 1;
    const buffer = new Uint32Array(1);
    window.crypto.getRandomValues(buffer);
    const randomFraction = buffer[0] / 0x100000000;
    return lower + Math.floor(randomFraction * range);
  }

  return lower;
};

export default {
  name: 'DashboardContent',
  data() {
    return {
      estadisticas: {
        usuarios: 0,
        ganado: 0,
        potreros: 0,
        salud: 0,
        tenants: 0
      },
      currentTenant: null,
      isSuperAdmin: false,
      tenants: []
    };
  },
  mounted() {
    console.log('[DashboardContent] Componente montado');
    this.checkUserRole();
    console.log('[DashboardContent] isSuperAdmin:', this.isSuperAdmin);
    
    if (this.isSuperAdmin) {
      console.log('[DashboardContent] Cargando tenants para super admin...');
      this.cargarTenants();
    }
    
    console.log('[DashboardContent] Cargando estadísticas...');
    this.cargarEstadisticas();
    
    if (!this.isSuperAdmin) {
      console.log('[DashboardContent] Cargando tenant actual para admin normal...');
      this.cargarTenantActual();
    }
    
    // Escuchar cambios de tenant
    globalThis.addEventListener('tenant-selected', this.onTenantChanged);
  },
  beforeUnmount() {
    globalThis.removeEventListener('tenant-selected', this.onTenantChanged);
  },
  methods: {
    checkUserRole() {
      const role = authService.getRole();
      this.isSuperAdmin = role === 'super_admin';
      console.log('[DashboardContent] Rol verificado:', role, 'isSuperAdmin:', this.isSuperAdmin);
    },
    async cargarTenants() {
      try {
        console.log('[DashboardContent] Iniciando carga de tenants...');
        const response = await tenantAPI.getAll(true);
        console.log('[DashboardContent] Respuesta de tenants:', response);
        
        if (response.data?.status === 'success') {
          this.tenants = response.data.data || [];
          this.estadisticas.tenants = this.tenants.length;
          console.log('[DashboardContent] Tenants cargados:', this.tenants.length);
        } else {
          console.warn('[DashboardContent] Respuesta de tenants sin éxito:', response.data);
          this.tenants = [];
          this.estadisticas.tenants = 0;
        }
      } catch (error) {
        console.error('[DashboardContent] Error cargando tenants:', error);
        console.error('[DashboardContent] Detalles del error:', {
          message: error.message,
          response: error.response?.data,
          status: error.response?.status
        });
        this.tenants = [];
        this.estadisticas.tenants = 0;
      }
    },
    async cargarTenantActual() {
      try {
        const user = authService.getUser();
        const tenantId = user?.tenant_id;
        
        if (tenantId) {
          const response = await tenantAPI.getById(tenantId);
          if (response.data?.status === 'success') {
            this.currentTenant = response.data.data;
          }
        }
      } catch (error) {
        console.warn('Error cargando tenant actual:', error);
      }
    },
    onTenantChanged() {
      // Recargar estadísticas cuando cambia el tenant
      this.cargarEstadisticas();
    },
    async cargarEstadisticas() {
      console.log('[DashboardContent] Iniciando carga de estadísticas, isSuperAdmin:', this.isSuperAdmin);
      
      try {
        if (this.isSuperAdmin) {
          console.log('[DashboardContent] Cargando estadísticas para super admin...');
          
          // Para super admin, cargar usuarios y tenants
          try {
            console.log('[DashboardContent] Cargando usuarios...');
            const usuariosResponse = await userAPI.getAll();
            console.log('[DashboardContent] Respuesta de usuarios:', usuariosResponse);
            
            if (usuariosResponse.data?.status === 'success') {
              this.estadisticas.usuarios = usuariosResponse.data?.data?.length || 0;
              console.log('[DashboardContent] Usuarios cargados:', this.estadisticas.usuarios);
            } else {
              console.warn('[DashboardContent] Respuesta de usuarios sin éxito:', usuariosResponse.data);
              this.estadisticas.usuarios = 0;
            }
          } catch (userError) {
            console.error('[DashboardContent] Error cargando usuarios:', userError);
            console.error('[DashboardContent] Detalles:', {
              message: userError.message,
              response: userError.response?.data,
              status: userError.response?.status
            });
            this.estadisticas.usuarios = 0;
          }

          // Tenants ya se cargan en cargarTenants()
          // Si hay tenant seleccionado, cargar estadísticas de ese tenant
          const selectedTenantId = localStorage.getItem('qr_farm_selected_tenant_id');
          console.log('[DashboardContent] Tenant seleccionado:', selectedTenantId);
          
          if (selectedTenantId) {
            try {
              console.log('[DashboardContent] Cargando ganado para tenant:', selectedTenantId);
              const ganadoResponse = await ganadoAPI.getAll();
              console.log('[DashboardContent] Respuesta de ganado:', ganadoResponse);
              
              if (ganadoResponse.data?.status === 'success') {
                this.estadisticas.ganado = ganadoResponse.data?.data?.length || 0;
                console.log('[DashboardContent] Ganado cargado:', this.estadisticas.ganado);
              } else {
                console.warn('[DashboardContent] Respuesta de ganado sin éxito:', ganadoResponse.data);
                this.estadisticas.ganado = 0;
              }
            } catch (ganadoError) {
              console.error('[DashboardContent] Error cargando ganado:', ganadoError);
              this.estadisticas.ganado = 0;
            }

            try {
              console.log('[DashboardContent] Cargando potreros para tenant:', selectedTenantId);
              const potrerosResponse = await potreroAPI.getAll();
              console.log('[DashboardContent] Respuesta de potreros:', potrerosResponse);
              
              if (potrerosResponse.data?.status === 'success') {
                this.estadisticas.potreros = potrerosResponse.data?.data?.length || 0;
                console.log('[DashboardContent] Potreros cargados:', this.estadisticas.potreros);
              } else {
                console.warn('[DashboardContent] Respuesta de potreros sin éxito:', potrerosResponse.data);
                this.estadisticas.potreros = 0;
              }
            } catch (potreroError) {
              console.error('[DashboardContent] Error cargando potreros:', potreroError);
              this.estadisticas.potreros = 0;
            }
          } else {
            console.log('[DashboardContent] No hay tenant seleccionado, estableciendo valores en 0');
            this.estadisticas.ganado = 0;
            this.estadisticas.potreros = 0;
          }
        } else {
          console.log('[DashboardContent] Cargando estadísticas para admin normal...');
          
          // Para admin normal, cargar todas las estadísticas
          try {
            console.log('[DashboardContent] Cargando usuarios...');
            const usuariosResponse = await userAPI.getAll();
            console.log('[DashboardContent] Respuesta de usuarios:', usuariosResponse);
            
            if (usuariosResponse.data?.status === 'success') {
              this.estadisticas.usuarios = usuariosResponse.data?.data?.length || 0;
              console.log('[DashboardContent] Usuarios cargados:', this.estadisticas.usuarios);
            } else {
              console.warn('[DashboardContent] Respuesta de usuarios sin éxito:', usuariosResponse.data);
              this.estadisticas.usuarios = 0;
            }
          } catch (userError) {
            console.error('[DashboardContent] Error cargando usuarios:', userError);
            console.error('[DashboardContent] Detalles:', {
              message: userError.message,
              response: userError.response?.data,
              status: userError.response?.status
            });
            this.estadisticas.usuarios = 0;
          }

          try {
            console.log('[DashboardContent] Cargando ganado...');
            const ganadoResponse = await ganadoAPI.getAll();
            console.log('[DashboardContent] Respuesta de ganado:', ganadoResponse);
            
            if (ganadoResponse.data?.status === 'success') {
              this.estadisticas.ganado = ganadoResponse.data?.data?.length || 0;
              console.log('[DashboardContent] Ganado cargado:', this.estadisticas.ganado);
            } else {
              console.warn('[DashboardContent] Respuesta de ganado sin éxito:', ganadoResponse.data);
              this.estadisticas.ganado = 0;
            }
          } catch (ganadoError) {
            console.error('[DashboardContent] Error cargando ganado:', ganadoError);
            console.error('[DashboardContent] Detalles:', {
              message: ganadoError.message,
              response: ganadoError.response?.data,
              status: ganadoError.response?.status
            });
            this.estadisticas.ganado = 0;
          }

          try {
            console.log('[DashboardContent] Cargando potreros...');
            const potrerosResponse = await potreroAPI.getAll();
            console.log('[DashboardContent] Respuesta de potreros:', potrerosResponse);
            
            if (potrerosResponse.data?.status === 'success') {
              this.estadisticas.potreros = potrerosResponse.data?.data?.length || 0;
              console.log('[DashboardContent] Potreros cargados:', this.estadisticas.potreros);
            } else {
              console.warn('[DashboardContent] Respuesta de potreros sin éxito:', potrerosResponse.data);
              this.estadisticas.potreros = 0;
            }
          } catch (potreroError) {
            console.error('[DashboardContent] Error cargando potreros:', potreroError);
            console.error('[DashboardContent] Detalles:', {
              message: potreroError.message,
              response: potreroError.response?.data,
              status: potreroError.response?.status
            });
            this.estadisticas.potreros = 0;
          }

          // Salud promedio simulada
          this.estadisticas.salud = secureRandomInt(80, 99);
          console.log('[DashboardContent] Salud promedio:', this.estadisticas.salud);
        }
        
        console.log('[DashboardContent] Estadísticas finales:', this.estadisticas);
      } catch (error) {
        console.error('[DashboardContent] Error general cargando estadísticas:', error);
        console.error('[DashboardContent] Stack trace:', error.stack);
        // En caso de error general, mostrar valores por defecto
        this.estadisticas = {
          usuarios: this.isSuperAdmin ? 0 : 0,
          ganado: 0,
          potreros: 0,
          salud: 85,
          tenants: 0
        };
      }
    }
  }
};