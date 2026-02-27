/**
 * Custom error classes for API
 */

import { ErrorCode, ErrorCodes, ErrorDetail } from './api-types';

export class ApiError extends Error {
  constructor(
    public statusCode: number,
    public code: ErrorCode,
    message: string,
    public details?: ErrorDetail[]
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

export class NotFoundError extends ApiError {
  constructor(resource: string, id?: string) {
    const message = id ? `${resource} with id ${id} not found` : `${resource} not found`;
    super(404, ErrorCodes.NOT_FOUND, message);
    this.name = 'NotFoundError';
  }
}

export class ValidationError extends ApiError {
  constructor(message: string, details?: ErrorDetail[]) {
    super(400, ErrorCodes.VALIDATION_ERROR, message, details);
    this.name = 'ValidationError';
  }
}

export class UnauthorizedError extends ApiError {
  constructor(message: string = 'Authentication required') {
    super(401, ErrorCodes.UNAUTHORIZED, message);
    this.name = 'UnauthorizedError';
  }
}

export class ForbiddenError extends ApiError {
  constructor(message: string = 'You do not have permission to perform this action') {
    super(403, ErrorCodes.FORBIDDEN, message);
    this.name = 'ForbiddenError';
  }
}

export class ConflictError extends ApiError {
  constructor(message: string) {
    super(409, ErrorCodes.CONFLICT, message);
    this.name = 'ConflictError';
  }
}

export class InternalError extends ApiError {
  constructor(message: string = 'Internal server error') {
    super(500, ErrorCodes.INTERNAL_ERROR, message);
    this.name = 'InternalError';
  }
}
