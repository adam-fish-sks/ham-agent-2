/**
 * Simple logger utility
 */

type LogLevel = 'info' | 'warn' | 'error' | 'debug';

class Logger {
  private shouldLog(level: LogLevel): boolean {
    if (process.env.NODE_ENV === 'production' && level === 'debug') {
      return false;
    }
    return true;
  }

  info(message: string, meta?: any) {
    if (this.shouldLog('info')) {
      console.log(`[INFO] ${message}`, meta || '');
    }
  }

  warn(message: string, meta?: any) {
    if (this.shouldLog('warn')) {
      console.warn(`[WARN] ${message}`, meta || '');
    }
  }

  error(message: string, meta?: any) {
    if (this.shouldLog('error')) {
      console.error(`[ERROR] ${message}`, meta || '');
    }
  }

  debug(message: string, meta?: any) {
    if (this.shouldLog('debug')) {
      console.debug(`[DEBUG] ${message}`, meta || '');
    }
  }
}

export const logger = new Logger();
