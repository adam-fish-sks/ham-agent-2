import { describe, it, expect } from 'vitest';
import {
  ApiError,
  NotFoundError,
  ValidationError,
  UnauthorizedError,
  ForbiddenError,
  ConflictError,
  InternalError,
} from './errors';
import { ErrorCodes } from './api-types';

describe('Error Classes', () => {
  describe('ApiError', () => {
    it('creates an API error with correct properties', () => {
      const error = new ApiError(400, ErrorCodes.VALIDATION_ERROR, 'Invalid input');

      expect(error).toBeInstanceOf(Error);
      expect(error.statusCode).toBe(400);
      expect(error.code).toBe(ErrorCodes.VALIDATION_ERROR);
      expect(error.message).toBe('Invalid input');
      expect(error.name).toBe('ApiError');
    });

    it('includes details when provided', () => {
      const details = [{ field: 'email', message: 'Invalid email' }];
      const error = new ApiError(400, ErrorCodes.VALIDATION_ERROR, 'Invalid input', details);

      expect(error.details).toEqual(details);
    });
  });

  describe('NotFoundError', () => {
    it('creates a 404 error for a resource', () => {
      const error = new NotFoundError('User');

      expect(error.statusCode).toBe(404);
      expect(error.code).toBe(ErrorCodes.NOT_FOUND);
      expect(error.message).toBe('User not found');
    });

    it('includes ID in message when provided', () => {
      const error = new NotFoundError('User', '123');

      expect(error.message).toBe('User with id 123 not found');
    });
  });

  describe('ValidationError', () => {
    it('creates a 400 validation error', () => {
      const error = new ValidationError('Invalid input');

      expect(error.statusCode).toBe(400);
      expect(error.code).toBe(ErrorCodes.VALIDATION_ERROR);
      expect(error.message).toBe('Invalid input');
    });
  });

  describe('UnauthorizedError', () => {
    it('creates a 401 error with default message', () => {
      const error = new UnauthorizedError();

      expect(error.statusCode).toBe(401);
      expect(error.code).toBe(ErrorCodes.UNAUTHORIZED);
      expect(error.message).toBe('Authentication required');
    });

    it('accepts custom message', () => {
      const error = new UnauthorizedError('Token expired');

      expect(error.message).toBe('Token expired');
    });
  });

  describe('ForbiddenError', () => {
    it('creates a 403 error with default message', () => {
      const error = new ForbiddenError();

      expect(error.statusCode).toBe(403);
      expect(error.code).toBe(ErrorCodes.FORBIDDEN);
    });
  });

  describe('ConflictError', () => {
    it('creates a 409 conflict error', () => {
      const error = new ConflictError('Resource already exists');

      expect(error.statusCode).toBe(409);
      expect(error.code).toBe(ErrorCodes.CONFLICT);
      expect(error.message).toBe('Resource already exists');
    });
  });

  describe('InternalError', () => {
    it('creates a 500 error with default message', () => {
      const error = new InternalError();

      expect(error.statusCode).toBe(500);
      expect(error.code).toBe(ErrorCodes.INTERNAL_ERROR);
      expect(error.message).toBe('Internal server error');
    });
  });
});
