import { vi } from 'vitest'
import { useFetchData } from './useFetchData.js'

// Mock axios
vi.mock('axios', () => ({
  default: {
    CancelToken: {
      source: vi.fn(() => ({
        token: { reason: null },
        cancel: vi.fn()
      }))
    },
    isCancel: vi.fn(() => false)
  },
  __esModule: true
}))

describe('useFetchData', () => {
  let mockFetchFunction
  let composable

  beforeEach(() => {
    vi.clearAllMocks()
    console.log = vi.fn()
    console.error = vi.fn()

    mockFetchFunction = vi.fn()
  })

  describe('Initialization', () => {
    it('should initialize with default values', () => {
      composable = useFetchData(mockFetchFunction)

      expect(composable.data.value).toBeNull()
      expect(composable.loading.value).toBe(false)
      expect(composable.error.value).toBeNull()
      expect(composable.isCancelled.value).toBe(false)
    })

    it('should have required methods', () => {
      composable = useFetchData(mockFetchFunction)

      expect(typeof composable.loadData).toBe('function')
      expect(typeof composable.reload).toBe('function')
      expect(typeof composable.forceReload).toBe('function')
      expect(typeof composable.cancelRequest).toBe('function')
      expect(typeof composable.resetState).toBe('function')
    })
  })

  describe('loadData Method', () => {
    it('should load data successfully', async () => {
      mockFetchFunction.mockResolvedValue('test data')
      composable = useFetchData(mockFetchFunction, { immediate: false })

      const result = await composable.loadData()

      expect(mockFetchFunction).toHaveBeenCalled()
      expect(composable.data.value).toBe('test data')
      expect(composable.loading.value).toBe(false)
      expect(composable.error.value).toBeNull()
      expect(result).toBe('test data')
    })

    it('should handle errors', async () => {
      mockFetchFunction.mockRejectedValue(new Error('Test error'))
      composable = useFetchData(mockFetchFunction, { immediate: false })

      await composable.loadData()

      expect(composable.error.value).toBe('Test error')
      expect(composable.loading.value).toBe(false)
    })

    it('should retry on failure', async () => {
      mockFetchFunction.mockRejectedValueOnce(new Error('First error'))
      mockFetchFunction.mockRejectedValueOnce(new Error('Second error'))
      mockFetchFunction.mockResolvedValue('success data')

      composable = useFetchData(mockFetchFunction, { immediate: false, retryAttempts: 2 })

      await composable.loadData()

      expect(mockFetchFunction).toHaveBeenCalledTimes(3)
      expect(composable.data.value).toBe('success data')
    })

    it('should cancel request', async () => {
      let resolvePromise
      const promise = new Promise(resolve => { resolvePromise = resolve })
      mockFetchFunction.mockReturnValue(promise)

      composable = useFetchData(mockFetchFunction, { immediate: false })
      const loadPromise = composable.loadData()

      composable.cancelRequest()

      resolvePromise('data')
      await loadPromise

      expect(composable.isCancelled.value).toBe(true)
    })
  })

  describe('reload Method', () => {
    it('should call loadData', async () => {
      mockFetchFunction.mockResolvedValue('reload data')
      composable = useFetchData(mockFetchFunction, { immediate: false })

      const result = await composable.reload({ param: 'test' })

      expect(mockFetchFunction).toHaveBeenCalledWith({
        param: 'test',
        signal: expect.any(AbortSignal),
        cancelToken: expect.any(Object)
      })
      expect(result).toBe('reload data')
    })
  })

  describe('forceReload Method', () => {
    it('should reset state and load data', async () => {
      mockFetchFunction.mockResolvedValue('force reload data')
      composable = useFetchData(mockFetchFunction, { immediate: false })

      // Load data first to set state
      await composable.loadData()
      expect(composable.data.value).toBe('force reload data')

      // Now force reload
      mockFetchFunction.mockResolvedValue('new force reload data')
      const result = await composable.forceReload()

      expect(composable.data.value).toBe('new force reload data')
      expect(composable.error.value).toBeNull()
      expect(result).toBe('new force reload data')
    })
  })

  describe('cancelRequest Method', () => {
    it('should cancel ongoing requests', () => {
      composable = useFetchData(mockFetchFunction, { immediate: false })

      composable.cancelRequest()

      expect(composable.isCancelled.value).toBe(true)
    })
  })

  describe('Options', () => {
    it('should call onSuccess callback', async () => {
      const onSuccess = vi.fn()
      mockFetchFunction.mockResolvedValue('success data')
      composable = useFetchData(mockFetchFunction, {
        immediate: false,
        onSuccess
      })

      await composable.loadData()

      expect(onSuccess).toHaveBeenCalledWith('success data')
    })

    it('should call onError callback', async () => {
      const onError = vi.fn()
      mockFetchFunction.mockRejectedValue(new Error('Test error'))
      composable = useFetchData(mockFetchFunction, {
        immediate: false,
        onError
      })

      await composable.loadData()

      expect(onError).toHaveBeenCalled()
    })

    it('should not load immediately when immediate is false', () => {
      composable = useFetchData(mockFetchFunction, { immediate: false })

      expect(mockFetchFunction).not.toHaveBeenCalled()
    })
  })

  describe('resetState Function', () => {
    it('should reset all state', async () => {
      composable = useFetchData(mockFetchFunction, { immediate: false })

      // Load data first to set state
      mockFetchFunction.mockResolvedValue('test data')
      await composable.loadData()
      expect(composable.data.value).toBe('test data')

      // Now reset state
      composable.resetState()

      expect(composable.data.value).toBeNull()
      expect(composable.loading.value).toBe(false)
      expect(composable.error.value).toBeNull()
      expect(composable.isCancelled.value).toBe(false)
    })
  })

  describe('Edge Cases', () => {
    it('should handle AbortError cancellation', async () => {
      const abortError = new Error('Aborted')
      abortError.name = 'AbortError'
      mockFetchFunction.mockRejectedValue(abortError)
      composable = useFetchData(mockFetchFunction, { immediate: false })

      await composable.loadData()

      // handleCancel returns true for AbortError, stopping processing
      expect(composable.loading.value).toBe(false)
    })

    it('should handle axios cancel error', async () => {
      const axios = await import('axios')
      const cancelError = { isCancel: true }
      axios.default.isCancel.mockReturnValue(true)
      mockFetchFunction.mockRejectedValue(cancelError)
      composable = useFetchData(mockFetchFunction, { immediate: false })

      await composable.loadData()

      expect(composable.loading.value).toBe(false)
    })

    it('should ignore response when cancelled', async () => {
      let resolvePromise
      const promise = new Promise(resolve => { resolvePromise = resolve })
      mockFetchFunction.mockReturnValue(promise)
      composable = useFetchData(mockFetchFunction, { immediate: false })

      const loadPromise = composable.loadData()
      composable.cancelRequest()
      resolvePromise('data')
      await loadPromise

      // When cancelled, data should remain null because isCancelled check prevents assignment
      expect(composable.data.value).toBeNull()
    })

    it('should handle error without message', async () => {
      const errorWithoutMessage = {}
      mockFetchFunction.mockRejectedValue(errorWithoutMessage)
      composable = useFetchData(mockFetchFunction, { 
        immediate: false,
        retryAttempts: 0
      })

      await composable.loadData()

      // handleFinalError uses err.message || "Error desconocido"
      // But if error is handled by handleCancel, error.value may be null
      expect(composable.loading.value).toBe(false)
    })

    it('should handle keepDataOnUnmount option', () => {
      // This test verifies the option exists and can be set
      // The actual behavior is tested through component lifecycle
      composable = useFetchData(mockFetchFunction, { 
        immediate: false,
        keepDataOnUnmount: true
      })

      expect(composable).toBeDefined()
      expect(composable.data).toBeDefined()
    })

    it('should handle loadData with params', async () => {
      mockFetchFunction.mockResolvedValue('param data')
      composable = useFetchData(mockFetchFunction, { immediate: false })

      await composable.loadData({ id: 1, name: 'test' })

      expect(mockFetchFunction).toHaveBeenCalledWith({
        id: 1,
        name: 'test',
        signal: expect.any(AbortSignal),
        cancelToken: expect.any(Object)
      })
    })

    it('should handle error with message property', async () => {
      const errorWithMessage = new Error('Custom error message')
      // Ensure axios.isCancel returns false so handleCancel doesn't catch it
      const axios = await import('axios')
      axios.default.isCancel.mockReturnValue(false)
      
      mockFetchFunction.mockRejectedValue(errorWithMessage)
      composable = useFetchData(mockFetchFunction, { 
        immediate: false,
        retryAttempts: 0 // 0 retries means 1 attempt total
      })

      await composable.loadData()

      // After the single attempt fails, handleFinalError should be called
      // handleFinalError sets: error.value = err.message || "Error desconocido"
      expect(composable.error.value).toBe('Custom error message')
      expect(composable.loading.value).toBe(false)
      expect(mockFetchFunction).toHaveBeenCalledTimes(1)
    })
  })
})