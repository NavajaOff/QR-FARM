// JS extraído de crear_cuenta.html
document.getElementById('registerForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    const primerNombre = formData.get('primerNombre');
    const primerApellido = formData.get('primerApellido');
    const email = formData.get('email');
    const password = formData.get('password');
    const terminos = formData.get('terminos');
    if (!primerNombre || !primerApellido || !email || !password) {
        Swal.fire({
            icon: 'error',
            title: 'Campos requeridos',
            text: 'Por favor completa todos los campos obligatorios',
            confirmButtonColor: '#dc3545'
        });
        return;
    }
    if (!terminos) {
        Swal.fire({
            icon: 'error',
            title: 'Términos y condiciones',
            text: 'Debes aceptar los términos y condiciones para continuar',
            confirmButtonColor: '#dc3545'
        });
        return;
    }
    if (password.length < 6) {
        Swal.fire({
            icon: 'error',
            title: 'Contraseña débil',
            text: 'La contraseña debe tener al menos 6 caracteres',
            confirmButtonColor: '#dc3545'
        });
        return;
    }
    Swal.fire({
        title: 'Creando cuenta...',
        html: '<i class="fas fa-spinner fa-spin"></i> Procesando información',
        showConfirmButton: false,
        allowOutsideClick: false,
        timer: 2500
    }).then(() => {
        Swal.fire({
            icon: 'success',
            title: '¡Cuenta creada exitosamente!',
            html: `
                <p>Bienvenido <strong>${primerNombre} ${primerApellido}</strong></p>
                <p>Tu cuenta ha sido creada correctamente.</p>
                <p>Se ha enviado un email de confirmación a <strong>${email}</strong></p>
            `,
            confirmButtonColor: '#00d563',
            confirmButtonText: 'Continuar'
        }).then(() => {
            window.location.href = '/iniciar_sesion';
        });
    });
});
