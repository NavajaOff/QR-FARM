<template>
<nav class="navbar navbar-dark bg-success">
        <div class="container-fluid py-2 py-md-3 px-3 px-md-4">
            <a class="navbar-brand" href="{{ url_for('index') }}">
                <i class="fas fa-home me-2"></i>Inicio
            </a>
            <a class="navbar-brand mx-auto d-flex align-items-center" href="{{ url_for('index') }}">
                <span class="fw-bold fs-2">QR FARM</span>
                <i class="fas fa-cow ms-2 logo-icon"></i>
            </a>
            
            <div class="navbar-brand">
                <i class="fas fa-cow fa-2x"></i>
            </div>
        </div>
    </nav>

    <!-- Main Content -->
    <div class="container-fluid min-vh-100 bg-light-custom">
        <div class="row min-vh-100 align-items-center py-4 py-md-5">
            <div class="col-12 col-lg-10 col-xl-8 mx-auto">
                <div class="row g-0 bg-white rounded-4 shadow-lg overflow-hidden">
                    <!-- Left Side - Image -->
                    <div class="col-12 col-md-6">
                        <div class="p-3 p-sm-4 p-lg-5 h-100 d-flex flex-column justify-content-center">
                            <div class="text-center">
                                <img src="{{ url_for('static', filename='images/crear_cuenta.jpg') }}" 
                                     alt="Vacas Holstein - QR Farm" 
                                     class="img-fluid rounded-4 shadow-sm register-image">
                            </div>
                        </div>
                    </div>

                    <!-- Right Side - Registration Form -->
                    <div class="col-12 col-md-6">
                        <div class="p-3 p-sm-4 p-lg-5 h-100 d-flex align-items-center bg-form-register">
                            <div class="w-100">
                                <div class="text-center mb-4">
                                    <h3 class="text-white fw-bold">Crear una cuenta</h3>
                                    <p class="text-white-50">Es rápido y fácil</p>
                                </div>

                                <form id="registerForm" class="px-0 px-sm-2 px-md-3">
                                    <div class="row g-3 mb-3">
                                        <div class="col-6">
                                            <input type="text" class="form-control" id="primerNombre" name="primerNombre" placeholder="Primer Nombre" required>
                                        </div>
                                        <div class="col-6">
                                            <input type="text" class="form-control" id="segundoNombre" name="segundoNombre" placeholder="Segundo Nombre">
                                        </div>
                                    </div>

                                    <div class="row g-3 mb-3">
                                        <div class="col-6">
                                            <input type="text" class="form-control" id="primerApellido" name="primerApellido" placeholder="Primer Apellido" required>
                                        </div>
                                        <div class="col-6">
                                            <input type="text" class="form-control" id="segundoApellido" name="segundoApellido" placeholder="Segundo Apellido">
                                        </div>
                                    </div>

                                    <div class="row g-3 mb-3">
                                        <div class="col-6">
                                            <input type="text" class="form-control" id="direccion" name="direccion" placeholder="Dirección" required>
                                        </div>
                                        <div class="col-6">
                                            <input type="tel" class="form-control" id="telefono" name="telefono" placeholder="Número de teléfono" required>
                                        </div>
                                    </div>

                                    <div class="row g-3 mb-3">
                                        <div class="col-6">
                                            <input type="email" class="form-control" id="email" name="email" placeholder="Email" required>
                                        </div>
                                        <div class="col-6">
                                            <input type="password" class="form-control" id="password" name="password" placeholder="Contraseña" required>
                                        </div>
                                    </div>

                                    <div class="row g-3 mb-3">
                                        <div class="col-6">
                                            <select class="form-select" id="pais" name="pais" required>
                                                <option value="">Seleccionar País</option>
                                                <option value="colombia">Colombia</option>
                                                <option value="mexico">México</option>
                                                <option value="argentina">Argentina</option>
                                                <option value="chile">Chile</option>
                                                <option value="peru">Perú</option>
                                            </select>
                                        </div>
                                        <div class="col-6">
                                            <select class="form-select" id="tipoDocumento" name="tipoDocumento" required>
                                                <option value="">Tipo de Documento</option>
                                                <option value="cedula">Cédula de Ciudadanía</option>
                                                <option value="pasaporte">Pasaporte</option>
                                                <option value="cedula_extranjeria">Cédula de Extranjería</option>
                                            </select>
                                        </div>
                                    </div>

                                    <div class="row g-3 mb-3">
                                        <div class="col-6">
                                            <input type="text" class="form-control" id="numeroDocumento" name="numeroDocumento" placeholder="Número de documento" required>
                                        </div>
                                        <div class="col-6">
                                            <!-- Campo de código electrónico eliminado -->
                                        </div>
                                    </div>

                                    <div class="mb-3">
                                        <textarea class="form-control" id="observaciones" name="observaciones" rows="3" placeholder="Observaciones adicionales (opcional)"></textarea>
                                    </div>

                                    <div class="mb-3 form-check">
                                        <input type="checkbox" class="form-check-input" id="terminos" name="terminos" required>
                                        <label class="form-check-label text-white" for="terminos">
                                            Acepto los <a href="#" class="text-info">términos y condiciones</a> y la <a href="#" class="text-info">política de privacidad</a>
                                        </label>
                                    </div>

                                    <div class="d-grid">
                                        <button type="submit" class="btn btn-success btn-lg fw-bold">
                                            Crear Cuenta
                                        </button>
                                    </div>

                                    <div class="text-center mt-3">
                                        <p class="text-white">¿Ya tienes una cuenta? 
                                            <a href="{{ url_for('iniciar_sesion') }}" class="text-info fw-bold">Iniciar Sesión</a>
                                        </p>
                                    </div>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
  name: 'CrearCuenta',
};
</script>

<style scoped>
/* Puedes agregar estilos específicos aquí */
</style>
