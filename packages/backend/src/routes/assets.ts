import { Router } from 'express';
import { prisma } from '@ham-agent/database';
import { scrubAssetForCache, validateScrubbed, logger, classifyDevice, parseDeviceSpecs } from '@ham-agent/shared';
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

// Search/query assets with intelligent filtering
assetsRouter.post('/search', async (req, res) => {
  try {
    const {
      country,
      deviceClass,
      status,
      warehouseId,
      warehouseCode,
      category,
      manufacturer,
      minRam,
      assignedOnly,
      availableOnly,
    } = req.body;

    logger.info('Asset search request', { filters: req.body });

    // Fetch all assets with relationships
    const assets = await prisma.asset.findMany({
      include: {
        assignedTo: {
          include: {
            address: true,
          },
        },
        warehouse: {
          include: {
            address: true,
          },
        },
        office: {
          include: {
            address: true,
          },
        },
      },
    });

    // Filter assets based on criteria
    let filtered = assets;

    // Filter by country (from assigned employee address OR warehouse location)
    if (country) {
      // Map country to warehouse code
      const countryToWarehouse: Record<string, string> = {
        'Canada': 'YYZ',
        'United States': 'ER3',
        'United Kingdom': 'LDW',
        'Netherlands': 'VEW',
        'Australia': 'SYD',
        'Singapore': 'SIW',
        'Japan': 'TYO',
        'United Arab Emirates': 'DXB',
        'South Africa': 'SOA',
        'India': 'LPB',
        'Brazil': 'LBZ',
        'Mexico': 'MXW',
        'Philippines': 'LPP',
        'Costa Rica': 'CSW',
      };

      const warehouseCodeForCountry = countryToWarehouse[country];
      
      // Look up warehouse ID for the country
      let warehouseIdForCountry: string | undefined;
      if (warehouseCodeForCountry) {
        const warehouse = await prisma.warehouse.findFirst({
          where: { code: warehouseCodeForCountry },
        });
        warehouseIdForCountry = warehouse?.id;
      }

      filtered = filtered.filter((asset) => {
        // Match if assigned to someone in that country
        const assignedToCountry = asset.assignedTo?.address?.country === country;
        // OR if located in warehouse for that country
        const inCountryWarehouse = warehouseIdForCountry && asset.warehouseId === warehouseIdForCountry;
        return assignedToCountry || inCountryWarehouse;
      });
    }

    // Filter by warehouse ID or code
    if (warehouseId) {
      filtered = filtered.filter((asset) => asset.warehouseId === warehouseId);
    }

    if (warehouseCode) {
      // Look up warehouse by code
      const warehouse = await prisma.warehouse.findFirst({
        where: { code: warehouseCode },
      });
      if (warehouse) {
        filtered = filtered.filter((asset) => asset.warehouseId === warehouse.id);
      }
    }

    // Filter by status
    if (status) {
      const statuses = Array.isArray(status) ? status : [status];
      filtered = filtered.filter((asset) => statuses.includes(asset.status));
    }

    // Filter by category
    if (category) {
      filtered = filtered.filter((asset) => asset.category === category);
    }

    // Filter by manufacturer (parse from name)
    if (manufacturer) {
      filtered = filtered.filter((asset) =>
        asset.name?.toLowerCase().includes(manufacturer.toLowerCase())
      );
    }

    // Filter by minimum RAM
    if (minRam) {
      filtered = filtered.filter((asset) => {
        const specs = parseDeviceSpecs(asset.name || '');
        return specs.ramGb && specs.ramGb >= minRam;
      });
    }

    // Convenience filters
    if (assignedOnly) {
      filtered = filtered.filter((asset) => asset.assignedToId !== null);
    }

    if (availableOnly) {
      filtered = filtered.filter((asset) => asset.status === 'available');
    }

    // Classify devices and filter by device class if specified
    const results = filtered
      .map((asset) => {
        const deviceClassification = classifyDevice(asset.name || '');
        const specs = parseDeviceSpecs(asset.name || '');

        return {
          id: asset.id,
          serialCode: asset.serialCode,
          assetTag: asset.assetTag,
          name: asset.name,
          category: asset.category,
          status: asset.status,
          deviceClass: deviceClassification,
          specs: {
            manufacturer: specs.manufacturer,
            model: specs.model,
            ram: specs.ram,
            ramGb: specs.ramGb,
            cpu: specs.cpu,
            isHighEnd: specs.isHighEnd,
          },
          location: {
            country: asset.assignedTo?.address?.country,
            city: asset.assignedTo?.address?.city,
            region: asset.assignedTo?.address?.region,
          },
          assignedTo: asset.assignedToId
            ? {
                id: asset.assignedTo?.id,
                name: `${asset.assignedTo?.firstName} ${asset.assignedTo?.lastName}`,
                email: asset.assignedTo?.email,
              }
            : null,
          warehouse: asset.warehouse
            ? {
                id: asset.warehouse.id,
                code: asset.warehouse.code,
                name: asset.warehouse.name,
              }
            : null,
        };
      })
      .filter((result) => !deviceClass || result.deviceClass === deviceClass);

    // Return results with metadata
    res.json({
      total: results.length,
      filters: req.body,
      results,
    });
  } catch (error) {
    logger.error('Asset search failed', error);
    res.status(500).json({ error: 'Search failed' });
  }
});

