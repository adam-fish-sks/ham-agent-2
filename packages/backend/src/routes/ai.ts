import { Router } from 'express';
import { prisma } from '@ham-agent/database';
import { logger } from '@ham-agent/shared';

export const aiRouter = Router();

// Get database schema information for AI context
async function getDatabaseContext(): Promise<string> {
  const [
    employeeCount,
    assetCount,
    productCount,
    orderCount,
    officeCount,
    warehouseCount,
  ] = await Promise.all([
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

// Query database based on AI analysis
async function queryDatabase(query: string): Promise<any> {
  const lowerQuery = query.toLowerCase();

  try {
    // Asset queries
    if (lowerQuery.includes('asset')) {
      if (lowerQuery.includes('assigned')) {
        return await prisma.asset.findMany({
          where: { status: 'assigned' },
          include: { product: true, assignedTo: true },
          take: 10,
        });
      }
      return await prisma.asset.findMany({
        include: { product: true, assignedTo: true },
        take: 10,
      });
    }

    // Employee queries
    if (lowerQuery.includes('employee')) {
      return await prisma.employee.findMany({
        include: { office: true },
        take: 10,
      });
    }

    // Product queries
    if (lowerQuery.includes('product')) {
      return await prisma.product.findMany({ take: 10 });
    }

    // Order queries
    if (lowerQuery.includes('order')) {
      return await prisma.order.findMany({
        include: { employee: true, warehouse: true },
        take: 10,
      });
    }

    return { message: 'No specific query matched. Please be more specific.' };
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

    // Default system prompt
    const defaultPrompt = `You are a helpful AI assistant for the HAM Agent Workwize Management Platform. 
You have access to a database with cached data from Workwize API.

IMPORTANT: All data in the database has been PII-scrubbed:
- Employee names are redacted (e.g., "J***" for "John")
- Emails are anonymized (e.g., "j***@company.com")
- Street addresses are removed (only city/state kept)
- Asset notes have PII patterns removed

When users ask questions:
1. Analyze what data they need
2. Let them know you'll query the database
3. Provide insights based on the scrubbed data
4. Remind them that names/emails are redacted for privacy

Be helpful and conversational. If you need to query data, explain what you're looking for.`;

    // Build conversation context with custom or default prompt
    const systemMessage = {
      role: 'system',
      content: `${customPrompt || defaultPrompt}

${dbContext}`,
    };

    // Query database if needed
    let queryResult = null;
    if (message.toLowerCase().includes('show') || 
        message.toLowerCase().includes('list') || 
        message.toLowerCase().includes('find') ||
        message.toLowerCase().includes('how many')) {
      queryResult = await queryDatabase(message);
    }

    // Add query results to context if available
    let userMessage = message;
    if (queryResult) {
      userMessage += `\n\n[Database Query Results]: ${JSON.stringify(queryResult, null, 2)}`;
    }

    const messages = [
      systemMessage,
      ...history,
      { role: 'user', content: userMessage },
    ];

    // Get AI response - lazy load Azure OpenAI only when needed
    const { chat } = await import('../lib/azure-openai');
    const aiResponse = await chat(messages);

    res.json({
      response: aiResponse,
      queryResults: queryResult,
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
