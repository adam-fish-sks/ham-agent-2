import { describe, it, expect } from 'vitest';
import request from 'supertest';
import { app } from '../index';

describe('Backend API', () => {
  describe('GET /health', () => {
    it('returns 200 and health status', async () => {
      const res = await request(app).get('/health').expect(200);

      expect(res.body).toMatchObject({
        status: 'ok',
        timestamp: expect.any(String),
      });
    });
  });

  describe('404 Handler', () => {
    it('returns 404 for unknown routes', async () => {
      const res = await request(app).get('/api/unknown-route').expect(404);

      expect(res.body).toMatchObject({
        error: {
          code: 'NOT_FOUND',
          message: expect.stringContaining('/api/unknown-route'),
        },
      });
    });
  });

  describe('CORS', () => {
    it('includes CORS headers', async () => {
      const res = await request(app).get('/health');

      expect(res.headers['access-control-allow-origin']).toBeDefined();
    });
  });

  describe('Security Headers', () => {
    it('includes helmet security headers', async () => {
      const res = await request(app).get('/health');

      expect(res.headers['x-content-type-options']).toBe('nosniff');
      expect(res.headers['x-frame-options']).toBeDefined();
    });
  });
});
