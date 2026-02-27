import { Router } from 'express';
import { prisma } from '@ham-agent/database';
import { logger } from '@ham-agent/shared';
import { workwizeClient } from '../lib/workwize';

export const offboardsRouter = Router();

offboardsRouter.get('/', async (req, res) => {
  try {
    const offboards = await prisma.offboard.findMany({
      include: { employee: true },
      orderBy: { createdAt: 'desc' },
    });
    res.json(offboards);
  } catch (error) {
    logger.error('Failed to fetch offboards', error);
    res.status(500).json({ error: 'Failed to fetch offboards' });
  }
});

offboardsRouter.post('/sync', async (req, res) => {
  try {
    const response = await workwizeClient.getOffboards();
    const offboards = response.data || [];

    let synced = 0;
    for (const offboard of offboards) {
      await prisma.offboard.upsert({
        where: { id: offboard.id },
        create: {
          id: offboard.id,
          employeeId: offboard.employee_id,
          offboardDate: offboard.offboard_date,
          reason: offboard.reason,
          status: offboard.status,
          returnedAssets: offboard.returned_assets || false,
          notes: offboard.notes,
          processedBy: offboard.processed_by,
        },
        update: {
          employeeId: offboard.employee_id,
          offboardDate: offboard.offboard_date,
          reason: offboard.reason,
          status: offboard.status,
          returnedAssets: offboard.returned_assets || false,
          notes: offboard.notes,
          processedBy: offboard.processed_by,
        },
      });
      synced++;
    }

    res.json({ synced, total: offboards.length });
  } catch (error) {
    logger.error('Offboard sync failed', error);
    res.status(500).json({ error: 'Sync failed' });
  }
});
