import { Router } from 'express';
import axios from 'axios';
import https from 'https';
import { logger } from '@ham-agent/shared';
import { prisma } from '@ham-agent/database';

export const statusRouter = Router();

const WORKWIZE_API_BASE = 'https://prod-back.goworkwize.com/api/public';
const WORKWIZE_KEY = process.env.WORKWIZE_KEY;

// HTTPS agent that bypasses SSL certificate verification (for development)
const httpsAgent = new https.Agent({
  rejectUnauthorized: false,
});

interface EndpointStatus {
  name: string;
  endpoint: string;
  status: 'healthy' | 'degraded' | 'down';
  responseTime: number | null;
  error?: string;
  statusCode?: number;
}

interface StatusResponse {
  overall: 'healthy' | 'degraded' | 'down';
  lastChecked: string;
  endpoints: EndpointStatus[];
}

// Health check for a single endpoint
async function checkEndpoint(name: string, endpoint: string): Promise<EndpointStatus> {
  const startTime = Date.now();

  try {
    const response = await axios.get(`${WORKWIZE_API_BASE}${endpoint}`, {
      headers: {
        Authorization: `Bearer ${WORKWIZE_KEY}`,
        Accept: 'application/json',
      },
      timeout: 20000, // 20 second timeout
      httpsAgent, // Use HTTPS agent that bypasses SSL verification
    });

    const responseTime = Date.now() - startTime;

    // Determine status based on response time and status code
    let status: 'healthy' | 'degraded' | 'down' = 'healthy';
    if (responseTime > 15000) {
      status = 'degraded'; // Slow response (15-20s)
    }
    if (response.status >= 500) {
      status = 'down';
    }

    return {
      name,
      endpoint,
      status,
      responseTime,
      statusCode: response.status,
    };
  } catch (error: any) {
    const responseTime = Date.now() - startTime;

    return {
      name,
      endpoint,
      status: 'down',
      responseTime: error.code === 'ECONNABORTED' ? null : responseTime,
      error: error.response?.data?.message || error.message || 'Unknown error',
      statusCode: error.response?.status,
    };
  }
}

// Get status of all Workwize API endpoints
statusRouter.get('/workwize', async (req, res) => {
  try {
    logger.info('Checking Workwize API status', { hasKey: !!WORKWIZE_KEY });

    if (!WORKWIZE_KEY) {
      logger.warn('WORKWIZE_KEY not found in environment');
      return res.status(500).json({
        overall: 'down',
        lastChecked: new Date().toISOString(),
        endpoints: [],
        error: 'Workwize API key not configured. Please set WORKWIZE_KEY in .env file.',
      });
    }

    // Check all main endpoints in parallel
    const checks = await Promise.all([
      checkEndpoint('Employees API', '/employees'),
      checkEndpoint('Assets API', '/assets'),
      checkEndpoint('Orders API', '/orders'),
      checkEndpoint('Products API', '/products'),
      checkEndpoint('Offices API', '/offices'),
      checkEndpoint('Warehouses API', '/warehouses'),
      checkEndpoint('Offboards API', '/offboards'),
    ]);

    // Determine overall status
    const downCount = checks.filter((c) => c.status === 'down').length;
    const degradedCount = checks.filter((c) => c.status === 'degraded').length;

    let overall: 'healthy' | 'degraded' | 'down';
    if (downCount > 0) {
      overall = downCount >= checks.length / 2 ? 'down' : 'degraded';
    } else if (degradedCount > 0) {
      overall = 'degraded';
    } else {
      overall = 'healthy';
    }

    const response: StatusResponse = {
      overall,
      lastChecked: new Date().toISOString(),
      endpoints: checks,
    };

    res.json(response);
  } catch (error) {
    logger.error('Failed to check Workwize API status', error);
    res.status(500).json({ error: 'Failed to check API status' });
  }
});

// Get database connection status
statusRouter.get('/database', async (req, res) => {
  try {
    const startTime = Date.now();

    // Simple query to test connection
    await prisma.$queryRaw`SELECT 1`;

    const responseTime = Date.now() - startTime;

    res.json({
      status: 'healthy',
      responseTime,
      lastChecked: new Date().toISOString(),
    });
  } catch (error: any) {
    logger.error('Database health check failed', error);
    res.status(503).json({
      status: 'down',
      error: error.message,
      lastChecked: new Date().toISOString(),
    });
  }
});
