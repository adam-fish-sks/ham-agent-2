import { Router } from 'express';
import { logger } from '@ham-agent/shared';
import { spawn } from 'child_process';
import path from 'path';

export const syncRouter = Router();

// Execute Python population script
async function runPythonScript(scriptName: string): Promise<{ success: boolean; output: string; error?: string }> {
  return new Promise((resolve) => {
    const scriptPath = path.join(process.cwd(), '..', '..', 'db-build-scripts', scriptName);
    
    logger.info(`Running Python script: ${scriptName}`);
    
    const python = spawn('python', [scriptPath]);
    let output = '';
    let errorOutput = '';
    
    python.stdout.on('data', (data) => {
      const text = data.toString();
      output += text;
      logger.info(`[${scriptName}] ${text.trim()}`);
    });
    
    python.stderr.on('data', (data) => {
      const text = data.toString();
      errorOutput += text;
      logger.error(`[${scriptName}] ${text.trim()}`);
    });
    
    python.on('close', (code) => {
      if (code === 0) {
        resolve({ success: true, output });
      } else {
        resolve({ success: false, output, error: errorOutput || `Script exited with code ${code}` });
      }
    });
    
    python.on('error', (err) => {
      resolve({ success: false, output, error: err.message });
    });
  });
}

// Parse counts from Python script output
function parseScriptOutput(output: string): { synced?: number; total?: number; message: string } {
  const lines = output.split('\n');
  let synced = 0;
  let total = 0;
  
  // Look for success messages with counts
  for (const line of lines) {
    // Match patterns like "✅ Created 1536 employee addresses"
    const createdMatch = line.match(/Created (\d+)/i);
    if (createdMatch) {
      synced += parseInt(createdMatch[1]);
    }
    
    // Match patterns like "Fetched 1632 total employees"
    const fetchedMatch = line.match(/Fetched (\d+) total/i);
    if (fetchedMatch) {
      total = parseInt(fetchedMatch[1]);
    }
    
    // Match patterns like "Processed 1699 assets"
    const processedMatch = line.match(/Processed (\d+)/i);
    if (processedMatch) {
      synced = parseInt(processedMatch[1]);
    }
  }
  
  return { synced, total, message: output };
}

// Sync all data from Workwize using Python population scripts
syncRouter.post('/all', async (req, res) => {
  try {
    logger.info('Starting full data population from Workwize using Python scripts');
    
    const results: any = {
      employees: { status: 'pending' },
      assets: { status: 'pending' },
      orders: { status: 'pending' },
      products: { status: 'pending' },
      offices: { status: 'pending' },
      warehouses: { status: 'pending' },
      offboards: { status: 'pending' },
    };
    
    // Run population scripts in sequence (some depend on others)
    const scripts = [
      { name: 'populate_employees.py', key: 'employees' },
      { name: 'populate_assets.py', key: 'assets' },
      { name: 'populate_orders.py', key: 'orders' },
      { name: 'populate_products.py', key: 'products' },
      { name: 'populate_offices.py', key: 'offices' },
      { name: 'populate_warehouses.py', key: 'warehouses' },
      { name: 'populate_offboards.py', key: 'offboards' },
    ];
    
    for (const script of scripts) {
      const result = await runPythonScript(script.name);
      
      if (result.success) {
        const parsed = parseScriptOutput(result.output);
        results[script.key] = {
          status: 'success',
          synced: parsed.synced || 0,
          total: parsed.total || parsed.synced || 0,
          message: 'Population completed successfully',
        };
      } else {
        results[script.key] = {
          status: 'error',
          synced: 0,
          total: 0,
          error: result.error || 'Script failed',
        };
        logger.error(`Failed to run ${script.name}`, result.error);
      }
    }
    
    logger.info('Full data population complete', results);
    res.json(results);
  } catch (error) {
    logger.error('Full data population failed', error);
    res.status(500).json({ error: 'Data population failed' });
  }
});
