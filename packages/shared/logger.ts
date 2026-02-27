/**
 * Pino-based structured logger
 */

import pino from 'pino';

const isDevelopment = process.env.NODE_ENV !== 'production';

export const logger = pino({
  level: process.env.LOG_LEVEL || (isDevelopment ? 'debug' : 'info'),
  transport: isDevelopment
    ? {
        target: 'pino-pretty',
        options: {
          colorize: true,
          ignore: 'pid,hostname',
          translateTime: 'SYS:standard',
        },
      }
    : undefined,
  // Redact sensitive fields
  redact: {
    paths: ['password', 'apiKey', 'token', 'secret', 'authorization'],
    remove: true,
  },
});

// Export types for convenience
export type Logger = pino.Logger;
