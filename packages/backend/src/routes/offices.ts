import { Router } from 'express';
import { prisma } from '@ham-agent/database';
import { logger } from '@ham-agent/shared';
import { workwizeClient } from '../lib/workwize';

export const officesRouter = Router();

officesRouter.get('/', async (req, res) => {
  try {
    const offices = await prisma.office.findMany({
      include: { address: true },
      orderBy: { createdAt: 'desc' },
    });
    res.json(offices);
  } catch (error) {
    logger.error('Failed to fetch offices', error);
    res.status(500).json({ error: 'Failed to fetch offices' });
  }
});

officesRouter.post('/sync', async (req, res) => {
  try {
    const response = await workwizeClient.getOffices();
    const offices = response.data || [];

    let synced = 0;
    for (const office of offices) {
      await prisma.office.upsert({
        where: { id: office.id },
        create: {
          id: office.id,
          name: office.name,
          code: office.code,
          addressId: office.address_id,
          phone: office.phone,
          email: office.email,
          capacity: office.capacity,
          status: office.status,
        },
        update: {
          name: office.name,
          code: office.code,
          addressId: office.address_id,
          phone: office.phone,
          email: office.email,
          capacity: office.capacity,
          status: office.status,
        },
      });
      synced++;
    }

    res.json({ synced, total: offices.length });
  } catch (error) {
    logger.error('Office sync failed', error);
    res.status(500).json({ error: 'Sync failed' });
  }
});
