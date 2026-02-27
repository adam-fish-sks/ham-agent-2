import { describe, it, expect, vi } from 'vitest';
import { successResponse, createdResponse, noContentResponse } from './responses';
import { Response } from 'express';

describe('Response Utilities', () => {
  describe('successResponse', () => {
    it('returns 200 with data by default', () => {
      const res = {
        status: vi.fn().mockReturnThis(),
        json: vi.fn(),
      } as unknown as Response;

      const data = { id: '1', name: 'Test' };
      successResponse(res, data);

      expect(res.status).toHaveBeenCalledWith(200);
      expect(res.json).toHaveBeenCalledWith({ data });
    });

    it('accepts custom status code', () => {
      const res = {
        status: vi.fn().mockReturnThis(),
        json: vi.fn(),
      } as unknown as Response;

      successResponse(res, { test: true }, 201);

      expect(res.status).toHaveBeenCalledWith(201);
    });
  });

  describe('createdResponse', () => {
    it('returns 201 with data', () => {
      const res = {
        status: vi.fn().mockReturnThis(),
        json: vi.fn(),
      } as unknown as Response;

      const data = { id: '1' };
      createdResponse(res, data);

      expect(res.status).toHaveBeenCalledWith(201);
      expect(res.json).toHaveBeenCalledWith({ data });
    });
  });

  describe('noContentResponse', () => {
    it('returns 204 with no body', () => {
      const res = {
        status: vi.fn().mockReturnThis(),
        send: vi.fn(),
      } as unknown as Response;

      noContentResponse(res);

      expect(res.status).toHaveBeenCalledWith(204);
      expect(res.send).toHaveBeenCalled();
    });
  });
});
