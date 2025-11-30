import { createRouter, createMemoryHistory } from 'vue-router'

const routes = [
  { path: '/login', name: 'Login' },
  { path: '/admin/dashboard', name: 'DashboardAdmin', meta: { requiresAuth: true, role: 'admin' } }
]

describe('Router Guards', () => {
  let router

  beforeEach(() => {
    router = createRouter({
      history: createMemoryHistory(),
      routes
    })

    // Add navigation guard
    router.beforeEach((to, from, next) => {
      const token = localStorage.getItem('token')

      if (to.meta.requiresAuth && !token) {
        return next('/login')
      }

      next()
    })
  })

  it('should redirect to login when accessing protected route without token', async () => {
    localStorage.clear()
    await router.push('/admin/dashboard')
    await router.isReady()
    expect(router.currentRoute.value.path).toBe('/login')
  })

  it('should allow access to login route', async () => {
    localStorage.clear()
    await router.push('/login')
    await router.isReady()
    expect(router.currentRoute.value.path).toBe('/login')
  })
})
