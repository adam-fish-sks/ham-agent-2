import { Router } from 'express';
import { prisma } from '@ham-agent/database';
import { scrubAssetForCache, validateScrubbed, logger } from '@ham-agent/shared';
import { workwizeClient } from '../lib/workwize';

export const assetsRouter = Router();

// Get all assets from cache
assetsRouter.get('/', async (req, res) => {
  try {
    const assets = await prisma.asset.findMany({
      include: {
        product: true,
        assignedTo: {
          include: {
            address: true,
          },
        },
        office: {
          include: {
            address: true,
          },
        },
        warehouse: {
          include: {
            address: true,
          },
        },
      },
      orderBy: { createdAt: 'desc' },
    });
    res.json(assets);
  } catch (error) {
    logger.error('Failed to fetch assets', error);
    res.status(500).json({ error: 'Failed to fetch assets' });
  }
});

// Get single asset from cache
assetsRouter.get('/:id', async (req, res) => {
  try {
    const asset = await prisma.asset.findUnique({
      where: { id: req.params.id },
      include: {
        product: true,
        assignedTo: {
          include: {
            address: true,
          },
        },
        office: {
          include: {
            address: true,
          },
        },
        warehouse: {
          include: {
            address: true,
          },
        },
      },
    });

    if (!asset) {
      return res.status(404).json({ error: 'Asset not found' });
    }

    res.json(asset);
  } catch (error) {
    logger.error('Failed to fetch asset', error);
    res.status(500).json({ error: 'Failed to fetch asset' });
  }
});

// Sync assets from Workwize API
assetsRouter.post('/sync', async (req, res) => {
  try {
    logger.info('Starting asset sync from Workwize');

    const response = await workwizeClient.getAssets();
    const assets = response.data || [];

    let synced = 0;
    let failed = 0;

    for (const asset of assets) {
      try {
        // Scrub PII before caching
        const scrubbed = scrubAssetForCache(asset);

        // Validate scrubbing
        if (!validateScrubbed(scrubbed)) {
          logger.error('PII validation failed for asset', { id: asset.id });
          failed++;
          continue;
        }

        // Cache scrubbed data
        await prisma.asset.upsert({
          where: { id: scrubbed.id },
          create: scrubbed,
          update: scrubbed,
        });

        synced++;
      } catch (error) {
        logger.error('Failed to sync asset', { id: asset.id, error });
        failed++;
      }
    }

    logger.info('Asset sync complete', { synced, failed, total: assets.length });
    res.json({ synced, failed, total: assets.length });
  } catch (error) {
    logger.error('Asset sync failed', error);
    res.status(500).json({ error: 'Sync failed' });
  }
});
