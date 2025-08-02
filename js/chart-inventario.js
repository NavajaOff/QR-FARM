// Gráfica de pastel para inventario
window.addEventListener('DOMContentLoaded', function() {
  const ctx = document.getElementById('inventarioPie').getContext('2d');
  new Chart(ctx, {
    type: 'pie',
    data: {
      labels: ['Animales', 'Saludables', 'En Tratamiento', 'Recién Nacidos'],
      datasets: [{
        data: [125, 118, 5, 2],
        backgroundColor: [
          '#0d6efd', // Animales
          '#198754', // Saludables
          '#ffc107', // Tratamiento
          '#0dcaf0'  // Recién nacidos
        ],
        borderWidth: 1
      }]
    },
    options: {
      plugins: {
        legend: {
          display: false
        }
      }
    }
  });
});
