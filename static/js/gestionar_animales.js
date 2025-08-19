// JS extraído de gestionar_animales.html
function verPerfilAnimal(nombre) {
            // Obtener datos completos del animal
            let animales = JSON.parse(localStorage.getItem('animales')) || [];
            let animal = animales.find(a => a.nombre === nombre);
            Swal.fire({
                title: `Perfil de ${nombre}`,
                html: `
                    <div class="text-start">
                        <p><strong>Código QR:</strong> ${animal ? animal.codigoQR : 'Sin código'}</p>
                        <p><strong>Propietario:</strong> ${animal ? animal.propietario : 'Sin propietario'}</p>
                        <p><strong>Fecha de nacimiento:</strong> ${animal ? animal.fechaNacimiento : 'Sin dato'}</p>
                        <p><strong>Peso actual:</strong> ${animal ? animal.pesoActual : 'Sin dato'} kg</p>
                        <p><strong>Última vacunación:</strong> ${animal ? animal.ultimaVacunacion : 'Sin dato'}</p>
                        <p><strong>Próxima vacunación:</strong> ${animal ? animal.proximaVacunacion || 'Sin dato' : 'Sin dato'}</p>
                        <p><strong>Potrero actual:</strong> ${animal ? animal.potreroActual : 'Sin dato'}</p>
                        <p><strong>Historial médico:</strong> ${animal ? animal.historialMedico : 'Sin incidencias'}</p>
                    </div>
                `,
                confirmButtonColor: '#00d563'
            });
        }

        function editarAnimal(nombre) {
            let animales = JSON.parse(localStorage.getItem('animales')) || [];
            let animal = animales.find(a => a.nombre === nombre);
            if (!animal) return;
            Swal.fire({
                title: `Editar ${nombre}`,
                html: `
                    <form class='text-start'>
                        <div class='mb-2'>
                            <label class='form-label'>Nombre:</label>
                            <input id='editNombre' type='text' class='form-control' value='${animal.nombre}'>
                        </div>
                        <div class='mb-2'>
                            <label class='form-label'>Código QR:</label>
                            <input id='editCodigoQR' type='text' class='form-control' value='${animal.codigoQR}'>
                        </div>
                        <div class='mb-2'>
                            <label class='form-label'>Propietario:</label>
                            <input id='editPropietario' type='text' class='form-control' value='${animal.propietario}'>
                        </div>
                        <div class='row mb-2'>
                            <div class='col-6 mb-2'>
                                <label class='form-label'>Fecha de nacimiento:</label>
                                <input id='editFechaNacimiento' type='date' class='form-control' value='${animal.fechaNacimiento}'>
                            </div>
                            <div class='col-6 mb-2'>
                                <label class='form-label'>Peso actual (kg):</label>
                                <input id='editPesoActual' type='number' class='form-control' value='${animal.pesoActual}'>
                            </div>
                        </div>
                        <div class='row mb-2'>
                            <div class='col-6 mb-2'>
                                <label class='form-label'>Última vacunación:</label>
                                <input id='editUltimaVacunacion' type='date' class='form-control' value='${animal.ultimaVacunacion}'>
                            </div>
                            <div class='col-6 mb-2'>
                                <label class='form-label'>Próxima vacunación:</label>
                                <input id='editProximaVacunacion' type='date' class='form-control' value='${animal.proximaVacunacion || ''}'>
                            </div>
                        </div>
                        <div class='mb-2'>
                            <label class='form-label'>Potrero actual:</label>
                            <input id='editPotreroActual' type='text' class='form-control' value='${animal.potreroActual}'>
                        </div>
                        <div class='mb-2'>
                            <label class='form-label'>Historial médico:</label>
                            <select id='editHistorialMedico' class='form-select'>
                                <option value='Saludable' ${animal.historialMedico === 'Saludable' ? 'selected' : ''}>Saludable</option>
                                <option value='En tratamiento' ${animal.historialMedico === 'En tratamiento' ? 'selected' : ''}>En tratamiento</option>
                                <option value='Enfermo' ${animal.historialMedico === 'Enfermo' ? 'selected' : ''}>Enfermo</option>
                            </select>
                        </div>
                    </form>
                `,
                showCancelButton: true,
                confirmButtonText: 'Guardar Cambios',
                confirmButtonColor: '#00d563',
                preConfirm: () => {
                    const editNombre = document.getElementById('editNombre').value;
                    const editCodigoQR = document.getElementById('editCodigoQR').value;
                    const editPropietario = document.getElementById('editPropietario').value;
                    const editFechaNacimiento = document.getElementById('editFechaNacimiento').value;
                    const editPesoActual = document.getElementById('editPesoActual').value;
                    const editUltimaVacunacion = document.getElementById('editUltimaVacunacion').value;
                    const editPotreroActual = document.getElementById('editPotreroActual').value;
                    const editHistorialMedico = document.getElementById('editHistorialMedico').value;
                    const editProximaVacunacion = document.getElementById('editProximaVacunacion').value;
                    if (!editNombre || !editCodigoQR || !editPropietario || !editFechaNacimiento || !editPesoActual || !editUltimaVacunacion || !editProximaVacunacion || !editPotreroActual || !editHistorialMedico) {
                        Swal.showValidationMessage('Completa todos los campos');
                        return false;
                    }
                    return { editNombre, editCodigoQR, editPropietario, editFechaNacimiento, editPesoActual, editUltimaVacunacion, editProximaVacunacion, editPotreroActual, editHistorialMedico };
                }
            }).then((result) => {
                if (result.isConfirmed && result.value) {
                    // Actualizar animal en localStorage
                    animal.nombre = result.value.editNombre;
                    animal.codigoQR = result.value.editCodigoQR;
                    animal.propietario = result.value.editPropietario;
                    animal.fechaNacimiento = result.value.editFechaNacimiento;
                    animal.pesoActual = result.value.editPesoActual;
                    animal.ultimaVacunacion = result.value.editUltimaVacunacion;
                    animal.proximaVacunacion = result.value.editProximaVacunacion;
                    animal.potreroActual = result.value.editPotreroActual;
                    animal.historialMedico = result.value.editHistorialMedico;
                    localStorage.setItem('animales', JSON.stringify(animales));
                    Swal.fire('¡Cambios guardados!', '', 'success');
                    renderAnimales();
                }
            });
        }

        function agregarNuevoAnimal() {
            // Modal para crear animal con todos los campos organizados
            Swal.fire({
                title: 'Agregar Nuevo Animal',
                html: `
                    <form id='formNuevoAnimal' class='text-start'>
                        <div class='row mb-2'>
                            <div class='col-12 mb-2'>
                                <label class='form-label'>Nombre/Código:</label>
                                <input id='nombreAnimal' class='form-control' placeholder='Nombre/Código'>
                            </div>
                            <div class='col-12 mb-2'>
                                <label class='form-label'>Código QR:</label>
                                <input id='codigoQR' class='form-control' placeholder='Código QR (ej: QR-Holstein-001)'>
                            </div>
                            <div class='col-12 mb-2'>
                                <label class='form-label'>Propietario:</label>
                                <input id='propietarioAnimal' class='form-control' placeholder='Propietario'>
                            </div>
                            <div class='col-12 mb-2'>
                                <label class='form-label'>Raza:</label>
                                <select id='razaAnimal' class='form-select'>
                                    <option value='Holstein'>Holstein</option>
                                    <option value='Angus'>Angus</option>
                                    <option value='Jersey'>Jersey</option>
                                    <option value='Brahman'>Brahman</option>
                                </select>
                            </div>
                        </div>
                        <div class='row mb-2'>
                            <div class='col-6 mb-2'>
                                <label class='form-label'>Fecha de nacimiento:</label>
                                <input id='fechaNacimiento' class='form-control' type='date'>
                            </div>
                            <div class='col-6 mb-2'>
                                <label class='form-label'>Peso actual (kg):</label>
                                <input id='pesoActual' class='form-control' type='number' placeholder='Peso actual'>
                            </div>
                        </div>
                        <div class='row mb-2'>
                            <div class='col-6 mb-2'>
                                <label class='form-label'>Última vacunación:</label>
                                <input id='ultimaVacunacion' class='form-control' type='date'>
                            </div>
                            <div class='col-6 mb-2'>
                                <label class='form-label'>Próxima vacunación:</label>
                                <input id='proximaVacunacion' class='form-control' type='date'>
                            </div>
                        </div>
                        <div class='row mb-2'>
                            <div class='col-12 mb-2'>
                                <label class='form-label'>Potrero actual:</label>
                                <input id='potreroActual' class='form-control' placeholder='Potrero actual'>
                            </div>
                        </div>
                        <div class='row mb-2'>
                            <div class='col-12 mb-2'>
                                <label class='form-label'>Historial médico:</label>
                                <select id='historialMedico' class='form-select'>
                                    <option value='Saludable'>Saludable</option>
                                    <option value='En tratamiento'>En tratamiento</option>
                                    <option value='Enfermo'>Enfermo</option>
                                </select>
                            </div>
                        </div>
                    </form>
                `,
                showCancelButton: true,
                confirmButtonText: 'Crear',
                cancelButtonText: 'Cancelar',
                confirmButtonColor: '#00d563',
                cancelButtonColor: '#dc3545',
                preConfirm: () => {
                    const nombre = document.getElementById('nombreAnimal').value;
                    const codigoQR = document.getElementById('codigoQR').value;
                    const propietario = document.getElementById('propietarioAnimal').value;
                    const raza = document.getElementById('razaAnimal').value;
                    const fechaNacimiento = document.getElementById('fechaNacimiento').value;
                    const pesoActual = document.getElementById('pesoActual').value;
                    const ultimaVacunacion = document.getElementById('ultimaVacunacion').value;
                    const proximaVacunacion = document.getElementById('proximaVacunacion').value;
                    const potreroActual = document.getElementById('potreroActual').value;
                    const historialMedico = document.getElementById('historialMedico').value;
                    // Validación mejorada
                    if (
                        !nombre.trim() ||
                        !codigoQR.trim() ||
                        !propietario.trim() ||
                        !raza.trim() ||
                        !fechaNacimiento.trim() ||
                        !pesoActual.trim() ||
                        isNaN(Number(pesoActual)) ||
                        Number(pesoActual) <= 0 ||
                        !ultimaVacunacion.trim() ||
                        !proximaVacunacion.trim() ||
                        !potreroActual.trim() ||
                        !historialMedico.trim()
                    ) {
                        Swal.showValidationMessage('Completa todos los campos correctamente. El peso debe ser mayor a cero.');
                        return false;
                    }
                    return { nombre, codigoQR, propietario, raza, fechaNacimiento, pesoActual, ultimaVacunacion, proximaVacunacion, potreroActual, historialMedico };
                }
            }).then((result) => {
                if (result.isConfirmed && result.value) {
                    let animales = JSON.parse(localStorage.getItem('animales')) || [];
                    animales.push(result.value);
                    localStorage.setItem('animales', JSON.stringify(animales));
                    Swal.fire('¡Animal creado!', '', 'success');
                    renderAnimales();
                }
            });
        }

        function logout() {
            Swal.fire({
                title: '¿Cerrar sesión?',
                text: '¿Estás seguro de que quieres cerrar sesión?',
                icon: 'question',
                showCancelButton: true,
                confirmButtonText: 'Sí, cerrar sesión',
                cancelButtonText: 'Cancelar',
                confirmButtonColor: '#dc3545'
            }).then((result) => {
                if (result.isConfirmed) {
                    localStorage.removeItem('isLoggedIn');
                    localStorage.removeItem('nombreUsuario');
                    window.location.href = 'index.html';
                }
            });
        }

        // Verificar autenticación
        document.addEventListener('DOMContentLoaded', function() {
            // Eliminada la verificación de sesión y redirección automática
            renderAnimales();
        });

        function renderAnimales(filtro = "", raza = "Todas las razas", salud = "Todos los estados") {
            const animales = JSON.parse(localStorage.getItem('animales')) || [];
            const grid = document.getElementById('gridAnimales');
            grid.innerHTML = '';
            let filtrados = animales;
            if (filtro) {
                filtrados = filtrados.filter(a => a.nombre.toLowerCase().includes(filtro.toLowerCase()) || a.codigoQR.toLowerCase().includes(filtro.toLowerCase()));
            }
            if (raza && raza !== "Todas las razas") {
                filtrados = filtrados.filter(a => a.raza === raza);
            }
            if (salud && salud !== "Todos los estados") {
                filtrados = filtrados.filter(a => a.historialMedico === salud);
            }
            if (filtrados.length === 0) {
                grid.innerHTML = '<div class="col-12 text-center text-muted">No hay animales registrados.</div>';
                return;
            }
            filtrados.forEach(animal => {
                grid.innerHTML += `
                <div class="col-md-6 col-lg-4 mb-4">
                    <div class="card border-0 shadow-sm h-100">
                        <div class="card-body text-center">
                            <i class="fas fa-cow fa-3x mb-3" style="color:#00d563;"></i>
                            <h5 class="card-title">${animal.nombre}</h5>
                            <p class="text-muted">Código QR: ${animal.codigoQR}</p>
                            <p class="text-muted">Propietario: ${animal.propietario}</p>
                            <p class="text-muted">Raza: ${animal.raza}</p>
                            <p class="text-muted">Fecha nacimiento: ${animal.fechaNacimiento}</p>
                            <p class="text-muted">Peso: ${animal.pesoActual} kg</p>
                            <p class="text-muted">Última vacunación: ${animal.ultimaVacunacion}</p>
                            <p class="text-muted">Potrero: ${animal.potreroActual}</p>
                            <span class="badge bg-success mb-3">${animal.historialMedico}</span>
                            <div class="d-grid gap-2">
                                <button class="btn btn-outline-primary" onclick="verPerfilAnimal('${animal.nombre}')">
                                    <i class="fas fa-eye me-1"></i>Ver Perfil
                                </button>
                                <button class="btn btn-outline-warning" onclick="editarAnimal('${animal.nombre}')">
                                    <i class="fas fa-edit me-1"></i>Editar
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                `;
            });
        }

        function filtrarAnimales() {
            const filtro = document.getElementById('busquedaAnimal').value;
            const raza = document.querySelector("select.form-select").value;
            const salud = document.querySelectorAll("select.form-select")[1].value;
            renderAnimales(filtro, raza, salud);
        }
