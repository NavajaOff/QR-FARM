<template>
<div class="container-fluid py-3 py-md-4 py-lg-5">
        <div class="row justify-content-center g-4">
            <div class="col-12 col-lg-10">
                <!-- Título -->
                <div class="text-center mb-4 mb-md-5">
                    <h1 class="display-4 fw-bold text-success">
                        <i class="fas fa-phone-alt me-3"></i>Contáctanos
                    </h1>
                    <p class="lead text-muted">Estamos aquí para ayudarte con QR Farm</p>
                </div>

                <!-- Cards Container -->
                <div class="row g-4">
                    <!-- Contact Information -->
                    <div class="col-12 col-md-6">
                        <div class="card border-0 shadow-lg h-100">
                            <div class="card-body p-3 p-sm-4 p-md-5">
                                <h3 class="card-title text-success mb-4">
                                    <i class="fas fa-info-circle me-2"></i>Información de Contacto
                                </h3>
                                
                                <div class="contact-item mb-4">
                                    <div class="d-flex align-items-center mb-2">
                                        <i class="fas fa-map-marker-alt fa-lg text-success me-3"></i>
                                        <h5 class="mb-0">Dirección</h5>
                                    </div>
                                    <p class="text-muted ms-4">Calle 123 #45-67<br>Bogotá, Colombia</p>
                                </div>

                                <div class="contact-item mb-4">
                                    <div class="d-flex align-items-center mb-2">
                                        <i class="fas fa-phone fa-lg text-success me-3"></i>
                                        <h5 class="mb-0">Teléfono</h5>
                                    </div>
                                    <p class="text-muted ms-4">
                                        <a href="tel:+573001234567" class="text-decoration-none">+57 300 123 4567</a>
                                    </p>
                                </div>

                                <div class="contact-item mb-4">
                                    <div class="d-flex align-items-center mb-2">
                                        <i class="fas fa-envelope fa-lg text-success me-3"></i>
                                        <h5 class="mb-0">Email</h5>
                                    </div>
                                    <p class="text-muted ms-4">
                                        <a href="mailto:info@qrfarm.com" class="text-decoration-none">info@qrfarm.com</a>
                                    </p>
                                </div>

                                <div class="contact-item mb-4">
                                    <div class="d-flex align-items-center mb-2">
                                        <i class="fab fa-whatsapp fa-lg text-success me-3"></i>
                                        <h5 class="mb-0">WhatsApp</h5>
                                    </div>
                                    <p class="text-muted ms-4">
                                        <a href="https://wa.me/573001234567" target="_blank" class="text-decoration-none">+57 300 123 4567</a>
                                    </p>
                                </div>

                                <div class="mt-4">
                                    <h5 class="text-success mb-3">Síguenos en redes sociales</h5>
                                    <div class="social-links">
                                        <a href="#" class="btn btn-outline-success me-2 mb-2">
                                            <i class="fab fa-facebook-f"></i> Facebook
                                        </a>
                                        <a href="#" class="btn btn-outline-success me-2 mb-2">
                                            <i class="fab fa-twitter"></i> Twitter
                                        </a>
                                        <a href="#" class="btn btn-outline-success me-2 mb-2">
                                            <i class="fab fa-instagram"></i> Instagram
                                        </a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Contact Form -->
                    <div class="col-12 col-md-6">
                        <div class="card border-0 shadow-lg h-100">
                            <div class="card-body p-3 p-sm-4 p-md-5">
                                <h3 class="card-title text-success mb-4">
                                    <i class="fas fa-paper-plane me-2"></i>Envíanos un mensaje
                                </h3>
                                
                                <form id="contactForm">
                                    <div class="mb-3">
                                        <label for="nombre" class="form-label fw-bold">Nombre completo</label>
                                        <input type="text" class="form-control form-control-lg" id="nombre" name="nombre" required>
                                    </div>

                                    <div class="mb-3">
                                        <label for="email" class="form-label fw-bold">Email</label>
                                        <input type="email" class="form-control form-control-lg" id="email" name="email" required>
                                    </div>

                                    <div class="mb-3">
                                        <label for="telefono" class="form-label fw-bold">Teléfono</label>
                                        <input type="tel" class="form-control form-control-lg" id="telefono" name="telefono">
                                    </div>

                                    <div class="mb-3">
                                        <label for="asunto" class="form-label fw-bold">Asunto</label>
                                        <select class="form-select form-select-lg" id="asunto" name="asunto" required>
                                            <option value="">Selecciona un asunto</option>
                                            <option value="informacion">Información general</option>
                                            <option value="soporte">Soporte técnico</option>
                                            <option value="ventas">Consulta de ventas</option>
                                            <option value="demo">Solicitar demo</option>
                                            <option value="otro">Otro</option>
                                        </select>
                                    </div>

                                    <div class="mb-4">
                                        <label for="mensaje" class="form-label fw-bold">Mensaje</label>
                                        <textarea class="form-control" id="mensaje" name="mensaje" rows="5" required placeholder="Escribe tu mensaje aquí..."></textarea>
                                    </div>

                                    <div class="d-grid">
                                        <button type="submit" class="btn btn-success btn-lg fw-bold">
                                            <i class="fas fa-paper-plane me-2"></i>Enviar Mensaje
                                        </button>
                                    </div>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Quick Actions -->
                <div class="row g-3 mt-4">
                    <div class="col-12">
                        <div class="card border-0 shadow-lg bg-success text-white">
                            <div class="card-body p-3 p-sm-4">
                                <div class="row g-3 text-center">
                                    <div class="col-12 col-sm-6 col-md-4">
                                        <a href="tel:+573001234567" class="btn btn-light w-100">
                                            <i class="fas fa-phone text-success me-2"></i>
                                            <strong>Llamar Ahora</strong>
                                        </a>
                                    </div>
                                    <div class="col-12 col-sm-6 col-md-4">
                                        <a href="https://wa.me/573001234567" target="_blank" class="btn btn-light w-100">
                                            <i class="fab fa-whatsapp text-success me-2"></i>
                                            <strong>WhatsApp</strong>
                                        </a>
                                    </div>
                                    <div class="col-12 col-sm-6 col-md-4">
                                        <a href="mailto:info@qrfarm.com" class="btn btn-light w-100">
                                            <i class="fas fa-envelope text-success me-2"></i>
                                            <strong>Enviar Email</strong>
                                        </a>
                                    </div>
                                </div>
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
  name: 'Contacto',
};
</script>

<style scoped>
/* Puedes agregar estilos específicos aquí */
</style>
