import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';
import dotenv from 'dotenv';
import path from 'path';
import { logger } from '@ham-agent/shared';
import { employeesRouter } from './routes/employees';
import { assetsRouter } from './routes/assets';
import { ordersRouter } from './routes/orders';
import { productsRouter } from './routes/products';
import { officesRouter } from './routes/offices';
import { warehousesRouter } from './routes/warehouses';
import { offboardsRouter } from './routes/offboards';
import { addressesRouter } from './routes/addresses';
import { syncRouter } from './routes/sync';
import { aiRouter } from './routes/ai';
import { statusRouter } from './routes/status';
import { errorHandler, notFoundHandler } from './middleware/errorHandler';
import { requestLogger } from './middleware/requestLogger';

// Load .env from project root
dotenv.config({ path: path.resolve(__dirname, '../../../.env') });

const app = express();
const PORT = process.env.PORT || 3001;

// Security middleware
app.use(helmet());

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // 100 requests per window
  message: { error: { code: 'RATE_LIMIT_EXCEEDED', message: 'Too many requests' } },
  standardHeaders: true,
  legacyHeaders: false,
});

app.use('/api/', limiter);

// CORS
app.use(
  cors({
    origin: process.env.ALLOWED_ORIGINS?.split(',') || '*',
    credentials: true,
  })
);

// Body parsing
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Request logging
app.use(requestLogger);

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// API Routes
app.use('/api/employees', employeesRouter);
app.use('/api/assets', assetsRouter);
app.use('/api/orders', ordersRouter);
app.use('/api/products', productsRouter);
app.use('/api/offices', officesRouter);
app.use('/api/warehouses', warehousesRouter);
app.use('/api/offboards', offboardsRouter);
app.use('/api/addresses', addressesRouter);
app.use('/api/sync', syncRouter);
app.use('/api/ai', aiRouter);
app.use('/api/status', statusRouter);

// 404 handler
app.use(notFoundHandler);

// Error handler (must be last)
app.use(errorHandler);

// Handle uncaught errors
process.on('uncaughtException', (error) => {
  logger.error('Uncaught Exception', { error: error.message, stack: error.stack });
  process.exit(1);
});

process.on('unhandledRejection', (reason) => {
  logger.error('Unhandled Rejection', { reason });
  process.exit(1);
});

const server = app.listen(PORT, () => {
  logger.info(`Backend server running on port ${PORT}`, { port: PORT, env: process.env.NODE_ENV });
});

server.on('error', (error) => {
  logger.error('Server error', { error });
  process.exit(1);
});

export { app };





