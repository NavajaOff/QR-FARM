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
                <p><strong>Encargado:</strong> ${animal ? animal.propietario : 'Sin encargado'}</p>
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
