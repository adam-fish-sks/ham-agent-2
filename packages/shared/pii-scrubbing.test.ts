import { describe, it, expect } from 'vitest';
import { scrubPII } from './pii-scrubbing';

describe('PII Scrubbing', () => {
  describe('scrubPII', () => {
    it('scrubs email addresses', () => {
      const result = scrubPII('john.doe@example.com', 'email');
      expect(result).toMatch(/^j\*{3,}@example\.com$/);
    });

    it('scrubs names', () => {
      const result = scrubPII('John', 'name');
      expect(result).toMatch(/^J\*+$/);
    });

    it('returns original value for non-PII fields', () => {
      const result = scrubPII('some value', 'id');
      expect(result).toBe('some value');
    });

    it('handles empty strings', () => {
      const result = scrubPII('', 'email');
      expect(result).toBe('');
    });

    it('handles null values', () => {
      const result = scrubPII(null, 'email');
      expect(result).toBeNull();
    });
  });
});
