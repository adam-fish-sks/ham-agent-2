import { Router } from 'express';
import { prisma } from '@ham-agent/database';
import { logger } from '@ham-agent/shared';
import { workwizeClient } from '../lib/workwize';

export const productsRouter = Router();

productsRouter.get('/', async (req, res) => {
  try {
    const products = await prisma.product.findMany({
      orderBy: { createdAt: 'desc' },
    });
    res.json(products);
  } catch (error) {
    logger.error('Failed to fetch products', error);
    res.status(500).json({ error: 'Failed to fetch products' });
  }
});

productsRouter.post('/sync', async (req, res) => {
  try {
    const response = await workwizeClient.getProducts();
    const products = response.data || [];

    let synced = 0;
    for (const product of products) {
      await prisma.product.upsert({
        where: { id: product.id },
        create: {
          id: product.id,
          name: product.name,
          sku: product.sku,
          category: product.category,
          description: product.description,
          manufacturer: product.manufacturer,
          model: product.model,
          price: product.price,
          currency: product.currency,
          status: product.status,
          stockQuantity: product.stock_quantity,
        },
        update: {
          name: product.name,
          sku: product.sku,
          category: product.category,
          description: product.description,
          manufacturer: product.manufacturer,
          model: product.model,
          price: product.price,
          currency: product.currency,
          status: product.status,
          stockQuantity: product.stock_quantity,
        },
      });
      synced++;
    }

    res.json({ synced, total: products.length });
  } catch (error) {
    logger.error('Product sync failed', error);
    res.status(500).json({ error: 'Sync failed' });
  }
});
