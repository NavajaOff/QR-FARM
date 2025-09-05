// JS extraído de menu.html
// Función para cambiar el menú activo
function setActiveMenu(element, section) {
    document.querySelectorAll('.sidebar .nav-link').forEach(link => {
        link.classList.remove('active');
    });
    element.classList.add('active');
    showSectionContent(section);
}

function showSectionContent(section) {
    switch(section) {
        case 'inventario':
            window.location.href = '/inventario';
            break;
        case 'gestionar-animales':
            window.location.href = '/gestionar_animales';
            break;
        case 'gestionar-potreros':
            window.location.href = '/gestionar_potreros';
            break;
        case 'escanear-qr':
            window.location.href = '/escanear_qr';
            break;
        case 'registrar-producto':
            window.location.href = '/registrar_producto';
            break;
        case 'vender-producto':
            window.location.href = '/vender_producto';
            break;
        case 'gestionar-clientes':
            window.location.href = '/gestionar_clientes';
            break;
        default:
            Swal.fire({
                title: 'Sección',
                text: 'Funcionalidad en desarrollo',
                icon: 'info',
                confirmButtonColor: '#00d563'
            });
    }
}

function showNotifications() {
    Swal.fire({
        title: '<i class="fas fa-bell"></i> Notificaciones',
        html: `
            <div class="text-start">
                <div class="alert alert-info">
                    <i class="fas fa-info-circle me-2"></i>
                    <strong>Recordatorio:</strong> Vacunación programada para mañana
                </div>
                <div class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    <strong>Alerta:</strong> Animal #125 requiere atención médica
                </div>
                <div class="alert alert-success">
                    <i class="fas fa-check-circle me-2"></i>
                    <strong>Completado:</strong> Registro de producción actualizado
                </div>
            </div>
        `,
        confirmButtonText: 'Marcar como leídas',
        confirmButtonColor: '#00d563',
        width: '600px'
    });
}

function generateReport() {
    Swal.fire({
        title: '<i class="fas fa-chart-bar"></i> Generar Reporte',
        html: `
            <div class="text-start">
                <div class="mb-3">
                    <label class="form-label fw-bold">Tipo de Reporte:</label>
                    <select class="form-select" id="tipoReporte">
                        <option value="produccion">Reporte de Producción</option>
                        <option value="salud">Reporte de Salud</option>
                        <option value="inventario">Reporte de Inventario</option>
                        <option value="financiero">Reporte Financiero</option>
                    </select>
                </div>
                <div class="mb-3">
                    <label class="form-label fw-bold">Período:</label>
                    <select class="form-select" id="periodo">
                        <option value="semana">Última semana</option>
                        <option value="mes">Último mes</option>
                        <option value="trimestre">Último trimestre</option>
                        <option value="año">Último año</option>
                    </select>
                </div>
            </div>
        `,
        showCancelButton: true,
        confirmButtonText: '<i class="fas fa-download"></i> Generar',
        cancelButtonText: 'Cancelar',
        confirmButtonColor: '#00d563',
        preConfirm: () => {
            const tipo = document.getElementById('tipoReporte').value;
            const periodo = document.getElementById('periodo').value;
            return { tipo, periodo };
        }
    }).then((result) => {
        if (result.isConfirmed) {
            Swal.fire({
                icon: 'success',
                title: 'Reporte generado',
                text: `Reporte de ${result.value.tipo} para ${result.value.periodo} generado exitosamente`,
                confirmButtonColor: '#00d563'
            });
        }
    });
}

function logout(event) {
    if (event) event.preventDefault();
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
            Swal.fire({
                title: 'Cerrando sesión...',
                html: '<i class="fas fa-spinner fa-spin"></i> Hasta pronto',
                showConfirmButton: false,
                timer: 1500
            }).then(() => {
                window.location.href = '/';
            });
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    // El backend Flask controla la sesión. Solo mostramos el nombre si está disponible en el DOM.
    const nombreUsuarioElem = document.getElementById('nombreUsuario');
    if (nombreUsuarioElem) {
        nombreUsuarioElem.textContent = nombreUsuarioElem.textContent || 'Usuario';
    }
});

function activarEscanearQR() {
    const elemento = document.querySelector('a[onclick*="escanear-qr"]');
    setActiveMenu(elemento, 'escanear-qr');
}

function activarRegistrarProducto() {
    const elemento = document.querySelector('a[onclick*="registrar-producto"]');
    setActiveMenu(elemento, 'registrar-producto');
}
