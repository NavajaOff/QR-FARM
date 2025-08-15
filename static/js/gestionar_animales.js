// JS extraído de gestionar_animales.html
function verPerfilAnimal(nombre) {
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
                    <label class='form-label'>Nombre/Código:</label>
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
                <!-- ...continúa el formulario... -->
            </form>
        `,
        confirmButtonColor: '#00d563'
    });
}
