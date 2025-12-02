# Análisis de Cobertura - QR-Farm

## Resumen Ejecutivo

**Cobertura Actual:** 79.19% (Frontend)  
**Objetivo:** 80%+  
**Gap:** ~0.81%

## Archivos con Peor Cobertura

### 1. QrScanner.vue - 33.23% (111/334 líneas)
**Impacto:** Alto (334 líneas, 223 no cubiertas)  
**Líneas no cubiertas:** 246-262, 260-262, 312-313, 331, 336, etc.  
**Ramas no cubiertas:** Múltiples condiciones en manejo de errores, estados de cámara, y callbacks

**Recomendaciones:**
- Agregar tests para estados de error de cámara (líneas 246-262)
- Cubrir callbacks de escaneo fallidos (líneas 312-313)
- Testear manejo de permisos de cámara denegados
- Cubrir casos de archivo inválido en upload

### 2. gestionar_animales.js - 41.55% (150/361 líneas)
**Impacto:** Muy Alto (361 líneas, 211 no cubiertas)  
**Líneas no cubiertas:** 8-9, 11-12, 20, 26-27, 30, 38, 45, etc.  
**Ramas no cubiertas:** Validaciones, manejo de errores, casos edge

**Recomendaciones:**
- Cubrir validaciones de datos inválidos (líneas 8-9, 11-12)
- Testear manejo de errores en actualización (líneas 26-27, 30)
- Agregar tests para casos con datos null/undefined (línea 38, 45)

### 3. GestionarUsuarios.vue - 57.33% (43/75 líneas)
**Impacto:** Medio (75 líneas, 32 no cubiertas)  
**Líneas no cubiertas:** 7, 44, 51, 73, 76, 84, 94, 105, 115, 126  
**Ramas no cubiertas:** Condiciones de renderizado, manejo de errores

**Recomendaciones:**
- Testear renderizado condicional (líneas 7, 44, 51)
- Cubrir manejo de errores en operaciones CRUD (líneas 73, 76, 84)
- Agregar tests para estados de carga y error (líneas 94, 105, 115, 126)

### 4. RegistroVacunacionAdmin.vue - 58.62% (17/29 líneas)
**Impacto:** Bajo (29 líneas, 12 no cubiertas)  
**Líneas no cubiertas:** 13, 16, 28, 32, 34, 39, 43, 77-79  
**Ramas no cubiertas:** Condiciones de validación y renderizado

**Recomendaciones:**
- Testear validaciones de formulario (líneas 13, 16, 28)
- Cubrir renderizado condicional (líneas 32, 34, 39, 43)
- Agregar tests para manejo de errores (líneas 77-79)

### 5. gestionar-potreros.js - 60.89% (151/248 líneas)
**Impacto:** Alto (248 líneas, 97 no cubiertas)  
**Líneas no cubiertas:** 6-8, 10-13, 15-17, etc.  
**Ramas no cubiertas:** Validaciones, manejo de errores, casos edge

**Recomendaciones:**
- Cubrir validaciones iniciales (líneas 6-8, 10-13)
- Testear manejo de errores en operaciones (líneas 15-17)
- Agregar tests para casos con datos inválidos

## Líneas Específicas No Cubiertas (Prioridad Alta)

### dashboard-content-usuario.js
- **Líneas 24-25:** `mounted()` hook - llamadas a `cargarDatosUsuario()` y `cargarEstadisticas()`
  - **Solución:** Test que monte el componente y verifique que se llaman estos métodos
  - **Estado:** ✅ Test agregado

### dashboard-content.js
- **Línea 8:** `return lower;` en `secureRandomInt` cuando parámetros son inválidos
  - **Solución:** Tests con `min`/`max` inválidos (NaN, Infinity, lower > upper)
  - **Estado:** ✅ Tests agregados

## Ramas No Cubiertas (Prioridad Alta)

### dashboard-content-usuario.js
- **Línea 33, rama 0:** `if (user?.persona)` - cuando `user` es null/undefined
  - **Solución:** Test con `user = null` o `user = undefined`
  - **Estado:** ✅ Ya cubierto

- **Línea 50-52, ramas:** Acceso opcional a `data?.data?.length`
  - **Solución:** Tests con respuestas sin `data` o con `data.data = null`
  - **Estado:** ✅ Ya cubierto

### dashboard-content.js
- **Línea 7, rama 0:** `if (!Number.isFinite(lower) || !Number.isFinite(upper) || lower > upper)`
  - **Solución:** Tests con parámetros inválidos
  - **Estado:** ✅ Tests agregados

- **Línea 11, rama 0:** `if (globalThis.window?.crypto?.getRandomValues)` - cuando crypto no está disponible
  - **Solución:** Test con `window.crypto = undefined`
  - **Estado:** ✅ Ya cubierto

## Tests Creados

### dashboard-content-usuario.spec.js
1. ✅ Test para `mounted()` hook que verifica llamadas a métodos
   - Cubre líneas 24-25

### dashboard-content.spec.js
1. ✅ Tests para `secureRandomInt` con parámetros inválidos
   - Cubre línea 8 (return lower cuando parámetros inválidos)
   - Tests para: min no finito, max no finito, lower > upper

## Estimación de Impacto

### Cobertura Esperada Después de Tests
- **dashboard-content-usuario.js:** De 85.71% a ~92% (+6.29%)
- **dashboard-content.js:** De 99.12% a 100% (+0.88%)

### Impacto Global Estimado
- **Cobertura actual:** 79.19%
- **Cobertura esperada:** ~79.5-80%
- **Incremento:** ~0.3-0.8%

## Recomendaciones Adicionales

### Para Alcanzar 80%+

1. **Priorizar QrScanner.vue** (mayor impacto)
   - Agregar tests para manejo de errores de cámara
   - Cubrir estados de escaneo fallido
   - Testear permisos denegados

2. **Mejorar gestionar_animales.js**
   - Cubrir validaciones y casos edge
   - Testear manejo de errores en todas las operaciones

3. **Completar GestionarUsuarios.vue**
   - Testear renderizado condicional
   - Cubrir todos los casos de error

### Mejoras de Código Sugeridas

1. **Extraer lógica compleja a funciones testables**
   - `secureRandomInt` ya está extraída ✅
   - Considerar extraer validaciones de `gestionar_animales.js`

2. **Simplificar condiciones anidadas**
   - Reducir complejidad ciclomática en `QrScanner.vue`
   - Usar early returns donde sea posible

3. **Agregar validaciones defensivas**
   - Verificar null/undefined antes de acceder a propiedades
   - Usar optional chaining consistentemente

## Configuración de SonarQube

✅ **Configuración mejorada:**
- `sonar.sources`: Solo código fuente de producción
- `sonar.tests`: Ubicación de archivos de test
- `sonar.exclusions`: Excluye tests del análisis de código fuente
- `sonar.test.inclusions`: Identifica archivos de test
- `sonar.coverage.exclusions`: Excluye tests de la cobertura

**Resultado:** SonarQube ahora mide cobertura solo del código fuente real, excluyendo archivos de test.

## Próximos Pasos

1. ✅ Mejorar configuración de SonarQube
2. ✅ Agregar tests para líneas críticas identificadas
3. ⏳ Ejecutar tests y verificar cobertura
4. ⏳ Priorizar archivos con mayor impacto para alcanzar 80%
5. ⏳ Continuar agregando tests para archivos con peor cobertura

