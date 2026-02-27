import { Router } from 'express';
import { prisma } from '@ham-agent/database';
import { logger } from '@ham-agent/shared';
import { workwizeClient } from '../lib/workwize';

export const warehousesRouter = Router();

warehousesRouter.get('/', async (req, res) => {
  try {
    const warehouses = await prisma.warehouse.findMany({
      include: { address: true },
      orderBy: { createdAt: 'desc' },
    });
    res.json(warehouses);
  } catch (error) {
    logger.error('Failed to fetch warehouses', error);
    res.status(500).json({ error: 'Failed to fetch warehouses' });
  }
});

warehousesRouter.post('/sync', async (req, res) => {
  try {
    const response = await workwizeClient.getWarehouses();
    const warehouses = response.data || [];

    let synced = 0;
    for (const warehouse of warehouses) {
      await prisma.warehouse.upsert({
        where: { id: warehouse.id },
        create: {
          id: warehouse.id,
          name: warehouse.name,
          code: warehouse.code,
          addressId: warehouse.address_id,
          capacity: warehouse.capacity,
          status: warehouse.status,
          type: warehouse.type,
        },
        update: {
          name: warehouse.name,
          code: warehouse.code,
          addressId: warehouse.address_id,
          capacity: warehouse.capacity,
          status: warehouse.status,
          type: warehouse.type,
        },
      });
      synced++;
    }

    res.json({ synced, total: warehouses.length });
  } catch (error) {
    logger.error('Warehouse sync failed', error);
    res.status(500).json({ error: 'Sync failed' });
  }
});
