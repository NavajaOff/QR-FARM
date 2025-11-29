// Simple utility function for testing
export function add(a, b) {
  return a + b
}

describe('Utils', () => {
  it('should add two numbers', () => {
    expect(add(1, 2)).toBe(3)
  })
})