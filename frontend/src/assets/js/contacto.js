 document.getElementById('contactForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const nombre = formData.get('nombre');
            const email = formData.get('email');
            const asunto = formData.get('asunto');
            const mensaje = formData.get('mensaje');
            
            if (nombre && email && asunto && mensaje) {
                Swal.fire({
                    title: 'Enviando mensaje...',
                    html: '<i class="fas fa-spinner fa-spin"></i> Por favor espera',
                    showConfirmButton: false,
                    allowOutsideClick: false,
                    timer: 2000
                }).then(() => {
                    Swal.fire({
                        icon: 'success',
                        title: '¡Mensaje enviado!',
                        html: `
                            <p>Gracias <strong>${nombre}</strong></p>
                            <p>Hemos recibido tu mensaje sobre: <strong>${asunto}</strong></p>
                            <p>Te responderemos a <strong>${email}</strong> en las próximas 24 horas.</p>
                        `,
                        confirmButtonColor: '#00d563'
                    }).then(() => {
                        // Limpiar formulario
                        document.getElementById('contactForm').reset();
                    });
                });
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'Por favor completa todos los campos obligatorios',
                    confirmButtonColor: '#dc3545'
                });
            }
        });