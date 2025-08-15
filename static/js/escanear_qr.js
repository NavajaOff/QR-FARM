function iniciarEscaneo() {
            Swal.fire({
                title: 'Iniciando escáner...',
                html: '<i class="fas fa-spinner fa-spin"></i> Activando cámara',
                showConfirmButton: false,
                timer: 2000
            }).then(() => {
                // Simular escaneo exitoso
                Swal.fire({
                    title: '¡Código QR detectado!',
                    html: `
                        <div class="text-start">
                            <h5>Holstein-001</h5>
                            <p><strong>Raza:</strong> Holstein</p>
                            <p><strong>Edad:</strong> 3 años</p>
                            <p><strong>Estado:</strong> <span class="badge bg-success">Saludable</span></p>
                            <p><strong>Potrero:</strong> Potrero 1</p>
                            <p><strong>Última revisión:</strong> 15/01/2024</p>
                        </div>
                    `,
                    confirmButtonText: 'Ver Perfil Completo',
                    confirmButtonColor: '#00d563'
                });
            });
        }

        function subirImagen() {
            Swal.fire({
                title: 'Subir imagen QR',
                html: `
                    <div class="mb-3">
                        <input type="file" class="form-control" accept="image/*">
                    </div>
                    <p class="text-muted">Selecciona una imagen que contenga un código QR</p>
                `,
                showCancelButton: true,
                confirmButtonText: 'Procesar Imagen',
                confirmButtonColor: '#00d563'
            });
        }

        function verDetalleEscaneo(animal) {
            Swal.fire({
                title: `Información de ${animal}`,
                html: `
                    <div class="text-start">
                        <p><strong>Código QR:</strong> QR-${animal}</p>
                        <p><strong>Fecha de escaneo:</strong> ${new Date().toLocaleString()}</p>
                        <p><strong>Ubicación:</strong> Potrero 1</p>
                        <p><strong>Estado actual:</strong> Saludable</p>
                        <p><strong>Observaciones:</strong> Sin novedades</p>
                    </div>
                `,
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