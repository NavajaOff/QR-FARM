// Import SweetAlert2 library
const Swal = window.Swal
// Import Bootstrap library
const bootstrap = window.bootstrap

function handleContactClick() {
  console.log("Contacto clickeado")

  Swal.fire({
    title: '<i class="fas fa-phone-alt"></i> Contáctanos',
    html: `
            <div style="text-align: left; margin: 20px 0;">
                <p><i class="fas fa-phone" style="color: #00d563; margin-right: 10px;"></i> 
                   <strong>Teléfono:</strong> +57 300 123 4567</p>
                <p><i class="fas fa-envelope" style="color: #00d563; margin-right: 10px;"></i> 
                   <strong>Email:</strong> info@qrfarm.com</p>
                <p><i class="fas fa-map-marker-alt" style="color: #00d563; margin-right: 10px;"></i> 
                   <strong>Dirección:</strong> Calle 123 #45-67, Bogotá, Colombia</p>
                <p><i class="fab fa-whatsapp" style="color: #25D366; margin-right: 10px;"></i> 
                   <strong>WhatsApp:</strong> +57 300 123 4567</p>
            </div>
        `,
    showCancelButton: true,
    confirmButtonText: '<i class="fas fa-phone"></i> Llamar Ahora',
    cancelButtonText: '<i class="fas fa-times"></i> Cerrar',
    confirmButtonColor: "#00d563",
    cancelButtonColor: "#6c757d",
    width: "500px",
  }).then((result) => {
    if (result.isConfirmed) {
      // Simular llamada telefónica
      window.open("tel:+573001234567")
    }
  })
}

function handleLoginClick() {
  console.log("Iniciar Sesión clickeado")

  Swal.fire({
    title: '<i class="fas fa-sign-in-alt"></i> Iniciar Sesión',
    text: "¿Deseas ir a la página de inicio de sesión?",
    icon: "question",
    showCancelButton: true,
    confirmButtonText: '<i class="fas fa-arrow-right"></i> Continuar',
    cancelButtonText: '<i class="fas fa-times"></i> Cancelar',
    confirmButtonColor: "#00d563",
    cancelButtonColor: "#6c757d",
  }).then((result) => {
    if (result.isConfirmed) {
      // Mostrar loading antes de redirigir
      Swal.fire({
        title: "Redirigiendo...",
        html: '<i class="fas fa-spinner fa-spin"></i> Cargando página de inicio de sesión',
        showConfirmButton: false,
        allowOutsideClick: false,
        timer: 1500,
      }).then(() => {
        window.location.href = "/iniciar_sesion"
      })
    }
  })
}

// Función para mostrar notificaciones de bienvenida
function showWelcomeNotification() {
  const Toast = Swal.mixin({
    toast: true,
    position: "top-end",
    showConfirmButton: false,
    timer: 3000,
    timerProgressBar: true,
    didOpen: (toast) => {
      toast.addEventListener("mouseenter", Swal.stopTimer)
      toast.addEventListener("mouseleave", Swal.resumeTimer)
    },
  })

  Toast.fire({
    icon: "success",
    title: "¡Bienvenido a QR Farm!",
    text: "Tu aliado en gestión ganadera",
  })
}

// Función para mostrar información sobre QR Farm
function showAboutInfo() {
  Swal.fire({
    title: '<i class="fas fa-info-circle"></i> Acerca de QR Farm',
    html: `
            <div style="text-align: left;">
                <h4><i class="fas fa-cow" style="color: #00d563;"></i> ¿Qué es QR Farm?</h4>
                <p>QR Farm es una plataforma innovadora que revoluciona la gestión ganadera mediante tecnología QR.</p>
                
                <h4><i class="fas fa-check-circle" style="color: #00d563;"></i> Beneficios:</h4>
                <ul>
                    <li><i class="fas fa-qrcode"></i> Identificación única por animal</li>
                    <li><i class="fas fa-chart-line"></i> Seguimiento en tiempo real</li>
                    <li><i class="fas fa-mobile-alt"></i> Acceso desde cualquier dispositivo</li>
                    <li><i class="fas fa-shield-alt"></i> Datos seguros y confiables</li>
                </ul>
            </div>
        `,
    confirmButtonText: '<i class="fas fa-thumbs-up"></i> ¡Entendido!',
    confirmButtonColor: "#00d563",
    width: "600px",
  })
}

// Función para validar formularios con SweetAlert
function validateFormWithAlert(formData) {
  const validation = validateForm(formData)

  if (!validation.isValid) {
    Swal.fire({
      icon: "error",
      title: '<i class="fas fa-exclamation-triangle"></i> Error de Validación',
      html: `
                <div style="text-align: left;">
                    <p>Se encontraron los siguientes errores:</p>
                    <ul>
                        ${validation.errors.map((error) => `<li><i class="fas fa-times-circle" style="color: #dc3545;"></i> ${error}</li>`).join("")}
                    </ul>
                </div>
            `,
      confirmButtonText: '<i class="fas fa-edit"></i> Corregir',
      confirmButtonColor: "#dc3545",
    })
    return false
  }

  return true
}

document.addEventListener("DOMContentLoaded", () => {
  console.log("El DOM está listo!")

  // Ejemplo de validación
  const formulario = document.getElementById("miFormulario")
  if (formulario) {
    formulario.addEventListener("submit", (event) => {
      event.preventDefault() // Evita el envío normal del formulario

      const formData = {
        nombre: document.getElementById("nombre").value,
        email: document.getElementById("email").value,
        edad: document.getElementById("edad").value,
      }

      if (validateFormWithAlert(formData)) {
        console.log("Formulario válido, listo para enviar:", formData)
        // Aquí iría el código para enviar el formulario
      } else {
        console.log("Formulario inválido, revisa los errores.")
      }
    })
  }

  setTimeout(showWelcomeNotification, 1000)
})

function validateForm(formData) {
  const errors = []

  if (!formData.nombre) {
    errors.push("El nombre es obligatorio.")
  }

  if (!formData.email) {
    errors.push("El email es obligatorio.")
  } else if (!isValidEmail(formData.email)) {
    errors.push("El email no tiene un formato válido.")
  }

  if (isNaN(formData.edad) || formData.edad === "") {
    errors.push("La edad debe ser un número.")
  }

  return {
    isValid: errors.length === 0,
    errors: errors,
  }
}

function isValidEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

window.QRFarm = {
  validateForm,
  validateFormWithAlert,
  isValidEmail,
  handleContactClick,
  handleLoginClick,
  showAboutInfo,
  showWelcomeNotification,
}

// Función para mostrar modal de demo
function showDemoModal() {
  Swal.fire({
    title: '<i class="fas fa-play-circle"></i> Demo de QR Farm',
    html: `
      <div class="text-start">
        <h5><i class="fas fa-mobile-alt text-success"></i> Funcionalidades principales:</h5>
        <div class="row mt-3">
          <div class="col-6">
            <ul class="list-unstyled">
              <li><i class="fas fa-check text-success"></i> Scanner QR</li>
              <li><i class="fas fa-check text-success"></i> Registro de animales</li>
              <li><i class="fas fa-check text-success"></i> Historial médico</li>
            </ul>
          </div>
          <div class="col-6">
            <ul class="list-unstyled">
              <li><i class="fas fa-check text-success"></i> Reportes automáticos</li>
              <li><i class="fas fa-check text-success"></i> Alertas inteligentes</li>
              <li><i class="fas fa-check text-success"></i> Sincronización en la nube</li>
            </ul>
          </div>
        </div>
        <div class="alert alert-success mt-3" role="alert">
          <i class="fas fa-gift"></i> <strong>¡Prueba gratuita por 30 días!</strong>
        </div>
      </div>
    `,
    showCancelButton: true,
    confirmButtonText: '<i class="fas fa-rocket"></i> Iniciar Prueba Gratuita',
    cancelButtonText: '<i class="fas fa-times"></i> Cerrar',
    confirmButtonColor: "#00d563",
    cancelButtonColor: "#6c757d",
    width: "600px",
  }).then((result) => {
    if (result.isConfirmed) {
      showRegistrationForm()
    }
  })
}

// Función para mostrar formulario de registro rápido
function showRegistrationForm() {
  Swal.fire({
    title: '<i class="fas fa-user-plus"></i> Registro Rápido',
    html: `
      <form id="quickRegisterForm" class="text-start">
        <div class="mb-3">
          <label for="nombre" class="form-label">Nombre completo</label>
          <input type="text" class="form-control" id="nombre" required>
        </div>
        <div class="mb-3">
          <label for="email" class="form-label">Email</label>
          <input type="email" class="form-control" id="email" required>
        </div>
        <div class="mb-3">
          <label for="telefono" class="form-label">Teléfono</label>
          <input type="tel" class="form-control" id="telefono" required>
        </div>
        <div class="mb-3">
          <label for="finca" class="form-label">Nombre de la finca</label>
          <input type="text" class="form-control" id="finca" required>
        </div>
      </form>
    `,
    showCancelButton: true,
    confirmButtonText: '<i class="fas fa-paper-plane"></i> Enviar Registro',
    cancelButtonText: '<i class="fas fa-arrow-left"></i> Volver',
    confirmButtonColor: "#00d563",
    cancelButtonColor: "#6c757d",
    width: "500px",
    preConfirm: () => {
      const form = document.getElementById("quickRegisterForm")
      const formData = new FormData(form)

      // Validar campos
      if (!form.checkValidity()) {
        Swal.showValidationMessage("Por favor completa todos los campos")
        return false
      }

      return {
        nombre: document.getElementById("nombre").value,
        email: document.getElementById("email").value,
        telefono: document.getElementById("telefono").value,
        finca: document.getElementById("finca").value,
      }
    },
  }).then((result) => {
    if (result.isConfirmed) {
      // Simular envío de registro
      Swal.fire({
        icon: "success",
        title: "¡Registro Exitoso!",
        html: `
          <p>Gracias <strong>${result.value.nombre}</strong></p>
          <p>Te hemos enviado un email a <strong>${result.value.email}</strong> con las instrucciones para activar tu cuenta.</p>
          <div class="alert alert-info mt-3">
            <i class="fas fa-info-circle"></i> Revisa tu bandeja de entrada y spam
          </div>
        `,
        confirmButtonText: '<i class="fas fa-envelope-open"></i> Entendido',
        confirmButtonColor: "#00d563",
      })
    }
  })
}

// Inicializar tooltips de Bootstrap y animación de contadores
document.addEventListener("DOMContentLoaded", () => {
  // Inicializar tooltips
  var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
  var tooltipList = tooltipTriggerList.map((tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl))

  // Animación de contadores en la sección de estadísticas
  const observerOptions = {
    threshold: 0.5,
  }

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        animateCounters()
        observer.unobserve(entry.target)
      }
    })
  }, observerOptions)

  const statsSection = document.querySelector(".bg-success")
  if (statsSection) {
    observer.observe(statsSection)
  }
})

// Función para animar contadores
function animateCounters() {
  const counters = [
    { element: document.querySelector(".stat-item:nth-child(1) h3"), target: 500, suffix: "+" },
    { element: document.querySelector(".stat-item:nth-child(2) h3"), target: 10000, suffix: "+" },
    { element: document.querySelector(".stat-item:nth-child(3) h3"), target: 50000, suffix: "+" },
    { element: document.querySelector(".stat-item:nth-child(4) h3"), target: 99.9, suffix: "%" },
  ]

  counters.forEach((counter) => {
    if (counter.element) {
      animateCounter(counter.element, counter.target, counter.suffix)
    }
  })
}

function animateCounter(element, target, suffix) {
  let current = 0
  const increment = target / 100
  const timer = setInterval(() => {
    current += increment
    if (current >= target) {
      current = target
      clearInterval(timer)
    }
    element.textContent = Math.floor(current) + suffix
  }, 20)
}

// Actualizar el objeto global
window.QRFarm = {
  ...window.QRFarm,
  showDemoModal,
  showRegistrationForm,
  animateCounters,
}

// Función para mostrar detalles de características
function showFeatureDetail(feature) {
  const features = {
    qr: {
      title: '<i class="fas fa-qrcode"></i> Identificación QR',
      content: `
        <div class="text-start">
          <h5>Características principales:</h5>
          <ul>
            <li><i class="fas fa-check text-success"></i> Códigos QR únicos por animal</li>
            <li><i class="fas fa-check text-success"></i> Información completa del historial</li>
            <li><i class="fas fa-check text-success"></i> Acceso instantáneo desde móvil</li>
            <li><i class="fas fa-check text-success"></i> Resistente a condiciones climáticas</li>
          </ul>
          <div class="alert alert-info">
            <i class="fas fa-lightbulb"></i> <strong>Tip:</strong> Los códigos QR se pueden imprimir en etiquetas resistentes al agua
          </div>
        </div>
      `,
    },
    analytics: {
      title: '<i class="fas fa-chart-line"></i> Análisis en Tiempo Real',
      content: `
        <div class="text-start">
          <h5>Métricas disponibles:</h5>
          <ul>
            <li><i class="fas fa-heartbeat text-danger"></i> Estado de salud</li>
            <li><i class="fas fa-weight text-primary"></i> Control de peso</li>
            <li><i class="fas fa-calendar text-warning"></i> Ciclos reproductivos</li>
            <li><i class="fas fa-syringe text-info"></i> Historial de vacunación</li>
          </ul>
          <div class="alert alert-success">
            <i class="fas fa-chart-bar"></i> <strong>Reportes automáticos</strong> cada semana por email
          </div>
        </div>
      `,
    },
    mobile: {
      title: '<i class="fas fa-mobile-alt"></i> Acceso Móvil',
      content: `
        <div class="text-start">
          <h5>Funcionalidades móviles:</h5>
          <ul>
            <li><i class="fas fa-camera text-primary"></i> Scanner QR integrado</li>
            <li><i class="fas fa-cloud text-info"></i> Sincronización automática</li>
            <li><i class="fas fa-bell text-warning"></i> Notificaciones push</li>
            <li><i class="fas fa-map-marker-alt text-danger"></i> Geolocalización de animales</li>
          </ul>
          <div class="alert alert-primary">
            <i class="fab fa-android"></i> <i class="fab fa-apple"></i> Disponible para Android e iOS
          </div>
        </div>
      `,
    },
  }

  const feature_data = features[feature]

  Swal.fire({
    title: feature_data.title,
    html: feature_data.content,
    confirmButtonText: '<i class="fas fa-thumbs-up"></i> ¡Genial!',
    confirmButtonColor: "#00d563",
    width: "600px",
  })
}

// Actualizar el objeto global
window.QRFarm = {
  ...window.QRFarm,
  showFeatureDetail,
}
