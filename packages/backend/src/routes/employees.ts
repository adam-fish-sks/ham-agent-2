import { Router } from 'express';
import { prisma } from '@ham-agent/database';
import { scrubEmployeeForCache, validateScrubbed, logger } from '@ham-agent/shared';
import { workwizeClient } from '../lib/workwize';

export const employeesRouter = Router();

// Get all employees from cache
employeesRouter.get('/', async (req, res) => {
  try {
    const employees = await prisma.employee.findMany({
      orderBy: { createdAt: 'desc' },
    });
    res.json(employees);
  } catch (error) {
    logger.error('Failed to fetch employees', error);
    res.status(500).json({ error: 'Failed to fetch employees' });
  }
});

// Get single employee from cache
employeesRouter.get('/:id', async (req, res) => {
  try {
    const employee = await prisma.employee.findUnique({
      where: { id: req.params.id },
      include: {
        office: true,
        assets: true,
      },
    });

    if (!employee) {
      return res.status(404).json({ error: 'Employee not found' });
    }

    res.json(employee);
  } catch (error) {
    logger.error('Failed to fetch employee', error);
    res.status(500).json({ error: 'Failed to fetch employee' });
  }
});

// Sync employees from Workwize API
employeesRouter.post('/sync', async (req, res) => {
  try {
    logger.info('Starting employee sync from Workwize');

    const response = await workwizeClient.getEmployees();
    const employees = response.data || [];

    let synced = 0;
    let failed = 0;

    for (const employee of employees) {
      try {
        // Scrub PII before caching
        const scrubbed = scrubEmployeeForCache(employee);

        // Validate scrubbing
        if (!validateScrubbed(scrubbed)) {
          logger.error('PII validation failed for employee', { id: employee.id });
          failed++;
          continue;
        }

        // Cache scrubbed data
        await prisma.employee.upsert({
          where: { id: scrubbed.id },
          create: scrubbed,
          update: scrubbed,
        });

        synced++;
      } catch (error) {
        logger.error('Failed to sync employee', { id: employee.id, error });
        failed++;
      }
    }

    logger.info('Employee sync complete', { synced, failed, total: employees.length });
    res.json({ synced, failed, total: employees.length });
  } catch (error) {
    logger.error('Employee sync failed', error);
    res.status(500).json({ error: 'Sync failed' });
  }
});
