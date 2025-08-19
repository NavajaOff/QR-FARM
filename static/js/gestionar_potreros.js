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
                <div class="row mb-3">
                    <div class="col-6">
                        <div class="border rounded p-2 text-center bg-light">
                            <strong>Fecha de último uso:</strong> ${p.fechaUltimoUso || ''}
                        </div>
                    </div>
                    <div class="col-6">
                        <div class="border rounded p-2 text-center bg-light">
                            <strong>Responsable:</strong> ${p.responsable}
                        </div>
                    </div>
                </div>
                <div class="row mb-3">
                    <div class="col-6">
                        <div class="border rounded p-2 text-center bg-light">
                            <strong>Área:</strong> ${p.area} hectáreas
                        </div>
                    </div>
                    <div class="col-6">
                        <div class="border rounded p-2 text-center bg-light">
                            <strong>Última limpieza:</strong> ${p.ultimaLimpieza || ''}
                        </div>
                    </div>
                    <div class="col-12">
                        <div class="border rounded p-2 text-center bg-light">
                            <strong>Próxima limpieza:</strong> ${p.proximaLimpieza || ''}
                        </div>
                    </div>
                </div>
                <div class="mb-3">
                    <div class="border rounded p-2 bg-light">
                        <strong>Notas:</strong> "${p.notas}"
                    </div>
                </div>
            </div>
            <div class="col-md-5">
                <div class="text-center">
                    <img src="../images/potrero.jpg" alt="Potrero con vacas" class="img-fluid rounded-3 shadow" style="max-width: 100%; height: 300px; object-fit: cover;">
                </div>
            </div>
        </div>
        <div class="row mt-4">
            <div class="col-12">
                <div class="d-flex justify-content-between align-items-center">
                    <button class="btn btn-outline-secondary" onclick="previousPotrero()">
                        <i class="fas fa-chevron-left me-1"></i>Anterior
                    </button>
                    <div class="d-flex gap-2">
                        <button class="btn btn-primary" onclick="editarPotrero()">
                            <i class="fas fa-edit me-1"></i>Editar
                        </button>
                        <button class="btn btn-success" onclick="crearPotrero()">
                            <i class="fas fa-plus me-1"></i>Crear Potrero
                        </button>
                    </div>
                    <button class="btn btn-outline-secondary" onclick="nextPotrero()">
                        Siguiente<i class="fas fa-chevron-right ms-1"></i>
                    </button>
                </div>
            </div>
        </div>
    `;
}

document.addEventListener('DOMContentLoaded', function() {
    mostrarPotrero(potreroActual);
});

function previousPotrero() {
    if (potreroActual > 0) {
        potreroActual--;
        mostrarPotrero(potreroActual);
    } else {
        Swal.fire({
            icon: 'info',
            title: 'Navegación',
            text: 'No hay potreros anteriores',
            confirmButtonColor: '#00d563'
        });
    }
}

function nextPotrero() {
    if (potreroActual < potreros.length - 1) {
        potreroActual++;
        mostrarPotrero(potreroActual);
    } else {
        Swal.fire({
            icon: 'info',
            title: 'Navegación',
            text: 'No hay más potreros',
            confirmButtonColor: '#00d563'
        });
    }
}

function editarPotrero() {
    const p = potreros[potreroActual];
    Swal.fire({
        title: `<i class='fas fa-edit'></i> Editar ${p.nombre}`,
        html: `
            <form id='editPotreroForm' class='text-start'>
                <div class='row mb-3'>
                    <div class='col-6'>
                        <label class='form-label'>Estado:</label>
                        <select class='form-select' id='estado'>
                            <option value='Disponible' ${p.estado === 'Disponible' ? 'selected' : ''}>Disponible</option>
                            <option value='Ocupado' ${p.estado === 'Ocupado' ? 'selected' : ''}>Ocupado</option>
                            <option value='Mantenimiento' ${p.estado === 'Mantenimiento' ? 'selected' : ''}>Mantenimiento</option>
                        </select>
                    </div>
                    <div class='col-6'>
                        <label class='form-label'>Capacidad:</label>
                        <input type='number' class='form-control' id='capacidad' value='${p.capacidad}'>
                    </div>
                </div>
                <div class='row mb-3'>
                    <div class='col-6'>
                        <label class='form-label'>Tipo de pasto:</label>
                        <input type='text' class='form-control' id='tipoPasto' value='${p.tipoPasto}'>
                    </div>
                    <div class='col-6'>
                        <label class='form-label'>Responsable:</label>
                        <input type='text' class='form-control' id='responsable' value='${p.responsable}'>
                    </div>
                </div>
                <div class='row mb-3'>
                    <div class='col-6'>
                        <label class='form-label'>Última limpieza:</label>
                        <input type='date' class='form-control' id='ultimaLimpieza' value='${p.ultimaLimpieza || ''}'>
                    </div>
                    <div class='col-6'>
                        <label class='form-label'>Próxima limpieza:</label>
                        <input type='date' class='form-control' id='proximaLimpieza' value='${p.proximaLimpieza || ''}'>
                    </div>
                </div>
                <div class='mb-3'>
                    <label class='form-label'>Área (hectáreas):</label>
                    <input type='number' step='0.1' class='form-control' id='area' value='${p.area}'>
                </div>
                <div class='mb-3'>
                    <label class='form-label'>Notas:</label>
                    <textarea class='form-control' id='notas' rows='3'>${p.notas}</textarea>
                </div>
            </form>
        `,
        showCancelButton: true,
        confirmButtonText: '<i class="fas fa-save"></i> Guardar Cambios',
        cancelButtonText: 'Cancelar',
        confirmButtonColor: '#00d563',
        width: '600px',
        preConfirm: () => {
            const estado = document.getElementById('estado').value;
            const capacidad = document.getElementById('capacidad').value;
            const tipoPasto = document.getElementById('tipoPasto').value;
            const responsable = document.getElementById('responsable').value;
            const ultimaLimpieza = document.getElementById('ultimaLimpieza').value;
            const proximaLimpieza = document.getElementById('proximaLimpieza').value;
            const area = document.getElementById('area').value;
            const notas = document.getElementById('notas').value;
            // Permitir guardar aunque algunos campos estén vacíos
            return { estado, capacidad, tipoPasto, responsable, ultimaLimpieza, proximaLimpieza, area, notas };
        }
    }).then((result) => {
        if (result.isConfirmed && result.value) {
            const p = potreros[potreroActual];
            // Solo actualiza si el campo tiene valor, si no, conserva el anterior
            p.estado = result.value.estado || p.estado;
            p.capacidad = result.value.capacidad ? parseInt(result.value.capacidad) : p.capacidad;
            p.tipoPasto = result.value.tipoPasto || p.tipoPasto;
            p.responsable = result.value.responsable || p.responsable;
            p.ultimaLimpieza = result.value.ultimaLimpieza || p.ultimaLimpieza;
            p.proximaLimpieza = result.value.proximaLimpieza || p.proximaLimpieza;
            p.area = result.value.area ? parseFloat(result.value.area) : p.area;
            p.notas = result.value.notas || p.notas;
            localStorage.setItem('potreros', JSON.stringify(potreros));
            Swal.fire({
                icon: 'success',
                title: 'Potrero actualizado',
                text: 'Los cambios se han guardado correctamente',
                confirmButtonColor: '#00d563'
            });
            mostrarPotrero(potreroActual);
        }
    });
}

function crearPotrero() {
    Swal.fire({
        title: '<i class="fas fa-plus"></i> Crear Nuevo Potrero',
        html: `
            <form id='newPotreroForm' class='text-start'>
                <div class='row mb-3'>
                    <div class='col-6'>
                        <label class='form-label'>Nombre del potrero:</label>
                        <input type='text' class='form-control' id='nombrePotrero' placeholder='Ej: Potrero 2'>
                    </div>
                    <div class='col-6'>
                        <label class='form-label'>Capacidad:</label>
                        <input type='number' class='form-control' id='capacidadNuevo' placeholder='Número de animales'>
                    </div>
                </div>
                <div class='row mb-3'>
                    <div class='col-6'>
                        <label class='form-label'>Tipo de pasto:</label>
                        <select class='form-select' id='tipoPastoNuevo'>
                            <option value=''>Seleccionar...</option>
                            <option value='Kikuyo'>Kikuyo</option>
                            <option value='Brachiaria'>Brachiaria</option>
                            <option value='Estrella'>Estrella</option>
                            <option value='Guinea'>Guinea</option>
                        </select>
                    </div>
                    <div class='col-6'>
                        <label class='form-label'>Responsable:</label>
                        <input type='text' class='form-control' id='responsableNuevo' placeholder='Nombre del responsable'>
                    </div>
                </div>
                <div class='row mb-3'>
                    <div class='col-6'>
                        <label class='form-label'>Última limpieza:</label>
                        <input type='date' class='form-control' id='ultimaLimpiezaNuevo'>
                    </div>
                    <div class='col-6'>
                        <label class='form-label'>Próxima limpieza:</label>
                        <input type='date' class='form-control' id='proximaLimpiezaNuevo'>
                    </div>
                </div>
                <div class='row mb-3'>
                    <div class='col-6'>
                        <label class='form-label'>Área (hectáreas):</label>
                        <input type='number' step='0.1' class='form-control' id='areaNuevo' placeholder='Ej: 3.5'>
                    </div>
                </div>
                <div class='mb-3'>
                    <label class='form-label'>Notas:</label>
                    <textarea class='form-control' id='notasNuevo' rows='3' placeholder='Observaciones adicionales...'></textarea>
                </div>
            </form>
        `,
        showCancelButton: true,
        confirmButtonText: '<i class="fas fa-plus"></i> Crear Potrero',
        cancelButtonText: 'Cancelar',
        confirmButtonColor: '#00d563',
        width: '600px',
        preConfirm: () => {
            const nombrePotrero = document.getElementById('nombrePotrero').value;
            const capacidadNuevo = document.getElementById('capacidadNuevo').value;
            const tipoPastoNuevo = document.getElementById('tipoPastoNuevo').value;
            const responsableNuevo = document.getElementById('responsableNuevo').value;
            const ultimaLimpiezaNuevo = document.getElementById('ultimaLimpiezaNuevo').value;
            const proximaLimpiezaNuevo = document.getElementById('proximaLimpiezaNuevo').value;
            const areaNuevo = document.getElementById('areaNuevo').value;
            const notasNuevo = document.getElementById('notasNuevo').value;
            if (!nombrePotrero || !capacidadNuevo || !tipoPastoNuevo || !responsableNuevo || !ultimaLimpiezaNuevo || !proximaLimpiezaNuevo || !areaNuevo) {
                Swal.showValidationMessage('Completa todos los campos');
                return false;
            }
            return { nombrePotrero, capacidadNuevo, tipoPastoNuevo, responsableNuevo, ultimaLimpiezaNuevo, proximaLimpiezaNuevo, areaNuevo, notasNuevo };
        }
    }).then((result) => {
        if (result.isConfirmed && result.value) {
            potreros.push({
                nombre: result.value.nombrePotrero,
                estado: 'Disponible',
                capacidad: parseInt(result.value.capacidadNuevo),
                ocupacion: 0,
                tipoPasto: result.value.tipoPastoNuevo,
                fechaUltimoUso: '',
                responsable: result.value.responsableNuevo,
                ultimaLimpieza: result.value.ultimaLimpiezaNuevo,
                proximaLimpieza: result.value.proximaLimpiezaNuevo,
                area: parseFloat(result.value.areaNuevo),
                notas: result.value.notasNuevo
            });
            localStorage.setItem('potreros', JSON.stringify(potreros));
            potreroActual = potreros.length - 1;
            Swal.fire({
                icon: 'success',
                title: 'Potrero creado',
                text: 'El nuevo potrero se ha creado exitosamente',
                confirmButtonColor: '#00d563'
            });
            mostrarPotrero(potreroActual);
        }
    });


        // Función para cerrar sesión
        function logout() {
            Swal.fire({
                title: '¿Cerrar sesión?',
                text: '¿Estás seguro de que quieres cerrar sesión?',
                icon: 'question',
                showCancelButton: true,
                confirmButtonText: 'Sí, cerrar sesión',
                cancelButtonText: 'Cancelar',
                confirmButtonColor: '#dc3545',
                cancelButtonColor: '#6c757d'
            }).then((result) => {
                if (result.isConfirmed) {
                    localStorage.removeItem('isLoggedIn');
                    localStorage.removeItem('nombreUsuario');
                    window.location.href = 'index.html';
                }
            });
        }

        // Verificar autenticación al cargar
        document.addEventListener('DOMContentLoaded', function() {
            const isLoggedIn = localStorage.getItem('isLoggedIn');
            if (isLoggedIn !== 'true') {
                window.location.href = 'iniciar_sesion.html';
            }
        });
    }
