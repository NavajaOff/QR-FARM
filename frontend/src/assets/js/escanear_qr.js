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
