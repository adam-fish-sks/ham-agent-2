import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import path from 'path';
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

// Load .env from project root
dotenv.config({ path: path.resolve(__dirname, '../../../.env') });

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());

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

// Error handler
app.use((err: any, req: express.Request, res: express.Response, next: express.NextFunction) => {
  console.error('Error:', err);
  res.status(500).json({ error: 'Internal server error' });
});

// Handle uncaught errors
process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
});

app.listen(PORT, () => {
  console.log(`Backend server running on port ${PORT}`);
}).on('error', (error) => {
  console.error('Server error:', error);
});
