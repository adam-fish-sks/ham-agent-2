import { Router } from 'express';
import { prisma } from '@ham-agent/database';
import { scrubAddressForCache, validateScrubbed, logger } from '@ham-agent/shared';

export const addressesRouter = Router();

addressesRouter.get('/', async (req, res) => {
  try {
    const addresses = await prisma.address.findMany({
      orderBy: { createdAt: 'desc' },
    });
    res.json(addresses);
  } catch (error) {
    logger.error('Failed to fetch addresses', error);
    res.status(500).json({ error: 'Failed to fetch addresses' });
  }
});
