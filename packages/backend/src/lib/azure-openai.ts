// Lazy-loaded Azure OpenAI to avoid startup crashes
export async function chat(
  messages: Array<{ role: string; content: string }>,
  options?: { tools?: any[]; maxIterations?: number }
) {
  const { OpenAIClient, AzureKeyCredential } = await import('@azure/openai');

  const endpoint = process.env.AZURE_OPENAI_ENDPOINT!;
  const apiKey = process.env.AZURE_OPENAI_API_KEY!;
  const deployment = process.env.AZURE_OPENAI_DEPLOYMENT || 'gpt-4';

  // Disable SSL verification for development
  process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';

  const client = new OpenAIClient(endpoint, new AzureKeyCredential(apiKey));

  try {
    const requestOptions: any = {};
    if (options?.tools && options.tools.length > 0) {
      requestOptions.tools = options.tools;
      requestOptions.tool_choice = 'auto'; // Let AI decide when to use tools
    }

    let currentMessages = [...messages];
    const maxIterations = options?.maxIterations || 5;
    let iteration = 0;

    // Agentic loop - allow AI to make multiple tool calls
    while (iteration < maxIterations) {
      const response = await client.getChatCompletions(deployment, currentMessages, requestOptions);
      const choice = response.choices[0];

      // If no tool calls, we're done
      if (!choice.message.toolCalls || choice.message.toolCalls.length === 0) {
        return choice.message.content || 'No response generated';
      }

      // AI wants to use tools - execute them
      currentMessages.push({
        role: 'assistant',
        content: choice.message.content || '',
      } as any);

      // Execute each tool call
      for (const toolCall of choice.message.toolCalls) {
        const { executeReadFile, executeSearchCode, executeAnalyzeFilterLogic, executeQueryDatabase } = await import('./ai-tools');
        const functionName = toolCall.function.name;
        const args = JSON.parse(toolCall.function.arguments);

        let result: string;
        try {
          switch (functionName) {
            case 'read_file':
              result = await executeReadFile(args);
              break;
            case 'search_code':
              result = await executeSearchCode(args);
              break;
            case 'analyze_filter_logic':
              result = await executeAnalyzeFilterLogic(args);
              break;
            case 'query_database': {
              const queryResult = await executeQueryDatabase(args);
              result = JSON.stringify(queryResult, null, 2);
              break;
            }
            default:
              result = `Unknown function: ${functionName}`;
          }
        } catch (error: any) {
          result = `Error executing ${functionName}: ${error.message}`;
        }

        // Add tool result as user message (Azure OpenAI doesn't support tool role properly)
        currentMessages.push({
          role: 'user',
          content: `[Tool: ${functionName}]\n${result}`,
        } as any);
      }

      iteration++;
    }

    // Max iterations reached
    return 'I needed more iterations to complete this task. Please try breaking it into smaller questions.';
  } catch (error) {
    console.error('Azure OpenAI error:', error);
    throw error;
  }
}
