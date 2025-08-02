// JS extraído de iniciar_sesion.html
document.getElementById('loginForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const usuario = document.getElementById('usuario').value.trim();
    const password = document.getElementById('password').value.trim();
    if (!usuario || !password) {
        Swal.fire({
            icon: 'error',
            title: 'Campos requeridos',
            text: 'Por favor completa todos los campos',
            confirmButtonColor: '#dc3545'
        });
        return;
    }
    Swal.fire({
        title: 'Iniciando sesión...',
        html: '<i class="fas fa-spinner fa-spin"></i> Verificando credenciales',
        showConfirmButton: false,
        allowOutsideClick: false,
        timer: 2000
    }).then(() => {
        localStorage.setItem('nombreUsuario', usuario);
        localStorage.setItem('isLoggedIn', 'true');
        Swal.fire({
            icon: 'success',
            title: '¡Bienvenido!',
            text: `Hola ${usuario}, sesión iniciada correctamente`,
            confirmButtonColor: '#00d563',
            timer: 1500,
            showConfirmButton: false
        }).then(() => {
            window.location.href = 'menu.html';
        });
    });
});
