/**
 * Error handling middleware
 */

import { Request, Response, NextFunction } from 'express';
import { ApiError, ErrorCodes, ApiResponse } from '@ham-agent/shared';
import { logger } from '@ham-agent/shared';
import { ZodError } from 'zod';

export function errorHandler(err: Error, req: Request, res: Response, _next: NextFunction) {
  // Log error
  logger.error('Request error', {
    error: err.message,
    stack: err.stack,
    path: req.path,
    method: req.method,
  });

  // Handle Zod validation errors
  if (err instanceof ZodError) {
    const response: ApiResponse = {
      error: {
        code: ErrorCodes.VALIDATION_ERROR,
        message: 'Invalid input data',
        details: err.errors.map((e) => ({
          field: e.path.join('.'),
          message: e.message,
        })),
      },
    };
    return res.status(400).json(response);
  }

  // Handle custom API errors
  if (err instanceof ApiError) {
    const response: ApiResponse = {
      error: {
        code: err.code,
        message: err.message,
        details: err.details,
      },
    };
    return res.status(err.statusCode).json(response);
  }

  // Handle unknown errors
  const response: ApiResponse = {
    error: {
      code: ErrorCodes.INTERNAL_ERROR,
      message: process.env.NODE_ENV === 'production' ? 'Internal server error' : err.message,
    },
  };
  return res.status(500).json(response);
}

export function notFoundHandler(req: Request, res: Response) {
  const response: ApiResponse = {
    error: {
      code: ErrorCodes.NOT_FOUND,
      message: `Route ${req.method} ${req.path} not found`,
    },
  };
  res.status(404).json(response);
}
