let registrosVacunacion = [
    {
        id: 1,
        idAnimal: "001",
        nombre: "Holstein-001",
        tipoVacuna: "Brucelosis",
        fechaAplicacion: "2025-02-15",
        proximaDosis: "2025-08-15",
        responsable: "Dr. Juan Pérez",
        estado: "Completado"
    }
];

// Función para registrar nueva vacunación
function registrarVacunacion() {
    Swal.fire({
        title: 'Registrar Nueva Vacunación',
        html: `
            <form id="formVacunacion" class="text-start">
                <div class="row g-3">
                    <div class="col-6">
                        <label class="form-label">ID Animal:</label>
                        <input type="text" id="idAnimal" class="form-control" required>
                    </div>
                    <div class="col-6">
                        <label class="form-label">Tipo de Vacuna:</label>
                        <select id="tipoVacuna" class="form-select" required>
                            <option value="">Seleccionar...</option>
                            <option>Brucelosis</option>
                            <option>Fiebre Aftosa</option>
                            <option>Tuberculosis</option>
                        </select>
                    </div>
                    <div class="col-6">
                        <label class="form-label">Fecha de Aplicación:</label>
                        <input type="date" id="fechaAplicacion" class="form-control" required>
                    </div>
                    <div class="col-6">
                        <label class="form-label">Próxima Dosis:</label>
                        <input type="date" id="proximaDosis" class="form-control" required>
                    </div>
                    <div class="col-12">
                        <label class="form-label">Responsable:</label>
                        <input type="text" id="responsable" class="form-control" required>
                    </div>
                    <div class="col-12">
                        <label class="form-label">Observaciones:</label>
                        <textarea id="observaciones" class="form-control" rows="3"></textarea>
                    </div>
                </div>
            </form>
        `,
        showCancelButton: true,
        confirmButtonText: 'Guardar',
        cancelButtonText: 'Cancelar',
        confirmButtonColor: '#00d563',
        preConfirm: () => {
            // Aquí irá la lógica de validación y guardado
            const datos = {
                idAnimal: document.getElementById('idAnimal').value,
                tipoVacuna: document.getElementById('tipoVacuna').value,
                fechaAplicacion: document.getElementById('fechaAplicacion').value,
                proximaDosis: document.getElementById('proximaDosis').value,
                responsable: document.getElementById('responsable').value,
                observaciones: document.getElementById('observaciones').value
            };
            return datos;
        }
    }).then((result) => {
        if (result.isConfirmed) {
            // Aquí irá la lógica para guardar en la base de datos
            Swal.fire({
                icon: 'success',
                title: 'Registro guardado',
                text: 'La vacunación ha sido registrada exitosamente'
            });
            cargarRegistros(); // Recargar la tabla
        }
    });
}

// Función para generar reporte
function generarReporte() {
    Swal.fire({
        title: 'Generar Reporte de Vacunación',
        html: `
            <div class="text-start">
                <div class="mb-3">
                    <label class="form-label">Periodo:</label>
                    <select class="form-select" id="periodo">
                        <option value="mes">Último mes</option>
                        <option value="trimestre">Último trimestre</option>
                        <option value="semestre">Último semestre</option>
                        <option value="año">Último año</option>
                    </select>
                </div>
                <div class="mb-3">
                    <label class="form-label">Formato:</label>
                    <select class="form-select" id="formato">
                        <option value="pdf">PDF</option>
                        <option value="excel">Excel</option>
                    </select>
                </div>
            </div>
        `,
        showCancelButton: true,
        confirmButtonText: 'Generar',
        cancelButtonText: 'Cancelar',
        confirmButtonColor: '#00d563'
    }).then((result) => {
        if (result.isConfirmed) {
            Swal.fire({
                icon: 'success',
                title: 'Reporte generado',
                text: 'El reporte se ha generado exitosamente',
                showConfirmButton: false,
                timer: 1500
            });
        }
    });
}

// Función para cargar los registros en la tabla
function cargarRegistros() {
    const tbody = document.querySelector('tbody');
    tbody.innerHTML = '';
    
    registrosVacunacion.forEach(registro => {
        tbody.innerHTML += `
            <tr>
                <td>${registro.idAnimal}</td>
                <td>${registro.nombre}</td>
                <td>${registro.tipoVacuna}</td>
                <td>${registro.fechaAplicacion}</td>
                <td>${registro.proximaDosis}</td>
                <td>${registro.responsable}</td>
                <td><span class="badge bg-success">${registro.estado}</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-primary me-1" onclick="verDetalle(${registro.id})">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-warning" onclick="editarRegistro(${registro.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                </td>
            </tr>
        `;
    });
}

// Cargar registros al iniciar
document.addEventListener('DOMContentLoaded', cargarRegistros);