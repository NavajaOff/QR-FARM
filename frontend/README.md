# Escáner de códigos QR

Este frontend Vue 3 incluye ahora el componente reutilizable `QrScanner.vue`, compatible con rutas `/admin/scan-qr` y `/user/scan-qr`. El escáner activa la cámara del dispositivo, detecta códigos QR mediante `html5-qrcode` y consulta el backend para mostrar la información del recurso sin abandonar la página.

## Integración en rutas

- Administrador: `frontend/src/views/admin/EscanearQRAdmin.vue` usa `<QrScanner role="admin" resource-endpoint="/ganado/{id}" />`.
- Usuario: `frontend/src/views/user/EscanearQRUsuario.vue` usa `<QrScanner role="user" resource-endpoint="/ganado/{id}" />`.
- Las rutas están declaradas en `frontend/src/router/index.js`.

## Endpoint esperado

El componente espera que el backend exponga `GET /api/ganado/{id}` con la siguiente estructura:

```json
{
  "id": 1,
  "nombre": "Lola",
  "raza": "Cebú",
  "sexo": "hembra",
  "fecha_nacimiento": "2021-06-12T00:00:00Z",
  "estado": "saludable",
  "estado_salud": "Libre de enfermedades",
  "peso": 450,
  "codigo_qr": "QR_1_Lola",
  "propietario": {
    "nombre": "JOSE DAVID HERNANDEZ NAVAJA",
    "telefono": "3212302504",
    "rol": "admin"
  },
  "potrero": {
    "nombre": "Potrero 3",
    "tipo_pasto": "Brachiaria",
    "ultima_limpieza": "2025-10-12T07:30:00Z",
    "fecha_ultimo_uso": "2025-11-05T14:00:00Z",
    "proxima_limpieza": "2025-12-01T08:00:00Z",
    "capacidad": 40,
    "estado": "disponible"
  },
  "vacunas": [
    { "id": 10, "nombre": "Fiebre Aftosa", "fecha_aplicacion": "2025-05-20T00:00:00Z", "proxima_dosis": "2026-05-20T00:00:00Z", "responsable": "Carlos Ruiz", "estado": "aplicado" }
  ],
  "historial": [
    { "id": 3, "fecha": "2025-09-15T00:00:00Z", "observaciones": "Buen estado general", "resultado": "Sin anomalías", "veterinario": "Carlos Ruiz" }
  ]
}
```

El backend ya expone esta estructura mediante `GanadoService.obtener_ganado_detallado`.

## QR con datos embebidos

- Cada QR generado incluye un payload JSON con la estructura `schema: "qr-farm.v1"` que contiene datos básicos del ganado (ID, nombre, propietario, potrero, estado y URL).
- Define la variable de entorno `QR_FARM_WEB_URL` (o `QR_FARM_FRONTEND_URL`) en el backend para que el QR apunte a la ficha en línea correcta.
- El QR mantiene compatibilidad con códigos antiguos: si solo incluye texto, el escáner extrae el ID y consulta la API como antes.

## Flujo offline / online

- Si el QR aporta el JSON embebido y el navegador está sin conexión, `QrScanner.vue` renderiza la tarjeta con esa información inmediata.
- Cuando hay conexión, el escáner muestra los datos embebidos y sincroniza con la API; si la actualización falla, se mantiene la información offline y se muestra una alerta suave.
- Si el QR no incluye datos embebidos y no hay conexión, se informa claramente al usuario que no es posible obtener la información.

## Pruebas manuales

1. **Permisos**: al entrar por primera vez al escáner, aceptar el acceso a la cámara.
2. **Dispositivos**: probar en iPhone (Safari), Android (Chrome) y escritorio (Chrome/Firefox con webcam).
3. **Escenarios**:
   - QR con JSON `{ "id": 123 }`.
   - QR con texto `ID:123`.
   - QR con URL (el componente avisa si no contiene ID).
   - Fallback cargando una imagen (`Subir imagen (fallback)`).
4. **Errores esperados**:
   - 404 → “QR no reconocido. Verifica que el código exista.”
   - 403 → “No autorizado para consultar este recurso.”
   - 500 → “Error del servidor al consultar el recurso.”

## Requisitos de permisos

- Cámara: `navigator.mediaDevices.getUserMedia({ video: true })`.
- HTTPS recomendado para habilitar cámaras en móviles.
- Token JWT enviado automáticamente por `src/services/api.js` en el encabezado `Authorization`.

## Telemetría

El componente registra en consola todos los intentos de lectura (exitosos y fallidos) y conserva un historial visible en la interfaz para auditoría básica. Para extenderlo, envía los eventos capturados en `QrScanner.vue` al backend.

## Tarjeta detallada del ganado

- La información se presenta en `GanadoDetailCard.vue` con pestañas: **Información general**, **Potrero**, **Vacunas** y **Historial**.
- Cada sección incluye íconos de FontAwesome, disposición responsive (grid en escritorio, bloques en móvil) y mensajes amigables cuando faltan datos.
- Las dosis próximas a vencer (<= 10 días) y vencidas se resaltan con chips de color.
- El botón `Volver a escanear` reactiva la cámara sin recargar la vista; acciones extra (`Ver historial completo`, `Descargar ficha`) se emiten hacia la vista que consume el componente.
- Cuando los datos provienen del QR (modo offline) se muestra un banner amarillo. Si hay conexión, el botón **Actualizar datos** sincroniza la ficha con `/api/ganado/{id}`.

## Modo offline

- El backend genera QR con un payload JSON `qr-farm.v1` que incluye datos esenciales (ID, nombre, estado, propietario, potrero, peso, URL).
- `QrScanner.vue` detecta este payload embebido y muestra la ficha sin necesidad de una llamada HTTP cuando `navigator.onLine === false`.
- Al recuperar la conexión, el sistema intenta sincronizar automáticamente; el usuario también puede forzar la actualización desde la tarjeta.
- Los QR antiguos que contienen solo la URL siguen funcionando: el escáner extrae el ID numérico de la ruta y consulta la API como antes.
