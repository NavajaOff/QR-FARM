import { fetchQrResource, transformEmbeddedPayload } from './qr'

describe('qr', () => {
  it('should export qr functions', () => {
    expect(fetchQrResource).toBeDefined()
    expect(typeof fetchQrResource).toBe('function')
    expect(transformEmbeddedPayload).toBeDefined()
    expect(typeof transformEmbeddedPayload).toBe('function')
  })
})