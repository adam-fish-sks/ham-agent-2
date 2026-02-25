import { Router } from 'express';
import { logger } from '@ham-agent/shared';
import axios from 'axios';

export const syncRouter = Router();

// Sync all data from Workwize
syncRouter.post('/all', async (req, res) => {
  try {
    logger.info('Starting full sync from Workwize');
    
    const results = {
      employees: { synced: 0, failed: 0 },
      assets: { synced: 0, failed: 0 },
      orders: { synced: 0, failed: 0 },
      products: { synced: 0, failed: 0 },
      offices: { synced: 0, failed: 0 },
      warehouses: { synced: 0, failed: 0 },
      offboards: { synced: 0, failed: 0 },
    };
    
    // Sync each entity type
    const entities = ['employees', 'assets', 'orders', 'products', 'offices', 'warehouses', 'offboards'];
    
    for (const entity of entities) {
      try {
        const response = await axios.post(`http://localhost:${process.env.PORT || 3001}/api/${entity}/sync`);
        results[entity] = response.data;
      } catch (error) {
        logger.error(`Failed to sync ${entity}`, error);
        results[entity].failed = -1;
      }
    }
    
    logger.info('Full sync complete', results);
    res.json(results);
  } catch (error) {
    logger.error('Full sync failed', error);
    res.status(500).json({ error: 'Full sync failed' });
  }
});
