import { describe, it, expect } from 'vitest';

// Vitest sanity check — ensures jsdom + vitest pipeline boots cleanly.
// Replace with real component/render tests as the app grows.
describe('vitest setup', () => {
  it('exposes jsdom window + document', () => {
    expect(typeof window).toBe('object');
    expect(typeof document).toBe('object');
  });
});
