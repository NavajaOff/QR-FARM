import authService from '../../services/authService.js';

/**
 * Componente InventarioUsuario
 * Maneja la lógica del inventario de animales del usuario
 */
export default {
  name: "InventarioUsuario",
  data() {
    return {
      animales: [
        { id: 1, nombre: "Rosita", raza: "Brahman", edad: 2, estado: "Saludable", potrero: "Potrero 1" },
        { id: 2, nombre: "Luna", raza: "Brahman", edad: 1, estado: "En tratamiento", potrero: "Potrero 2" },
        { id: 3, nombre: "Bella", raza: "Holstein", edad: 3, estado: "Saludable", potrero: "Potrero 1" },
        { id: 4, nombre: "Max", raza: "Angus", edad: 4, estado: "Saludable", potrero: "Potrero 2" }
      ]
    };
  },
  mounted() {
    if (!authService.isAuthenticated() || !authService.isUser()) {
      this.$router.push('/login');
      return;
    }

    // Inicializar gráfico si Chart.js está disponible
    this.$nextTick(() => {
      this.initChart();
    });
  },
  computed: {
    /**
     * Total de animales
     */
    totalAnimales() {
      return this.animales.length;
    },

    /**
     * Cantidad de animales saludables
     */
    countSaludable() {
      return this.animales.filter(a => a.estado === 'Saludable').length;
    },

    /**
     * Cantidad de animales en tratamiento
     */
    countTratamiento() {
      return this.animales.filter(a => a.estado === 'En tratamiento').length;
    },

    /**
     * Cantidad de animales recién nacidos
     */
    countRecienNacidos() {
      return this.animales.filter(a => a.edad <= 1).length;
    }
  },
  methods: {
    /**
     * Inicializa el gráfico de inventario
     */
    initChart() {
      // Verificar si Chart.js está disponible
      if (typeof Chart !== 'undefined') {
        const ctx = document.getElementById('inventarioPie');
        if (ctx) {
          const chartCtx = ctx.getContext('2d');
          new Chart(chartCtx, {
            type: 'doughnut',
            data: {
              labels: ['Saludables', 'En tratamiento', 'Otros'],
              datasets: [{
                data: [
                  this.countSaludable,
                  this.countTratamiento,
                  Math.max(0, this.totalAnimales - this.countSaludable - this.countTratamiento)
                ],
                backgroundColor: ['#28a745', '#ffc107', '#6c757d'],
                borderWidth: 2,
                borderColor: '#fff'
              }]
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                legend: {
                  position: 'bottom',
                  labels: {
                    padding: 20,
                    usePointStyle: true
                  }
                }
              }
            }
          });
        }
      }
    },

    /**
     * Muestra el perfil de un animal
     * @param {number} id - ID del animal
     */
    verPerfilAnimal(id) {
      const animal = this.animales.find(a => a.id === id);
      if (animal) {
        const html = `
          <div class="text-start">
            <p><strong>ID:</strong> ${animal.id}</p>
            <p><strong>Nombre:</strong> ${animal.nombre}</p>
            <p><strong>Raza:</strong> ${animal.raza}</p>
            <p><strong>Edad:</strong> ${animal.edad} años</p>
            <p><strong>Estado:</strong> ${animal.estado}</p>
            <p><strong>Potrero:</strong> ${animal.potrero}</p>
          </div>
        `;
        if (window.Swal) {
          window.Swal.fire({
            title: `Perfil de ${animal.nombre}`,
            html,
            confirmButtonColor: '#28a745'
          });
        } else {
          alert(`Perfil de ${animal.nombre}\n\nID: ${animal.id}\nNombre: ${animal.nombre}\nRaza: ${animal.raza}\nEdad: ${animal.edad} años\nEstado: ${animal.estado}\nPotrero: ${animal.potrero}`);
        }
      }
    },

    /**
     * Edita un animal (funcionalidad pendiente)
     * @param {number} id - ID del animal
     */
    editarAnimal(id) {
      if (window.Swal) {
        window.Swal.fire('Editar Animal', `Funcionalidad para editar animal ${id} próximamente`, 'info');
      } else {
        alert(`Editar animal ${id}`);
      }
    },

    /**
     * Retorna la clase CSS para el estado del animal
     * @param {string} estado - Estado del animal
     * @returns {string} Clase CSS correspondiente
     */
    estadoClass(estado) {
      if (estado === 'Saludable') return 'bg-success';
      if (estado === 'En tratamiento') return 'bg-warning';
      if (estado === 'Enfermo') return 'bg-danger';
      return 'bg-secondary';
    }
  }
};