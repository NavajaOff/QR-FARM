import { Chart, registerables } from 'chart.js';
Chart.register(...registerables);

const createInventoryChart = (ctx, config) => {
  const ChartConstructor = (typeof window !== 'undefined' && window.Chart) ? window.Chart : Chart;
  const chartInstance = new ChartConstructor(ctx, config);
  chartInstance.update();
  return chartInstance;
};

export default {
  name: "Inventario",
  data() {
    return {
      animales: [
        { id: "001", nombre: "Holstein-001", raza: "Holstein", edad: 3, estado: "Saludable", potrero: "Potrero 1" },
        { id: "002", nombre: "Angus-002", raza: "Angus", edad: 2, estado: "En Tratamiento", potrero: "Potrero 2" },
        { id: "003", nombre: "Jersey-003", raza: "Jersey", edad: 4, estado: "Saludable", potrero: "Potrero 1" }
      ],
      chartInstance: null
    };
  },
  computed: {
    totalAnimales() {
      return this.animales.length;
    },
    countSaludable() {
      return this.animales.filter(a => a.estado === 'Saludable').length;
    },
    countTratamiento() {
      return this.animales.filter(a => a.estado === 'En Tratamiento').length;
    },
    countRecienNacidos() {
      return this.animales.filter(a => a.recién === true).length || 0;
    }
  },
  mounted() {
    if (this.chartInstance) {
      this.chartInstance.destroy();
      this.chartInstance = null;
    }

    const ctxElement = document.getElementById('inventarioPie');
    if (!ctxElement) {
      return;
    }

    const ctx = ctxElement.getContext('2d');
    const data = {
      labels: ['Saludables', 'En Tratamiento', 'Otros'],
      datasets: [{
        data: [
          this.countSaludable,
          this.countTratamiento,
          Math.max(0, this.totalAnimales - this.countSaludable - this.countTratamiento)
        ],
        backgroundColor: ['#28a745', '#ffc107', '#6c757d']
      }]
    };
    this.chartInstance = createInventoryChart(ctx, {
      type: 'doughnut',
      data,
      options: { responsive: true, maintainAspectRatio: false }
    });
  },
  beforeUnmount() {
    if (this.chartInstance) {
      this.chartInstance.destroy();
      this.chartInstance = null;
    }
  },
  methods: {
    verPerfilAnimal(id) {
      const a = this.animales.find(x => x.id === id);
      const html = `
        <div class="text-start">
          <p><strong>ID:</strong> ${a?.id || ''}</p>
          <p><strong>Nombre:</strong> ${a?.nombre || ''}</p>
          <p><strong>Raza:</strong> ${a?.raza || ''}</p>
          <p><strong>Edad:</strong> ${a?.edad || ''} años</p>
          <p><strong>Estado:</strong> ${a?.estado || ''}</p>
          <p><strong>Potrero:</strong> ${a?.potrero || ''}</p>
        </div>
      `;
      if (window.Swal) Swal.fire({ title: `Perfil ${id}`, html, confirmButtonColor: '#00d563' });
      else alert(`Perfil ${id}\n\n` + JSON.stringify(a, null, 2));
    },
    editarAnimal(id) {
      if (window.Swal) Swal.fire('Editar', `Aquí editarías al animal ${id}`, 'info');
      else alert('Editar ' + id);
    },
    estadoClass(estado) {
      if (estado === 'Saludable') return 'bg-success';
      if (estado === 'En Tratamiento') return 'bg-warning';
      if (estado === 'Enfermo') return 'bg-danger';
      return 'bg-secondary';
    }
  }
};