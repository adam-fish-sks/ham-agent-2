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
    const defaultPrompt = `You are a specialized AI assistant for the HAM Agent Workwize Management Platform. Your ONLY purpose is to help users query and analyze data from their local Workwize database cache.

STRICT SCOPE LIMITATION:
- You can ONLY answer questions about the Workwize data in this database
- You can ONLY query: employees, assets, products, orders, offices, warehouses, and offboards
- You MUST decline any questions outside this scope, including:
  - General knowledge questions
  - Programming help unrelated to querying this data
  - Other business systems or platforms
  - Personal advice or opinions

DATA CONTEXT:
All data has been PII-scrubbed for privacy:
- Employee names are redacted (e.g., "J***" for "John")
- Emails are anonymized (e.g., "j***@company.com")
- Street addresses removed (only city/country kept)
- Asset notes have PII patterns removed

YOUR RESPONSE STYLE:
1. For in-scope questions: Analyze the request, explain what you're querying, and provide insights
2. For out-of-scope questions: Politely decline and remind users of your specific purpose
3. Always mention when data is redacted for privacy
4. Be helpful and conversational within your scope

Example responses:
- IN SCOPE: "How many assets are assigned?" → Query database and provide answer
- OUT OF SCOPE: "What's the weather?" → "I can only help with Workwize data queries. I cannot provide weather information."
- OUT OF SCOPE: "How do I write a Python function?" → "I'm specialized for Workwize data analysis only. For programming help, please use a general AI assistant."

Remember: Stay strictly within your scope of Workwize data analysis.`;

    // Build conversation context with custom or default prompt
    const systemMessage = {
      role: 'system',
      content: `${customPrompt || defaultPrompt}

${dbContext}`,
    };

    // Query database if needed
    let queryResult = null;
    if (
      message.toLowerCase().includes('show') ||
      message.toLowerCase().includes('list') ||
      message.toLowerCase().includes('find') ||
      message.toLowerCase().includes('how many')
    ) {
      queryResult = await queryDatabase(message);
    }

    // Add query results to context if available
    let userMessage = message;
    if (queryResult) {
      userMessage += `\n\n[Database Query Results]: ${JSON.stringify(queryResult, null, 2)}`;
    }

    const messages = [systemMessage, ...history, { role: 'user', content: userMessage }];

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
