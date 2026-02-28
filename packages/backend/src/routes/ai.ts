import { Router } from 'express';
import { prisma } from '@ham-agent/database';
import { logger } from '@ham-agent/shared';

export const aiRouter = Router();

// Get database schema information for AI context
async function getDatabaseContext(): Promise<string> {
  const [employeeCount, assetCount, productCount, orderCount, officeCount, warehouseCount] =
    await Promise.all([
      prisma.employee.count(),
      prisma.asset.count(),
      prisma.product.count(),
      prisma.order.count(),
      prisma.office.count(),
      prisma.warehouse.count(),
    ]);

  return `
Database Information:
- Employees: ${employeeCount} records (PII scrubbed: names and emails redacted)
- Assets: ${assetCount} records (PII scrubbed: assigned user names redacted, only IDs stored)
- Products: ${productCount} records
- Orders: ${orderCount} records
- Offices: ${officeCount} records
- Warehouses: ${warehouseCount} records

Available operations:
- Query employees by department, role, or status
- Query assets by category, status, or assigned employee ID
- Query products by category or manufacturer
- Query orders by status or date range
- All queries return cached data with PII already scrubbed
`.trim();
}

// Query database based on explicit parameters from AI tool call
export async function queryDatabase(params: {
  country?: string;
  deviceClass?: string;
  warehouseOnly?: boolean;
  availableOnly?: boolean;
  assignedOnly?: boolean;
  manufacturer?: string;
}): Promise<any> {
  try {
    const assets = await prisma.asset.findMany({
      include: {
        assignedTo: {
          include: { address: true },
        },
        warehouse: {
          include: { address: true },
        },
      },
    });

    const { classifyDevice, parseDeviceSpecs } = await import('@ham-agent/shared');

    let filtered = assets;

    if (params.country) {
      const countryToWarehouse: Record<string, string> = {
        'Canada': '8',
        'United States': '2',
        'United Kingdom': '1',
        'Netherlands': '4',
        'Australia': '9',
        'Singapore': '12',
        'Japan': '15',
        'United Arab Emirates': '16',
        'South Africa': '13',
        'India': '6',
        'Brazil': '7',
        'Mexico': '11',
        'Philippines': '10',
        'Costa Rica': '14',
      };
      const warehouseId = countryToWarehouse[params.country];
      
      if (params.warehouseOnly) {
        filtered = filtered.filter(a => warehouseId && a.warehouseId?.toString() === warehouseId);
      } else {
        filtered = filtered.filter(a => 
          a.assignedTo?.address?.country === params.country ||
          (warehouseId && a.warehouseId?.toString() === warehouseId)
        );
      }
    }

    if (params.availableOnly) {
      filtered = filtered.filter(a => a.status === 'available');
    }

    if (params.assignedOnly) {
      filtered = filtered.filter(a => a.assignedToId !== null);
    }

    if (params.manufacturer) {
      filtered = filtered.filter(a => a.name?.includes(params.manufacturer));
    }

    const results = filtered.map(asset => {
      const deviceClass = classifyDevice(asset.name || '');
      const specs = parseDeviceSpecs(asset.name || '');
      return {
        id: asset.id,
        serialCode: asset.serialCode,
        name: asset.name,
        status: asset.status,
        deviceClass,
        specs,
        country: asset.assignedTo?.address?.country,
        warehouseId: asset.warehouseId,
      };
    }).filter(r => !params.deviceClass || r.deviceClass === params.deviceClass);

    return {
      params: params,
      total: results.length,
      results: results.slice(0, 50),
    };
  } catch (error) {
    logger.error('Database query error', error);
    throw error;
  }
}

// Chat with AI assistant
aiRouter.post('/chat', async (req, res) => {
  try {
    const { message, history = [], customPrompt } = req.body;

    if (!message) {
      return res.status(400).json({ error: 'Message is required' });
    }

    // Get database context
    const dbContext = await getDatabaseContext();

    // Use custom prompt from frontend (required)
    if (!customPrompt) {
      return res.status(400).json({ error: 'System prompt is required. Please configure it in Settings.' });
    }

    // Build conversation context with custom prompt
    const systemMessage = {
      role: 'system',
      content: `${customPrompt}

${dbContext}`,
    };

    const messages = [systemMessage, ...history, { role: 'user', content: message }];

    // Get AI response with tool support - AI decides when and how to query
    const { chat } = await import('../lib/azure-openai');
    const { AI_TOOLS } = await import('../lib/ai-tools');
    
    const aiResponse = await chat(messages, {
      tools: AI_TOOLS,
      maxIterations: 5,
    });

    res.json({
      response: aiResponse,
    });
  } catch (error: any) {
    logger.error('AI chat error', error);
    res.status(500).json({ error: error.message || 'Failed to process chat request' });
  }
});

// Get database statistics for AI context
aiRouter.get('/stats', async (req, res) => {
  try {
    const context = await getDatabaseContext();
    res.json({ context });
  } catch (error) {
    logger.error('Failed to get stats', error);
    res.status(500).json({ error: 'Failed to get statistics' });
  }
});
