// AI Assistant Tools - Give the AI capabilities like file reading, code search, etc.

export const AI_TOOLS = [
  {
    type: 'function',
    function: {
      name: 'read_file',
      description: 'Read the contents of a code file to understand implementation details',
      parameters: {
        type: 'object',
        properties: {
          filePath: {
            type: 'string',
            description: 'Relative path to the file from project root (e.g., "packages/backend/src/routes/ai.ts")',
          },
          startLine: {
            type: 'number',
            description: 'Starting line number (optional)',
          },
          endLine: {
            type: 'number',
            description: 'Ending line number (optional)',
          },
        },
        required: ['filePath'],
      },
    },
  },
  {
    type: 'function',
    function: {
      name: 'search_code',
      description: 'Search for specific text patterns in the codebase',
      parameters: {
        type: 'object',
        properties: {
          query: {
            type: 'string',
            description: 'Text or regex pattern to search for',
          },
          filePattern: {
            type: 'string',
            description: 'Glob pattern to limit search (e.g., "*.ts", "packages/backend/**")',
          },
        },
        required: ['query'],
      },
    },
  },
  {
    type: 'function',
    function: {
      name: 'query_database',
      description: 'Execute a database query with intelligent filters. Use your AI reasoning to determine the correct parameters based on the user query.',
      parameters: {
        type: 'object',
        properties: {
          country: {
            type: 'string',
            description: 'Filter by country name (exact: Canada, United States, United Kingdom, Australia, India, Brazil, Mexico, Singapore, Japan, South Africa, Netherlands, United Arab Emirates, Philippines, Costa Rica)',
          },
          deviceClass: {
            type: 'string',
            enum: ['Enhanced Windows', 'Standard Windows', 'Enhanced Mac', 'Standard Mac'],
            description: 'Device classification based on specs',
          },
          warehouseOnly: {
            type: 'boolean',
            description: 'Set to true when user asks about devices "in warehouse" or "in [country] warehouse" - filters for devices physically in warehouses, not deployed',
          },
          availableOnly: {
            type: 'boolean',
            description: 'Only show devices with status=available',
          },
          assignedOnly: {
            type: 'boolean',
            description: 'Only show devices that are assigned/deployed to employees',
          },
          manufacturer: {
            type: 'string',
            description: 'Filter by manufacturer (Dell, Apple, etc.)',
          },
        },
      },
    },
  },
  {
    type: 'function',
    function: {
      name: 'analyze_filter_logic',
      description: 'Inspect the filter detection logic to understand why a query returned unexpected results',
      parameters: {
        type: 'object',
        properties: {
          queryText: {
            type: 'string',
            description: 'The original user query to analyze',
          },
        },
        required: ['queryText'],
      },
    },
  },
];

// Tool execution handlers
export async function executeReadFile(args: { filePath: string; startLine?: number; endLine?: number }) {
  const fs = await import('fs/promises');
  const path = await import('path');
  
  const fullPath = path.join(process.cwd(), '../..', args.filePath);
  const content = await fs.readFile(fullPath, 'utf-8');
  const lines = content.split('\n');
  
  if (args.startLine && args.endLine) {
    return lines.slice(args.startLine - 1, args.endLine).join('\n');
  }
  
  return content;
}

export async function executeSearchCode(args: { query: string; filePattern?: string }) {
  // This would use ripgrep or similar - simplified for now
  const { execSync } = await import('child_process');
  
  try {
    const pattern = args.filePattern ? `-g "${args.filePattern}"` : '';
    const result = execSync(`rg -n -i "${args.query}" ${pattern}`, {
      cwd: process.cwd() + '/../..',
      encoding: 'utf-8',
      maxBuffer: 10 * 1024 * 1024,
    });
    return result;
  } catch (error: any) {
    // rg returns exit code 1 when no matches found
    return error.stdout || 'No matches found';
  }
}

export async function executeQueryDatabase(args: {
  country?: string;
  deviceClass?: string;
  warehouseOnly?: boolean;
  availableOnly?: boolean;
  assignedOnly?: boolean;
  manufacturer?: string;
}) {
  // Import the queryDatabase function from ai routes
  const { queryDatabase } = await import('../routes/ai');
  return await queryDatabase(args);
}

export async function executeAnalyzeFilterLogic(args: { queryText: string }) {
  // Read the filter detection code
  const filterCode = await executeReadFile({
    filePath: 'packages/backend/src/routes/ai.ts',
    startLine: 40,
    endLine: 80,
  });
  
  return `Filter Detection Logic:\n${filterCode}\n\nOriginal Query: "${args.queryText}"\nLowercase: "${args.queryText.toLowerCase()}"`;
}
