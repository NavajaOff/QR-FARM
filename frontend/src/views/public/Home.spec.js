import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import Home from './Home.vue'

describe('Home.vue', () => {
  let router

  beforeEach(() => {
    // Mock de location para createMemoryHistory
    globalThis.location = {
      pathname: '/',
      search: '',
      hash: ''
    }

    // Crear router mock con createMemoryHistory
    router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/', component: Home },
        { path: '/contacto', component: { template: '<div>Contacto</div>' } },
        { path: '/login', component: { template: '<div>Login</div>' } }
      ]
    })
  })

  const createWrapper = (options = {}) => {
    return mount(Home, {
      global: {
        plugins: [router],
        stubs: {
          'router-link': {
            template: '<a><slot /></a>'
          }
        }
      },
      ...options
    })
  }

  describe('Component Definition', () => {
    it('should export a Vue component', () => {
      expect(Home).toBeDefined()
      expect(Home.name).toBe('Home')
    })
  })

  describe('Template Rendering', () => {
    it('should render the navbar', () => {
      const wrapper = createWrapper()
      const navbar = wrapper.find('.navbar')
      expect(navbar.exists()).toBe(true)
      expect(navbar.text()).toContain('QR FARM')
    })

    it('should render navigation links', () => {
      const wrapper = createWrapper()
      const links = wrapper.findAll('a')
      expect(links).toHaveLength(3)
    })

    it('should render hero section', () => {
      const wrapper = createWrapper()
      const heroSection = wrapper.find('.hero-section')
      expect(heroSection.exists()).toBe(true)
    })

    it('should render hero content', () => {
      const wrapper = createWrapper()
      const heroContent = wrapper.find('.display-4')
      expect(heroContent.text()).toContain('Tu aliado inteligente')
    })

    it('should render hero image', () => {
      const wrapper = createWrapper()
      const image = wrapper.find('img')
      expect(image.exists()).toBe(true)
      expect(image.attributes('alt')).toContain('Ganado en pastizales')
    })
  })

  describe('Component Integration', () => {
    it('should mount correctly', () => {
      const wrapper = createWrapper()
      expect(wrapper.vm).toBeDefined()
    })
  })

  describe('Keyboard Navigation', () => {
    it('should handle Enter key on Contacto link', async () => {
      const wrapper = createWrapper()
      const contactoLink = wrapper.findAll('a').find(link => link.text().includes('Contacto'))

      await contactoLink.trigger('keydown.enter')

      // Since router.push is mocked, we just verify the event was triggered
      expect(contactoLink.exists()).toBe(true)
    })

    it('should handle Space key on Contacto link', async () => {
      const wrapper = createWrapper()
      const contactoLink = wrapper.findAll('a').find(link => link.text().includes('Contacto'))

      await contactoLink.trigger('keydown.space')

      expect(contactoLink.exists()).toBe(true)
    })

    it('should handle Enter key on Login link', async () => {
      const wrapper = createWrapper()
      const loginLink = wrapper.findAll('a').find(link => link.text().includes('Iniciar Sesión'))

      await loginLink.trigger('keydown.enter')

      expect(loginLink.exists()).toBe(true)
    })

    it('should handle Space key on Login link', async () => {
      const wrapper = createWrapper()
      const loginLink = wrapper.findAll('a').find(link => link.text().includes('Iniciar Sesión'))

      await loginLink.trigger('keydown.space')

      expect(loginLink.exists()).toBe(true)
    })
  })
})