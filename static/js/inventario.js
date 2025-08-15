function agregarAnimal() {
            Swal.fire({
                title: '<i class="fas fa-plus"></i> Agregar Nuevo Animal',
                html: `
                    <form class="text-start">
                        <div class="mb-3">
                            <label class="form-label">Código/Nombre:</label>
                            <input type="text" class="form-control" placeholder="Ej: Holstein-004">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Raza:</label>
                            <select class="form-select">
                                <option>Holstein</option>
                                <option>Angus</option>
                                <option>Jersey</option>
                                <option>Brahman</option>
                            </select>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Edad:</label>
                            <input type="text" class="form-control" placeholder="Ej: 2 años">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Potrero:</label>
                            <select class="form-select">
                                <option>Potrero 1</option>
                                <option>Potrero 2</option>
                                <option>Potrero 3</option>
                            </select>
                        </div>
                    </form>
                `,
                showCancelButton: true,
                confirmButtonText: 'Agregar',
                confirmButtonColor: '#00d563'
            });
        }

        function verDetalle(id) {
            Swal.fire({
                title: `Detalle del Animal ${id}`,
                text: 'Mostrando información detallada del animal',
                icon: 'info',
                confirmButtonColor: '#00d563'
            });
        }

        function editarAnimal(id) {
            Swal.fire({
                title: `Editar Animal ${id}`,
                text: 'Formulario de edición del animal',
                icon: 'info',
                confirmButtonColor: '#00d563'
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
        });