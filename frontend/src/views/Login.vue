<template>
    <!-- Header con espaciado responsivo -->
    <nav class="navbar navbar-dark bg-success">
        <div class="container-fluid py-2 py-md-3 px-3 px-md-4">
            <a class="navbar-brand" href="{{ url_for('index') }}">
                <i class="fas fa-home me-2"></i>Inicio
            </a>
            <a class="navbar-brand mx-auto d-flex align-items-center" href="{{ url_for('index') }}">
                <span class="fw-bold fs-2">QR FARM</span>
                <i class="fas fa-cow ms-2 logo-icon"></i>
            </a>
            
            <div class="navbar-brand d-none d-md-block">
                <i class="fas fa-cow fa-2x"></i>
            </div>
        </div>
    </nav>

    <!-- Main Content con grid y espaciado mejorados -->
    <div class="container-fluid bg-light min-vh-100">
        <div class="row min-vh-100 align-items-center py-4 py-md-5">
            <div class="col-12 col-lg-10 col-xl-8 mx-auto">
                <div class="row g-0 bg-white rounded-4 shadow-lg overflow-hidden">
                    <!-- Left Side - Image and Description -->
                    <div class="col-12 col-md-6">
                        <div class="p-3 p-sm-4 p-lg-5 h-100 d-flex flex-column justify-content-center bg-white">
                            <div class="text-center mb-4">
                                <img src="/src/assets/images/vacas-grupo.jpg" alt="Grupo de vacas - QR Farm" />
                            </div>
                            <div class="text-center px-2 px-sm-3 px-md-4">
                                <p class="text-muted mb-2">Tu aliado inteligente en la gestión ganadera.</p>
                                <p class="text-muted mb-2">Simplifica el control de tu ganado, mejora la trazabilidad</p>
                                <p class="text-muted mb-2">y optimiza tus procesos con tecnología QR.</p>
                                <p class="text-muted fw-bold mb-0">¡Transforma tu finca hoy!</p>
                            </div>
                        </div>
                    </div>

                    <!-- Right Side - Login Form -->
                    <div class="col-12 col-md-6">
                        <div class="p-3 p-sm-4 p-lg-5 h-100 d-flex align-items-center bg-secondary">
                            <div class="w-100">
                                <div class="text-center mb-4">
                                    <i class="fas fa-user-circle fa-3x text-white mb-3"></i>
                                    <h4 class="text-white fw-bold">Inicio de Sesión</h4>
                                </div>

                                <form id="loginForm" method="POST" action="{{ url_for('iniciar_sesion') }}" class="px-0 px-sm-2 px-md-3">
                                    {% if error %}
                                    <div class="alert alert-danger text-center mb-3">{{ error }}</div>
                                    {% endif %}
                                    
                                    <div class="form-group mb-3">
                                        <input type="text" 
                                            class="form-control form-control-lg" 
                                            id="usuario" 
                                            name="usuario" 
                                            placeholder="Usuario" 
                                            required>
                                    </div>
                                    
                                    <div class="form-group mb-4">
                                        <input type="password" 
                                            class="form-control form-control-lg" 
                                            id="password" 
                                            name="password" 
                                            placeholder="Contraseña" 
                                            required>
                                    </div>
                                    
                                    <div class="d-grid gap-2 mb-3">
                                        <button type="submit" class="btn btn-success btn-lg fw-bold">
                                            Iniciar Sesión
                                        </button>
                                    </div>
                                    
                                    <div class="text-center">
                                        <p class="text-white mb-0">
                                            ¿No tienes cuenta? 
                                            <a href="{{ url_for('crear_cuenta') }}" 
                                               class="text-info fw-bold">
                                                Crear cuenta
                                            </a>
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
