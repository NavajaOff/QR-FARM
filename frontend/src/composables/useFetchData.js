// useFetchData.js - Hook reutilizable para manejo de datos con cancelación
import { ref, readonly, onUnmounted, nextTick } from 'vue'
import axios from 'axios'

export function useFetchData(fetchFunction, options = {}) {
  const {
    immediate = true,
    onSuccess = null,
    onError = null,
    keepDataOnUnmount = false,
    retryAttempts = 2,
    retryDelay = 1000
  } = options

  // Estados reactivos
  const data = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const isCancelled = ref(false)

  // Control de cancelación
  let abortController = null
  let cancelTokenSource = null

  // Función para cancelar peticiones
  const cancelRequest = () => {
    if (abortController) {
      abortController.abort()
      abortController = null
    }
    if (cancelTokenSource) {
      cancelTokenSource.cancel('Request cancelled by user navigation')
      cancelTokenSource = null
    }
    isCancelled.value = true
  }

  // Función para resetear estados
  const resetState = () => {
    if (!keepDataOnUnmount) {
      data.value = null
    }
    error.value = null
    isCancelled.value = false
  }

  // Función principal de carga con reintentos
  const loadData = async (params = {}) => {
    // Cancelar petición anterior si existe
    cancelRequest()

    // Crear nuevos controladores de cancelación
    abortController = new AbortController()
    cancelTokenSource = axios.CancelToken.source()

    loading.value = true
    error.value = null
    isCancelled.value = false

    for (let attempt = 0; attempt <= retryAttempts; attempt++) {
      try {
        console.log(`Intentando cargar datos (intento ${attempt + 1}/${retryAttempts + 1})...`)

        // Ejecutar la función de fetch con ambos métodos de cancelación
        const result = await fetchFunction({
          ...params,
          signal: abortController.signal,
          cancelToken: cancelTokenSource.token
        })

        // Verificar si fue cancelado después de la respuesta
        if (isCancelled.value) {
          console.log('Petición cancelada, ignorando respuesta')
          return
        }

        // Procesar respuesta exitosa
        data.value = result
        loading.value = false

        if (onSuccess) {
          onSuccess(result)
        }

        console.log('Datos cargados exitosamente')
        return result

      } catch (err) {

        // Si fue cancelado por el usuario, no es un error real
        if (axios.isCancel(err) || err.name === 'AbortError' || isCancelled.value) {
          console.log('Petición cancelada por navegación del usuario')
          loading.value = false
          return
        }

        // Si es el último intento, manejar el error
        if (attempt === retryAttempts) {
          console.error('Error cargando datos después de todos los reintentos:', err)
          error.value = err.message || 'Error desconocido'
          loading.value = false

          if (onError) {
            onError(err)
          }
        } else {
          // Esperar antes del siguiente intento
          console.log(`Reintentando en ${retryDelay}ms...`)
          await new Promise(resolve => setTimeout(resolve, retryDelay))
        }
      }
    }
  }

  // Función para recargar datos
  const reload = (params = {}) => {
    return loadData(params)
  }

  // Función para forzar recarga
  const forceReload = (params = {}) => {
    resetState()
    return loadData(params)
  }

  // Cleanup automático
  onUnmounted(() => {
    cancelRequest()
    if (!keepDataOnUnmount) {
      resetState()
    }
  })

  // Carga inicial si está configurada
  if (immediate) {
    nextTick(() => {
      loadData()
    })
  }

  return {
    // Estados
    data: readonly(data),
    loading: readonly(loading),
    error: readonly(error),

    // Métodos
    loadData,
    reload,
    forceReload,
    cancelRequest,
    resetState,

    // Utilidades
    isCancelled: readonly(isCancelled)
  }
}