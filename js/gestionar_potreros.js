// JS extraído de gestionar_potreros.html
let potreros = JSON.parse(localStorage.getItem('potreros')) || [
    {
        nombre: 'Potrero 1',
        estado: 'Disponible',
        capacidad: 25,
        ocupacion: 18,
        tipoPasto: 'Kikuyo',
        fechaUltimoUso: '10/04/2025',
        responsable: 'Juan Pérez',
        area: 2.5,
        ultimaLimpieza: '10/04/2025',
        notas: 'Zona sombría, ideal para novillos'
    }
];
let potreroActual = 0;

function mostrarPotrero(idx) {
    const p = potreros[idx];
    if (!p) return;
    document.querySelector('.card-header h4').innerHTML = `<i class="fas fa-leaf me-2"></i>${p.nombre}`;
    const cardBody = document.querySelector('.card-body');
    cardBody.innerHTML = `
        <div class="row">
            <div class="col-md-7">
                <div class="row mb-3">
                    <div class="col-6">
                        <div class="border rounded p-2 text-center bg-light">
                            <strong>Estado:</strong> <span class="badge bg-success ms-1">${p.estado}</span>
                        </div>
                    </div>
                    <div class="col-6">
                        <div class="border rounded p-2 text-center bg-light">
                            <strong>Capacidad:</strong> ${p.capacidad} Animales
                        </div>
                    </div>
                </div>
                <div class="row mb-3">
                    <div class="col-6">
                        <div class="border rounded p-2 text-center bg-light">
                            <strong>Ocupación:</strong> ${p.ocupacion || 0} Animales
                        </div>
                    </div>
                    <div class="col-6">
                        <div class="border rounded p-2 text-center bg-light">
                            <strong>Tipo de pasto:</strong> ${p.tipoPasto}
                        </div>
                    </div>
                </div>
                <!-- ...continúa el render... -->
            </div>
        </div>
    `;
}
