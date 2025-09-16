// JS funcional para gestionar potreros
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
        proximaLimpieza: '',
        notas: 'Zona sombría, ideal para novillos'
    }
];
let potreroActual = 0;

// Funciones para gestionar potreros
function guardarEnLocalStorage() {
    localStorage.setItem('potreros', JSON.stringify(potreros));
}

function cargarDesdeLocalStorage() {
    potreros = JSON.parse(localStorage.getItem('potreros')) || [];
}

function agregarPotrero(potrero) {
    potreros.push(potrero);
    guardarEnLocalStorage();
}

function eliminarPotrero(index) {
    potreros.splice(index, 1);
    guardarEnLocalStorage();
}

function editarPotrero(index, potrero) {
    potreros[index] = potrero;
    guardarEnLocalStorage();
}

// Ejemplo de uso
cargarDesdeLocalStorage();
agregarPotrero({
    nombre: 'Potrero 2',
    estado: 'Ocupado',
    capacidad: 30,
    ocupacion: 25,
    tipoPasto: 'Ray Grass',
    fechaUltimoUso: '15/04/2025',
    responsable: 'María Gómez',
    area: 3.0,
    ultimaLimpieza: '15/04/2025',
    proximaLimpieza: '',
    notas: 'Buena disponibilidad de agua'
});
eliminarPotrero(0);
editarPotrero(0, {
    nombre: 'Potrero 2 Editado',
    estado: 'Disponible',
    capacidad: 30,
    ocupacion: 10,
    tipoPasto: 'Festuca',
    fechaUltimoUso: '20/04/2025',
    responsable: 'María Gómez',
    area: 3.0,
    ultimaLimpieza: '20/04/2025',
    proximaLimpieza: '',
    notas: 'Se recomienda fertilización'
});
