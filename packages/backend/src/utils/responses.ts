/**
 * API response utilities
 */

import { Response } from 'express';
import { ApiResponse } from '@ham-agent/shared';

export function successResponse<T>(res: Response, data: T, statusCode: number = 200) {
  const response: ApiResponse<T> = { data };
  return res.status(statusCode).json(response);
}

export function createdResponse<T>(res: Response, data: T) {
  return successResponse(res, data, 201);
}

export function noContentResponse(res: Response) {
  return res.status(204).send();
}
