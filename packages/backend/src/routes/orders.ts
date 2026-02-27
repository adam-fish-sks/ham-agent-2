import { Router } from 'express';
import { prisma } from '@ham-agent/database';
import { scrubOrderForCache, validateScrubbed, logger } from '@ham-agent/shared';
import { workwizeClient } from '../lib/workwize';

export const ordersRouter = Router();

ordersRouter.get('/', async (req, res) => {
  try {
    const orders = await prisma.order.findMany({
      include: { employee: true, warehouse: true },
      orderBy: { createdAt: 'desc' },
    });
    res.json(orders);
  } catch (error) {
    logger.error('Failed to fetch orders', error);
    res.status(500).json({ error: 'Failed to fetch orders' });
  }
});

ordersRouter.post('/sync', async (req, res) => {
  try {
    const response = await workwizeClient.getOrders();
    const orders = response.data || [];

    let synced = 0;
    for (const order of orders) {
      const scrubbed = scrubOrderForCache(order);
      if (validateScrubbed(scrubbed)) {
        await prisma.order.upsert({
          where: { id: scrubbed.id },
          create: scrubbed,
          update: scrubbed,
        });
        synced++;
      }
    }

    res.json({ synced, total: orders.length });
  } catch (error) {
    logger.error('Order sync failed', error);
    res.status(500).json({ error: 'Sync failed' });
  }
});
